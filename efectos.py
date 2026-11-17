"""
CENTS - Efectos interactivos (hover, foco y pulsacion)

Da vida a la interfaz sin tocar la logica de cada pantalla:

- Botones: un velo de color y un contorno suave aparecen con animacion al pasar el
  mouse y se intensifican al pulsar. Se instalan solos en TODOS los Button de la app
  (ver instalar_efectos) y, a mano, en los widgets con ButtonBehavior (aplicar_efecto_boton).
- Cursor del sistema: manita sobre botones, "I" sobre campos de texto.
- Un unico gestor de hover (una sola suscripcion a Window.mouse_pos) que guarda
  referencias debiles, para no retener widgets que ya se destruyeron.

Atributos opcionales que un widget puede definir para afinar su efecto:
    efecto_radio            radio de las esquinas del velo/contorno (por defecto 8)
    efecto_sobre_primario   True (o funcion que devuelva bool) si el boton esta relleno
                            de color primario: usa un velo blanco en vez de azul.
"""
import functools
from weakref import WeakSet

from kivy.animation import Animation
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.logger import Logger
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.modalview import ModalView
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from tema import tema


# ---------------------------------------------------------------------------
#  Gestor de hover
# ---------------------------------------------------------------------------
class _ObjetivoHover:
    """Registro ligero de un widget sensible al mouse (el widget debe conservarlo)."""

    def __init__(self, widget, al_cambiar, cursor):
        self.widget = widget
        self.al_cambiar = al_cambiar
        self.cursor = cursor
        self.dentro = False


def _ancestros(widget):
    """
    Recorre los padres de un widget hacia arriba. Se detiene al llegar a la Window:
    en Kivy Window.parent es la propia Window, asi que un "while padre is not None"
    nunca termina (la app se queda congelada al 100% de CPU).
    """
    padre = widget.parent
    for _ in range(200):  # tope de seguridad
        if not isinstance(padre, Widget):
            return
        yield padre
        padre = padre.parent


def _dentro_de_modal(widget):
    return any(isinstance(p, (ModalView, DropDown)) for p in _ancestros(widget))


class GestorHover:
    def __init__(self):
        self._objetivos = WeakSet()
        self._cursor = "arrow"
        self._enlazado = False

    def registrar(self, widget, al_cambiar, cursor="hand"):
        """Registra un widget. Devuelve un objeto que el widget debe guardar."""
        if not self._enlazado:
            Window.bind(mouse_pos=self._al_mover_mouse)
            self._enlazado = True
        objetivo = _ObjetivoHover(widget, al_cambiar, cursor)
        self._objetivos.add(objetivo)
        return objetivo

    @staticmethod
    def _bajo_cursor(w, pos, hay_modal):
        if w.get_root_window() is None or w.disabled or w.opacity == 0:
            return False
        if hay_modal and not _dentro_de_modal(w):
            return False  # hay una ventana modal abierta: lo de atras no reacciona
        for padre in _ancestros(w):  # no reaccionar a la parte recortada por un ScrollView
            if isinstance(padre, ScrollView) and not padre.collide_point(*padre.to_widget(*pos)):
                return False
        return w.collide_point(*w.to_widget(*pos))

    def _al_mover_mouse(self, _ventana, pos):
        hay_modal = any(isinstance(h, (ModalView, DropDown)) for h in Window.children)
        cursor = "arrow"
        for objetivo in list(self._objetivos):
            try:
                dentro = self._bajo_cursor(objetivo.widget, pos, hay_modal)
                if dentro != objetivo.dentro:
                    objetivo.dentro = dentro
                    objetivo.al_cambiar(dentro)
                if dentro:
                    if objetivo.cursor == "ibeam":
                        cursor = "ibeam"
                    elif cursor == "arrow":
                        cursor = objetivo.cursor
            except Exception as e:  # un widget con problemas no debe romper el mouse
                Logger.warning(f"CENTS: efecto hover omitido ({e})")
        if cursor != self._cursor:
            self._cursor = cursor
            try:
                Window.set_system_cursor(cursor)
            except Exception:
                pass  # proveedores de ventana sin cursores de sistema


gestor_hover = GestorHover()


