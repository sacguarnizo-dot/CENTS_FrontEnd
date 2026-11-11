"""
CENTS - Componentes de Tarjetas, Botones, Entradas, Avatares y Píldoras
Diseñado para adaptarse dinámicamente con alta interactividad al Modo Claro y Modo Oscuro.
"""

import os
import sys
_dir_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _dir_raiz not in sys.path:
    sys.path.insert(0, _dir_raiz)

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, RoundedRectangle, Ellipse, Line
from kivy.properties import ListProperty, StringProperty, BooleanProperty, NumericProperty
from tema import tema

class AvatarCircular(BoxLayout):
    """Avatar circular centrado que actualiza su elipse reactivamente con su pos y size."""
    texto = StringProperty("U")
    diametro = NumericProperty(40)
    
    def __init__(self, texto="U", diametro=40, color_fondo=None, color_texto=[1, 1, 1, 1], **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint=(None, None),
            size=(diametro, diametro),
            **kwargs
        )
        self.diametro = diametro
        self.texto = texto
        self._color_fondo = color_fondo if color_fondo else [0.145, 0.388, 0.922, 1]
        self._color_texto = color_texto
        
        self.lbl = Label(
            text=f"[b]{texto}[/b]",
            markup=True,
            font_size=f"{max(11, int(diametro * 0.40))}sp",
            color=self._color_texto,
            halign="center",
            valign="middle"
        )
        self.lbl.bind(size=self.lbl.setter('text_size'))
        self.add_widget(self.lbl)
        
        self.bind(pos=self._actualizar_canvas, size=self._actualizar_canvas)
        self._actualizar_canvas()
        
    def _actualizar_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self._color_fondo)
            Ellipse(pos=self.pos, size=self.size)
            
    def establecer_color(self, color):
        self._color_fondo = color
        self._actualizar_canvas()
        
    def establecer_texto(self, texto):
        self.texto = texto
        self.lbl.text = f"[b]{texto}[/b]"

