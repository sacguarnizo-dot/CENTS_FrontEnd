"""
CENTS - Barra de paginación real

    FilaPaginacion(unidad="movimientos", tamano=10, al_cambiar=funcion)
    fila.actualizar(total, pagina)

Muestra "Mostrando 1 - 10 de 24 movimientos" y los botones de página, calculados a partir
del total y del tamaño de página. Los números se muestran de 3 en 3 (1 2 3 / 4 5 6 ...);
la flecha → avanza a la página siguiente y ← aparece cuando hay páginas anteriores ocultas.
"""
import os
import sys
_dir_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _dir_raiz not in sys.path:
    sys.path.insert(0, _dir_raiz)

import math
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from tema import tema
from iconos import icono
from componentes.tarjetas import BotonPildora

BOTONES_VISIBLES = 3


class FilaPaginacion(BoxLayout):
    def __init__(self, unidad="movimientos", tamano=10, al_cambiar=None, tam_boton=32, alto=36, padding=None, **kwargs):
        super().__init__(orientation="horizontal", size_hint_y=None, height=alto, padding=padding or [8, 8, 8, 0], **kwargs)
        self.unidad = unidad
        self.tamano = tamano
        self.al_cambiar = al_cambiar
        self.tam_boton = tam_boton
        self.total = 0
        self.pagina = 1

        self.lbl = Label(text="", font_size="12sp", color=tema.texto_atenuado, halign="left")
        self.lbl.bind(size=self.lbl.setter("text_size"))
        self.add_widget(self.lbl)

        self.caja = BoxLayout(orientation="horizontal", spacing=6, size_hint=(None, 1))
        self.caja.bind(minimum_width=self.caja.setter("width"))
        self.add_widget(self.caja)
        self.actualizar(0, 1)

    @property
    def paginas(self):
        return max(1, math.ceil(self.total / self.tamano))

    def actualizar(self, total, pagina):
        """Recalcula texto y botones para `total` registros estando en `pagina`."""
        self.total = total
        self.pagina = min(max(1, pagina), self.paginas)
        if total:
            desde = (self.pagina - 1) * self.tamano + 1
            hasta = min(self.pagina * self.tamano, total)
            self.lbl.text = f"Mostrando {desde} - {hasta} de {total} {self.unidad}"
        else:
            self.lbl.text = f"Sin {self.unidad}"
        self._dibujar_botones()

    def _crear_boton(self, texto, activo=False, destino=None):
        b = BotonPildora(texto=texto, activo=activo, markup=True, size_hint=(None, None), size=(self.tam_boton, self.tam_boton))
        b.efecto_radio = 6
        b.bind(on_release=lambda *a, d=destino: self.ir_a(d))
        return b

    def _dibujar_botones(self):
        self.caja.clear_widgets()
        paginas = self.paginas
        inicio = ((self.pagina - 1) // BOTONES_VISIBLES) * BOTONES_VISIBLES + 1
        fin = min(inicio + BOTONES_VISIBLES - 1, paginas)
        if inicio > 1:
            self.caja.add_widget(self._crear_boton(icono("arrow-left"), destino=self.pagina - 1))
        for n in range(inicio, fin + 1):
            self.caja.add_widget(self._crear_boton(str(n), activo=(n == self.pagina), destino=n))
        if self.pagina < paginas:
            self.caja.add_widget(self._crear_boton(icono("arrow-right"), destino=self.pagina + 1))

    def ir_a(self, pagina):
        if pagina is None or pagina == self.pagina:
            return
        self.pagina = pagina
        if self.al_cambiar:
            self.al_cambiar(pagina)  # la pantalla recarga sus filas y vuelve a llamar a actualizar()
        else:
            self.actualizar(self.total, pagina)

    def actualizar_tema(self, *args):
        self.lbl.color = tema.texto_atenuado
        self._dibujar_botones()