# ---------------------------------------------------------------------------
#  Efecto de boton
# ---------------------------------------------------------------------------
class EfectoBoton:
    """Velo + contorno animados dibujados encima del boton (canvas.after)."""

    def __init__(self, widget):
        self.widget = widget
        self._hover = False
        self._nivel = "reposo"
        with widget.canvas.after:
            self._c_velo = Color(1, 1, 1, 0)
            self._r_velo = RoundedRectangle(pos=widget.pos, size=widget.size, radius=[8])
            self._c_borde = Color(1, 1, 1, 0)
            self._l_borde = Line(rounded_rectangle=(widget.x, widget.y, widget.width, widget.height, 8), width=1.2)
        widget.bind(pos=self._geometria, size=self._geometria, disabled=self._actualizar)
        if hasattr(widget, "state"):
            widget.bind(state=self._actualizar)
        self._objetivo = gestor_hover.registrar(widget, self._al_hover, "hand")

    # -- geometria ---------------------------------------------------------
    def _radio(self):
        w = self.widget
        r = getattr(w, "efecto_radio", None)
        if r is None:
            lista = getattr(w, "radio", None)
            r = lista[0] if isinstance(lista, (list, tuple)) and lista else 8
        return min(r, w.height / 2) if w.height > 0 else r

    def _geometria(self, *args):
        w = self.widget
        r = self._radio()
        self._r_velo.pos = w.pos
        self._r_velo.size = w.size
        self._r_velo.radius = [r]
        self._l_borde.rounded_rectangle = (w.x, w.y, w.width, w.height, r)

    # -- estado ------------------------------------------------------------
    def _sobre_primario(self):
        valor = getattr(self.widget, "efecto_sobre_primario", False)
        return bool(valor() if callable(valor) else valor)

    def _al_hover(self, dentro):
        self._hover = dentro
        self._actualizar()

    def _actualizar(self, *args):
        w = self.widget
        if w.disabled:
            nivel = "reposo"
        elif getattr(w, "state", "normal") == "down":
            nivel = "press"
        elif self._hover:
            nivel = "hover"
        else:
            nivel = "reposo"
        if nivel == self._nivel:
            return
        self._nivel = nivel

        if self._sobre_primario():
            color_velo = (1, 1, 1)
            alfas = {"reposo": (0, 0), "hover": (0.16, 0), "press": (0.28, 0)}
        elif tema.modo == "oscuro":
            color_velo = tuple(tema.primario[:3])
            alfas = {"reposo": (0, 0), "hover": (0.12, 0.55), "press": (0.22, 0.9)}
        else:
            color_velo = tuple(tema.primario[:3])
            alfas = {"reposo": (0, 0), "hover": (0.07, 0.55), "press": (0.15, 0.9)}

        alfa_velo, alfa_borde = alfas[nivel]
        duracion = 0.08 if nivel == "press" else 0.16
        self._c_velo.rgb = color_velo
        self._c_borde.rgb = tuple(tema.primario[:3])
        Animation.cancel_all(self._c_velo)
        Animation.cancel_all(self._c_borde)
        Animation(a=alfa_velo, d=duracion, t="out_quad").start(self._c_velo)
        Animation(a=alfa_borde, d=duracion, t="out_quad").start(self._c_borde)


def aplicar_efecto_boton(widget, radio=None, sobre_primario=None):
    """Instala el efecto en un widget (una sola vez). Devuelve el efecto."""
    existente = getattr(widget, "_efecto_boton", None)
    if existente is not None:
        return existente
    if radio is not None:
        widget.efecto_radio = radio
    if sobre_primario is not None:
        widget.efecto_sobre_primario = sobre_primario
    widget._efecto_boton = EfectoBoton(widget)
    return widget._efecto_boton


_instalado = False


def instalar_efectos():
    """Hace que TODO kivy.uix.button.Button (y subclases) estrene el efecto al crearse."""
    global _instalado
    if _instalado:
        return
    _instalado = True
    original = Button.__init__

    @functools.wraps(original)
    def __init__(self, *args, **kwargs):
        original(self, *args, **kwargs)
        aplicar_efecto_boton(self)

    Button.__init__ = __init__