class BotonPildora(Button):
    """
    Botón estilo cápsula / píldora para filtros, moneda, idioma y tema.
    Responde visualmente al estado activo, hover, pulsado y modo claro/oscuro.
    """
    activo = BooleanProperty(False)
    radio = ListProperty([8, 8, 8, 8])
    
    def __init__(self, texto="", activo=False, **kwargs):
        kwargs.setdefault('background_normal', '')
        kwargs.setdefault('background_down', '')
        kwargs.setdefault('background_color', [0, 0, 0, 0])
        super().__init__(text=texto, **kwargs)
        self.activo = activo
        self.font_size = "12sp"
        self.bold = True
        
        self.bind(pos=self._actualizar_fondo, size=self._actualizar_fondo, state=self._actualizar_fondo, activo=self._actualizar_fondo)
        tema.bind(modo=self._actualizar_fondo)
        self._actualizar_fondo()
        
    def _actualizar_fondo(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.activo:
                if self.state == 'down':
                    Color(*tema.primario_hover)
                else:
                    Color(*tema.primario)
                RoundedRectangle(pos=self.pos, size=self.size, radius=self.radio)
                self.color = [1, 1, 1, 1]
            else:
                if tema.modo == "oscuro":
                    if self.state == 'down':
                        Color(0.18, 0.25, 0.38, 1)
                    else:
                        Color(0.11, 0.15, 0.23, 1)
                    RoundedRectangle(pos=self.pos, size=self.size, radius=self.radio)
                    Color(0.24, 0.32, 0.46, 1)
                    Line(rounded_rectangle=(self.x, self.y, self.width, self.height, self.radio[0]), width=1)
                    self.color = [0.88, 0.92, 0.98, 1]
                else:
                    if self.state == 'down':
                        Color(0.89, 0.92, 0.96, 1)
                    else:
                        Color(*tema.fondo_sutil)
                    RoundedRectangle(pos=self.pos, size=self.size, radius=self.radio)
                    Color(*tema.borde)
                    Line(rounded_rectangle=(self.x, self.y, self.width, self.height, self.radio[0]), width=1)
                    self.color = tema.texto_secundario

class EntradaTexto(TextInput):
    """
    Campo de texto interactivo con foco visual acentuado, cursor azul,
    soporte completo de teclado, placeholder y adaptación a tema oscuro/claro.
    """
    def __init__(self, **kwargs):
        kwargs.setdefault('multiline', False)
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', 42)
        kwargs.setdefault('padding', [14, 11, 14, 11])
        kwargs.setdefault('font_size', '13sp')
        kwargs.setdefault('cursor_width', 2)
        kwargs.setdefault('write_tab', False)
        super().__init__(**kwargs)
        self.background_active = ""
        self.background_normal = ""
        self.background_color = [0, 0, 0, 0]
        self.selection_color = [0.23, 0.51, 0.96, 0.35]
        self.cursor_color = tema.primario
        self.foreground_color = tema.texto_principal
        self.hint_text_color = tema.texto_placeholder
        
        with self.canvas.before:
            self._color_fondo = Color(*tema.fondo_entrada)
            self._rect_fondo = RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
            self._color_borde = Color(*tema.borde)
            self._line_borde = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 8), width=1)
            
        self.bind(pos=self._actualizar_geometria, size=self._actualizar_geometria, focus=self._actualizar_foco)
        tema.bind(modo=self._al_cambiar_tema)
        
    def _actualizar_geometria(self, *args):
        self._rect_fondo.pos = self.pos
        self._rect_fondo.size = self.size
        self._line_borde.rounded_rectangle = (self.x, self.y, self.width, self.height, 8)
        
    def _actualizar_foco(self, *args):
        if self.focus:
            self._color_borde.rgba = tema.primario
            self._line_borde.width = 1.6
            if tema.modo == "oscuro":
                self._color_fondo.rgba = [0.09, 0.13, 0.20, 1]
            else:
                self._color_fondo.rgba = [1.0, 1.0, 1.0, 1]
        else:
            self._color_borde.rgba = tema.borde
            self._line_borde.width = 1.0
            self._color_fondo.rgba = tema.fondo_entrada
            
    def _al_cambiar_tema(self, *args):
        self.foreground_color = tema.texto_principal
        self.hint_text_color = tema.texto_placeholder
        self.cursor_color = tema.primario
        self._color_fondo.rgba = tema.fondo_entrada
        self._color_borde.rgba = tema.borde
        self._actualizar_foco()

# Alias de compatibilidad
EntradaEstilizada = EntradaTexto

