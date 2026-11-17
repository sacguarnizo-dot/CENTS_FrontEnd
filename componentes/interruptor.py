"""
CENTS - Interruptor (switch) animado con el estilo de la app

    Interruptor(activo=True, al_cambiar=funcion)     # funcion(nuevo_valor)
    interruptor.establecer(False)                    # cambia el estado sin llamar a al_cambiar
"""
import os
import sys
_dir_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _dir_raiz not in sys.path:
    sys.path.insert(0, _dir_raiz)

from kivy.animation import Animation
from kivy.graphics import Color, RoundedRectangle, Ellipse
from kivy.properties import BooleanProperty, NumericProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget
from tema import tema
from efectos import aplicar_efecto_boton


class Interruptor(ButtonBehavior, Widget):
    activo = BooleanProperty(False)
    posicion = NumericProperty(0.0)  # 0 = apagado, 1 = encendido (se anima)

    def __init__(self, activo=False, al_cambiar=None, **kwargs):
        super().__init__(size_hint=(None, None), size=(46, 26), **kwargs)
        self.al_cambiar = al_cambiar
        self.activo = activo
        self.posicion = 1.0 if activo else 0.0
        self.bind(pos=self._dibujar, size=self._dibujar, posicion=self._dibujar, disabled=self._dibujar)
        self.bind(activo=self._animar)
        tema.bind(modo=self._dibujar)
        aplicar_efecto_boton(self, radio=13)
        self._dibujar()

    def on_release(self, *args):
        self.activo = not self.activo
        if self.al_cambiar:
            self.al_cambiar(self.activo)

    def establecer(self, valor):
        self.activo = bool(valor)

    def _animar(self, *args):
        Animation.cancel_all(self, "posicion")
        Animation(posicion=1.0 if self.activo else 0.0, d=0.18, t="out_quad").start(self)

    def _dibujar(self, *args):
        t = self.posicion
        apagado = [(tema.borde[i] + tema.texto_atenuado[i]) / 2 for i in range(4)]
        color = [apagado[i] + (tema.primario[i] - apagado[i]) * t for i in range(4)]
        if self.disabled:
            color[3] *= 0.45
        d = self.height - 6
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[self.height / 2])
            Color(1, 1, 1, 0.6 if self.disabled else 1)
            Ellipse(pos=(self.x + 3 + (self.width - 6 - d) * t, self.y + 3), size=(d, d))
