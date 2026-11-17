"""
CENTS - Menú desplegable para los botones de filtro

    abrir_menu(boton, [(None, "Todas"), ("Salario", "Salario")], seleccionado, al_elegir)

Se abre justo debajo del botón con el estilo de la app (tarjeta con borde, opción activa
resaltada y marca de verificación). Al elegir una opción llama a al_elegir(valor).
"""
import os
import sys
_dir_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _dir_raiz not in sys.path:
    sys.path.insert(0, _dir_raiz)

from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.graphics import Color, RoundedRectangle, Line
from tema import tema
from iconos import con_icono


class _ItemMenu(Button):
    def __init__(self, etiqueta, activo, **kwargs):
        texto = con_icono(etiqueta, "check", derecha=True, separacion="   ") if activo else etiqueta
        super().__init__(
            text=texto,
            markup=True,
            size_hint_y=None,
            height=34,
            font_size="12sp",
            bold=activo,
            halign="left",
            valign="middle",
            padding=[12, 0],
            background_normal="",
            background_down="",
            background_color=[0, 0, 0, 0],
            color=tema.primario if activo else tema.texto_principal,
            **kwargs
        )
        self.activo_item = activo
        self.efecto_radio = 6
        self.bind(size=lambda w, *a: setattr(w, "text_size", (w.width, w.height)))
        self.bind(pos=self._dibujar, size=self._dibujar)

    def _dibujar(self, *args):
        self.canvas.before.clear()
        if self.activo_item:
            with self.canvas.before:
                Color(*tema.fondo_resaltado)
                RoundedRectangle(pos=self.pos, size=self.size, radius=[6])


class MenuFiltro(DropDown):
    def __init__(self, opciones, seleccionado=None, al_elegir=None, ancho=210, **kwargs):
        super().__init__(auto_width=False, width=ancho, max_height=300, bar_width=5, **kwargs)
        self._al_elegir = al_elegir
        self.container.padding = [6, 6, 6, 6]
        self.container.spacing = 2
        with self.container.canvas.before:
            self._c_fondo = Color(*tema.fondo_tarjeta)
            self._r_fondo = RoundedRectangle(pos=self.container.pos, size=self.container.size, radius=[10])
            self._c_borde = Color(*tema.borde)
            self._l_borde = Line(rounded_rectangle=(self.container.x, self.container.y, self.container.width, self.container.height, 10), width=1)
        self.container.bind(pos=self._geometria, size=self._geometria)

        for valor, etiqueta in opciones:
            item = _ItemMenu(etiqueta, activo=(valor == seleccionado))
            item.bind(on_release=lambda w, v=valor: self.select(v))
            self.add_widget(item)
        self.bind(on_select=self._elegido)

    def _geometria(self, *args):
        c = self.container
        self._r_fondo.pos = c.pos
        self._r_fondo.size = c.size
        self._l_borde.rounded_rectangle = (c.x, c.y, c.width, c.height, 10)

    def _elegido(self, _menu, valor):
        if self._al_elegir:
            self._al_elegir(valor)


def abrir_menu(boton, opciones, seleccionado, al_elegir, ancho=None):
    """Abre el menú de opciones [(valor, etiqueta), ...] debajo de `boton`."""
    ancho = ancho or max(boton.width, 190)
    menu = MenuFiltro(opciones, seleccionado, al_elegir, ancho)
    boton._menu_filtro = menu  # evita que el menú se recoja mientras está abierto
    menu.open(boton)
    return menu