class TarjetaBase(BoxLayout):
    """Contenedor de tarjeta SaaS con esquinas redondeadas y borde sutil."""
    radio = ListProperty([12, 12, 12, 12])
    tiene_borde = BooleanProperty(True)
    fondo_personalizado = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._actualizar_fondo, size=self._actualizar_fondo)
        tema.bind(modo=self._actualizar_fondo)
        
    def _actualizar_fondo(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            color_fondo = self.fondo_personalizado if self.fondo_personalizado else tema.fondo_tarjeta
            Color(*color_fondo)
            RoundedRectangle(pos=self.pos, size=self.size, radius=self.radio)
            if self.tiene_borde:
                Color(*tema.borde)
                Line(rounded_rectangle=(self.x, self.y, self.width, self.height, self.radio[0]), width=1)

class BadgeEstado(BoxLayout):
    """Pill / Etiqueta que muestra el estado de presupuesto o categoría."""
    texto = StringProperty("")
    tipo_badge = StringProperty("exito")
    
    def __init__(self, texto="", tipo_badge="exito", **kwargs):
        super().__init__(size_hint=(None, None), height=26, padding=[10, 2, 10, 2], **kwargs)
        self.texto = texto
        self.tipo_badge = tipo_badge
        
        self.etiqueta = Label(text=self.texto, font_size="11sp", bold=True, size_hint=(None, 1))
        self.etiqueta.bind(texture_size=lambda *a: setattr(self.etiqueta, 'width', self.etiqueta.texture_size[0]))
        self.etiqueta.bind(width=lambda *a: setattr(self, 'width', self.etiqueta.width + 20))
        self.add_widget(self.etiqueta)
        
        self.bind(pos=self._actualizar_fondo, size=self._actualizar_fondo)
        tema.bind(modo=self._actualizar_fondo)
        self._actualizar_fondo()
        
    def _actualizar_fondo(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.tipo_badge == "exito":
                bg = tema.exito_fondo
                tc = tema.exito
            elif self.tipo_badge == "advertencia":
                bg = tema.advertencia_fondo
                tc = tema.advertencia
            elif self.tipo_badge == "peligro":
                bg = tema.peligro_fondo
                tc = tema.peligro
            elif self.tipo_badge == "primario":
                bg = tema.fondo_resaltado
                tc = tema.primario
            else:
                bg = tema.fondo_sutil
                tc = tema.texto_secundario
                
            Color(*bg)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[13])
            self.etiqueta.color = tc

class TarjetaMetrica(TarjetaBase):
    """Tarjeta superior KPI con título, valor principal y variación/subtítulo."""
    def __init__(self, titulo="", valor="", subtitulo="", texto_badge="", es_positivo=True, **kwargs):
        super().__init__(orientation="vertical", padding=[20, 16, 20, 16], spacing=6, **kwargs)
        self.titulo_str = titulo
        self.valor_str = valor
        self.subtitulo_str = subtitulo
        self.texto_badge_str = texto_badge
        self.es_positivo = es_positivo
        
        # Título
        self.lbl_titulo = Label(
            text=titulo,
            font_size="13sp",
            color=tema.texto_secundario,
            size_hint_y=None,
            height=20,
            halign="left"
        )
        self.lbl_titulo.bind(size=self.lbl_titulo.setter('text_size'))
        self.add_widget(self.lbl_titulo)
        
        # Valor
        self.lbl_val = Label(
            text=f"[b]{valor}[/b]",
            markup=True,
            font_size="24sp",
            color=tema.texto_principal,
            size_hint_y=None,
            height=34,
            halign="left"
        )
        self.lbl_val.bind(size=self.lbl_val.setter('text_size'))
        self.add_widget(self.lbl_val)
        
        # Fila inferior con badge o subtítulo
        fila_inferior = BoxLayout(orientation="horizontal", spacing=6, size_hint_y=None, height=22)
        if texto_badge:
            self.badge = BadgeEstado(texto=texto_badge, tipo_badge="primario" if es_positivo else "advertencia")
            fila_inferior.add_widget(self.badge)
            
        if subtitulo:
            self.lbl_sub = Label(
                text=subtitulo,
                font_size="12sp",
                color=tema.texto_atenuado,
                size_hint_x=1,
                halign="left"
            )
            self.lbl_sub.bind(size=self.lbl_sub.setter('text_size'))
            fila_inferior.add_widget(self.lbl_sub)
            
        self.add_widget(fila_inferior)
        tema.bind(modo=self.actualizar_tema)
        
    def actualizar_valor(self, nuevo_valor):
        self.valor_str = nuevo_valor
        self.lbl_val.text = f"[b]{nuevo_valor}[/b]"
        
    def actualizar_tema(self, *args):
        self.lbl_titulo.color = tema.texto_secundario
        self.lbl_val.color = tema.texto_principal
        if hasattr(self, 'lbl_sub'):
            self.lbl_sub.color = tema.texto_atenuado

class BarraProgreso(Widget):
    """Barra de progreso redondeada para presupuestos."""
    progreso = NumericProperty(0)
    color_relleno = ListProperty([0.086, 0.686, 0.38, 1])
    
    def __init__(self, progreso=0, color_relleno=None, **kwargs):
        super().__init__(size_hint_y=None, height=8, **kwargs)
        self.progreso = progreso
        if color_relleno:
            self.color_relleno = color_relleno
        self.bind(pos=self._actualizar, size=self._actualizar, progreso=self._actualizar)
        tema.bind(modo=self._actualizar)
        
    def _actualizar(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(*tema.fondo_sutil)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[4])
            
            porc = min(max(self.progreso, 0), 100)
            ancho_relleno = (porc / 100.0) * self.width
            if ancho_relleno > 0:
                Color(*self.color_relleno)
                RoundedRectangle(pos=self.pos, size=(ancho_relleno, self.height), radius=[4])

class TarjetaPresupuestoCategoria(TarjetaBase):
    """Tarjeta individual de límite por categoría con barra de progreso."""
    def __init__(self, nombre_categoria="", gastado=0.0, limite=0.0, porcentaje=0, estado="", color=None, **kwargs):
        super().__init__(orientation="vertical", padding=[16, 16, 16, 16], spacing=10, **kwargs)
        
        fila_sup = BoxLayout(orientation="horizontal", size_hint_y=None, height=28)
        self.lbl_cat = Label(
            text=f"[b]{nombre_categoria}[/b]",
            markup=True,
            font_size="15sp",
            color=tema.texto_principal,
            halign="left"
        )
        self.lbl_cat.bind(size=self.lbl_cat.setter('text_size'))
        fila_sup.add_widget(self.lbl_cat)
        
        tipo_b = "exito"
        if "excedido" in estado.lower():
            tipo_b = "peligro"
        elif "cerca" in estado.lower():
            tipo_b = "advertencia"
            
        badge = BadgeEstado(texto=estado, tipo_badge=tipo_b)
        fila_sup.add_widget(badge)
        self.add_widget(fila_sup)
        
        self.lbl_montos = Label(
            text=f"[b]${gastado:,.2f}[/b] [color=#94A3B8]de ${limite:,.2f}[/color]",
            markup=True,
            font_size="16sp",
            color=tema.texto_principal,
            size_hint_y=None,
            height=24,
            halign="left"
        )
        self.lbl_montos.bind(size=self.lbl_montos.setter('text_size'))
        self.add_widget(self.lbl_montos)
        
        fila_prog = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=18)
        color_barra = color if color else [0.086, 0.686, 0.38, 1]
        self.barra = BarraProgreso(progreso=porcentaje, color_relleno=color_barra, size_hint_x=0.82)
        fila_prog.add_widget(self.barra)
        
        self.lbl_pct = Label(
            text=f"{porcentaje}%",
            font_size="13sp",
            bold=True,
            color=tema.texto_secundario,
            size_hint_x=0.18,
            halign="right"
        )
        self.lbl_pct.bind(size=self.lbl_pct.setter('text_size'))
        fila_prog.add_widget(self.lbl_pct)
        
        self.add_widget(fila_prog)
        tema.bind(modo=self.actualizar_tema)
        
    def actualizar_tema(self, *args):
        self.lbl_cat.color = tema.texto_principal
        self.lbl_montos.color = tema.texto_principal
        self.lbl_pct.color = tema.texto_secundario

