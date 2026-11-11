"""
CENTS - Gráficos Financieros Nativos en Kivy (Donut y Barras)
Soporte completo y reactivo para Modo Claro y Modo Oscuro.
"""

import os
import sys
_dir_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _dir_raiz not in sys.path:
    sys.path.insert(0, _dir_raiz)

from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse, Line, RoundedRectangle
from tema import tema

class WidgetGraficoDonut(Widget):
    """Dibuja el donut de categorías con trazos y proporciones exactas."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.actualizar_canvas, size=self.actualizar_canvas)
        tema.bind(modo=self.actualizar_canvas)
        
    def actualizar_canvas(self, *args):
        self.canvas.clear()
        if self.width <= 0 or self.height <= 0:
            return
            
        with self.canvas:
            diametro = min(self.width, self.height) * 0.82
            x = self.x + (self.width - diametro) / 2
            y = self.y + (self.height - diametro) / 2
            
            # Segmentos: Alimentación (32%), Transporte (22%), Vivienda (18%), Otros (28%)
            segmentos = [
                (0.32, [0.145, 0.388, 0.922, 1]),  # Alimentación - Azul Real
                (0.22, [0.22, 0.74, 0.97, 1]),     # Transporte - Celeste
                (0.18, [0.50, 0.55, 0.97, 1]),     # Vivienda - Índigo
                (0.28, [0.65, 0.72, 0.82, 1] if tema.modo == 'claro' else [0.30, 0.38, 0.50, 1]), # Otros
            ]
            
            angulo_actual = 0
            for fraccion, col in segmentos:
                Color(*col)
                amplitud = fraccion * 360
                Ellipse(pos=(x, y), size=(diametro, diametro), angle_start=angulo_actual, angle_end=angulo_actual + amplitud)
                angulo_actual += amplitud
                
            # Agujero interior para formar la dona
            radio_interno = diametro * 0.62
            ix = x + (diametro - radio_interno) / 2
            iy = y + (diametro - radio_interno) / 2
            
            Color(*tema.fondo_tarjeta)
            Ellipse(pos=(ix, iy), size=(radio_interno, radio_interno))

class ContenedorGraficoDonut(BoxLayout):
    """Contenedor horizontal con el gráfico de dona, texto central y leyenda."""
    def __init__(self, **kwargs):
        super().__init__(orientation="horizontal", spacing=10, **kwargs)
        
        from kivy.uix.floatlayout import FloatLayout
        caja_dona = FloatLayout(size_hint=(0.55, 1))
        
        self.donut = WidgetGraficoDonut(size_hint=(1, 1), pos_hint={"center_x": 0.5, "center_y": 0.5})
        caja_dona.add_widget(self.donut)
        
        self.etiqueta_centro = Label(
            text="[b][size=19]$1,245[/size][/b]\n[size=12]Total[/size]",
            markup=True,
            halign="center",
            valign="middle",
            color=tema.texto_principal,
            size_hint=(1, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        caja_dona.add_widget(self.etiqueta_centro)
        self.add_widget(caja_dona)
        
        # Leyenda
        self.diseno_leyenda = BoxLayout(orientation="vertical", spacing=8, size_hint=(0.45, 1), padding=[0, 15, 10, 15])
        
        elementos_leyenda = [
            ("Alimentación", "32%", [0.145, 0.388, 0.922, 1]),
            ("Transporte", "22%", [0.22, 0.74, 0.97, 1]),
            ("Vivienda", "18%", [0.50, 0.55, 0.97, 1]),
            ("Otros", "28%", [0.65, 0.72, 0.82, 1]),
        ]
        
        self.filas_leyenda = []
        for nombre, pct, col in elementos_leyenda:
            fila = BoxLayout(orientation="horizontal", spacing=8, size_hint_y=None, height=24)
            punto = Widget(size_hint=(None, None), size=(10, 10), pos_hint={"center_y": 0.5})
            with punto.canvas:
                Color(*col)
                Ellipse(pos=punto.pos, size=punto.size)
            punto.bind(pos=lambda w, *a, c=col: self._redibujar_punto(w, c))
            
            lbl_nom = Label(text=nombre, font_size="13sp", color=tema.texto_secundario, halign="left", size_hint_x=0.7)
            lbl_nom.bind(size=lbl_nom.setter('text_size'))
            lbl_pct = Label(text=pct, font_size="13sp", bold=True, color=tema.texto_principal, halign="right", size_hint_x=0.3)
            lbl_pct.bind(size=lbl_pct.setter('text_size'))
            
            fila.add_widget(punto)
            fila.add_widget(lbl_nom)
            fila.add_widget(lbl_pct)
            self.diseno_leyenda.add_widget(fila)
            self.filas_leyenda.append((lbl_nom, lbl_pct))
            
        self.add_widget(self.diseno_leyenda)
        tema.bind(modo=self.actualizar_tema)
        
    def _redibujar_punto(self, w, col):
        w.canvas.clear()
        with w.canvas:
            Color(*col)
            Ellipse(pos=w.pos, size=w.size)
            
    def actualizar_tema(self, *args):
        self.etiqueta_centro.color = tema.texto_principal
        for lbl_nom, lbl_pct in self.filas_leyenda:
            lbl_nom.color = tema.texto_secundario
            lbl_pct.color = tema.texto_principal

class WidgetGraficoBarras(Widget):
    """Dibuja barras para la comparativa de los últimos 6 meses (Jun a Nov)."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.meses = ["Jun", "Jul", "Ago", "Sep", "Oct", "Nov"]
        self.valores = [850, 1100, 920, 1350, 1050, 1245]
        self.bind(pos=self.actualizar_canvas, size=self.actualizar_canvas)
        tema.bind(modo=self.actualizar_canvas)
        
    def actualizar_canvas(self, *args):
        self.canvas.clear()
        if self.width <= 0 or self.height <= 0:
            return
            
        with self.canvas:
            relleno_inferior = 28
            relleno_superior = 20
            relleno_x = 24
            alto_grafico = self.height - relleno_inferior - relleno_superior
            ancho_grafico = self.width - relleno_x * 2
            
            Color(*tema.borde_claro)
            for i in range(4):
                linea_y = self.y + relleno_inferior + (alto_grafico / 3) * i
                Line(points=[self.x + relleno_x, linea_y, self.x + self.width - relleno_x, linea_y], width=1)
                
            n = len(self.meses)
            ancho_ranura = ancho_grafico / n
            ancho_barra = min(ancho_ranura * 0.45, 34)
            valor_max = 1500.0
            
            for i, (m, val) in enumerate(zip(self.meses, self.valores)):
                alto_b = (val / valor_max) * alto_grafico
                bx = self.x + relleno_x + i * ancho_ranura + (ancho_ranura - ancho_barra) / 2
                by = self.y + relleno_inferior
                
                if i == n - 1:
                    Color(*tema.primario)
                else:
                    if tema.modo == 'claro':
                        Color(0.78, 0.84, 0.94, 0.85)
                    else:
                        Color(0.24, 0.32, 0.45, 0.8)
                    
                RoundedRectangle(pos=(bx, by), size=(ancho_barra, alto_b), radius=[4, 4, 0, 0])