class BotonPrimario(Button):
    """Botón azul SaaS principal o contorneado con retroalimentación táctil."""
    radio = ListProperty([8, 8, 8, 8])
    es_contorno = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        kwargs.setdefault('background_normal', '')
        kwargs.setdefault('background_down', '')
        kwargs.setdefault('background_color', [0, 0, 0, 0])
        super().__init__(**kwargs)
        self.font_size = "14sp"
        self.bold = True
        self.bind(pos=self._actualizar_fondo, size=self._actualizar_fondo, state=self._actualizar_fondo)
        tema.bind(modo=self._actualizar_fondo)
        self._actualizar_fondo()
        
    def _actualizar_fondo(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.es_contorno:
                if self.state == 'down':
                    Color(*tema.fondo_sutil)
                else:
                    Color(0, 0, 0, 0)
                RoundedRectangle(pos=self.pos, size=self.size, radius=self.radio)
                Color(*tema.borde)
                Line(rounded_rectangle=(self.x, self.y, self.width, self.height, self.radio[0]), width=1.2)
                self.color = tema.texto_principal
            else:
                if self.state == 'down':
                    Color(*tema.primario_hover)
                else:
                    Color(*tema.primario)
                RoundedRectangle(pos=self.pos, size=self.size, radius=self.radio)
                self.color = [1, 1, 1, 1]
