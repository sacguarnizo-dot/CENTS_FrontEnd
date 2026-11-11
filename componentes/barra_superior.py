"""
CENTS - Barra Superior (TopBar)
Muestra título de pantalla, fecha con icono, perfil del usuario y botón de acción.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.properties import StringProperty, ObjectProperty
from kivymd.icon_definitions import md_icons
from tema import tema
from estado_app import estado
from componentes.tarjetas import AvatarCircular

class BotonCapsulaPerfil(ButtonBehavior, BoxLayout):
    """Cápsula interactiva del perfil que contiene el avatar y nombre del usuario."""
    def __init__(self, al_click=None, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint=(None, None),
            size=(148, 42),
            padding=[6, 4, 10, 4],
            spacing=8,
            pos_hint={"center_y": 0.5},
            **kwargs
        )
        self.al_click = al_click
        
        # Avatar circular dinámico
        self.avatar = AvatarCircular(texto="U", diametro=32)
        self.add_widget(self.avatar)
        
        # Nombre y rol
        caja_nom = BoxLayout(orientation="vertical", spacing=0)
        self.lbl_nom_usuario = Label(
            text=f"[b]{estado.usuario_actual.get('nombre', 'Usuario 1')}[/b]",
            markup=True,
            font_size="12sp",
            color=tema.texto_principal,
            halign="left"
        )
        self.lbl_nom_usuario.bind(size=self.lbl_nom_usuario.setter('text_size'))
        
        self.lbl_rol_usuario = Label(
            text="Usuario",
            font_size="10sp",
            color=tema.texto_atenuado,
            halign="left"
        )
        self.lbl_rol_usuario.bind(size=self.lbl_rol_usuario.setter('text_size'))
        
        caja_nom.add_widget(self.lbl_nom_usuario)
        caja_nom.add_widget(self.lbl_rol_usuario)
        self.add_widget(caja_nom)
        
        self.bind(pos=self._actualizar_fondo, size=self._actualizar_fondo)
        tema.bind(modo=self._actualizar_fondo)
        estado.bind(usuario_actual=self._actualizar_datos_usuario)
        self._actualizar_fondo()
        
    def _actualizar_fondo(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*tema.fondo_tarjeta)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[21])
            Color(*tema.borde)
            Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 21), width=1)
        self.lbl_nom_usuario.color = tema.texto_principal
        self.lbl_rol_usuario.color = tema.texto_atenuado
        
    def _actualizar_datos_usuario(self, *args):
        self.lbl_nom_usuario.text = f"[b]{estado.usuario_actual.get('nombre', 'Usuario 1')}[/b]"
        iniciales = estado.usuario_actual.get('iniciales', 'U')
        self.avatar.establecer_texto(iniciales[:2])
        
    def on_release(self):
        if self.al_click:
            self.al_click()

class BarraSuperior(BoxLayout):
    texto_titulo = StringProperty("Panel financiero")
    texto_subtitulo = StringProperty("Resumen general de tus finanzas")
    al_click_perfil = ObjectProperty(None)
    al_click_accion = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=70,
            padding=[24, 12, 24, 12],
            spacing=16,
            **kwargs
        )
        self.bind(pos=self._actualizar_fondo, size=self._actualizar_fondo)
        tema.bind(modo=self._actualizar_fondo)
        self._construir_ui()
        
    def _actualizar_fondo(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*tema.fondo_app)
            RoundedRectangle(pos=self.pos, size=self.size)
            Color(*tema.borde)
            Line(points=[self.x, self.y, self.x + self.width, self.y], width=1)
            
    def _construir_ui(self):
        # 1. Títulos Izquierda
        caja_titulo = BoxLayout(orientation="vertical", spacing=2, size_hint_x=0.48)
        
        self.lbl_titulo = Label(
            text=f"[b]{self.texto_titulo}[/b]",
            markup=True,
            font_size="18sp",
            color=tema.texto_principal,
            halign="left",
            valign="middle"
        )
        self.lbl_titulo.bind(size=self.lbl_titulo.setter('text_size'))
        caja_titulo.add_widget(self.lbl_titulo)
        
        self.lbl_subtitulo = Label(
            text=self.texto_subtitulo,
            font_size="12sp",
            color=tema.texto_secundario,
            halign="left",
            valign="middle"
        )
        self.lbl_subtitulo.bind(size=self.lbl_subtitulo.setter('text_size'))
        caja_titulo.add_widget(self.lbl_subtitulo)
        
        self.add_widget(caja_titulo)
        self.add_widget(Widget())
        
        # 2. Controles Derecha
        caja_derecha = BoxLayout(orientation="horizontal", spacing=12, size_hint=(None, 1))
        caja_derecha.bind(minimum_width=caja_derecha.setter('width'))
        
        # Píldora de fecha interactiva con icono de calendario
        self.pildora_fecha = BoxLayout(
            orientation="horizontal",
            size_hint=(None, None),
            size=(155, 38),
            padding=[10, 4, 12, 4],
            spacing=6,
            pos_hint={"center_y": 0.5}
        )
        self.pildora_fecha.bind(pos=lambda w, *a: self._redibujar_pildora(w), size=lambda w, *a: self._redibujar_pildora(w))
        
        self.ico_cal = Label(
            text=md_icons.get("calendar-month-outline", "📅"),
            font_name="Icons",
            font_size="16sp",
            color=tema.primario,
            size_hint=(None, 1),
            width=20
        )
        self.lbl_f = Label(
            text="Noviembre 2026",
            font_size="12sp",
            color=tema.texto_secundario,
            halign="left"
        )
        self.lbl_f.bind(size=self.lbl_f.setter('text_size'))
        self.pildora_fecha.add_widget(self.ico_cal)
        self.pildora_fecha.add_widget(self.lbl_f)
        caja_derecha.add_widget(self.pildora_fecha)
        self._redibujar_pildora(self.pildora_fecha)
        
        # Botón contextual de acción (ej. + Nuevo gasto / + Nuevo ingreso)
        self.btn_accion = Button(
            text="＋ Nuevo",
            font_size="13sp",
            bold=True,
            color=[1, 1, 1, 1],
            background_normal="",
            background_down="",
            background_color=[0, 0, 0, 0],
            size_hint=(None, None),
            size=(132, 38),
            pos_hint={"center_y": 0.5}
        )
        self.btn_accion.bind(pos=lambda w, *a: self._redibujar_btn_accion(w), size=lambda w, *a: self._redibujar_btn_accion(w), state=lambda w, *a: self._redibujar_btn_accion(w))
        self.btn_accion.bind(on_release=lambda *a: self.manejar_accion())
        caja_derecha.add_widget(self.btn_accion)
        self.btn_accion.opacity = 0
        self.btn_accion.disabled = True
        
        # Cápsula de perfil del usuario (sin desplazamientos a 0, 0)
        self.btn_perfil = BotonCapsulaPerfil(al_click=self.manejar_click_perfil)
        caja_derecha.add_widget(self.btn_perfil)
        
        self.add_widget(caja_derecha)
        
    def _redibujar_pildora(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.fondo_tarjeta)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[8])
            Color(*tema.borde)
            Line(rounded_rectangle=(w.x, w.y, w.width, w.height, 8), width=1)
            
    def _redibujar_btn_accion(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            if w.state == 'down':
                Color(*tema.primario_hover)
            else:
                Color(*tema.primario)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[8])
            
    def actualizar_encabezado(self, titulo, subtitulo, texto_accion=None):
        self.texto_titulo = titulo
        self.texto_subtitulo = subtitulo
        self.lbl_titulo.text = f"[b]{titulo}[/b]"
        self.lbl_subtitulo.text = subtitulo
        if texto_accion:
            self.btn_accion.text = texto_accion
            self.btn_accion.opacity = 1
            self.btn_accion.disabled = False
        else:
            self.btn_accion.opacity = 0
            self.btn_accion.disabled = True
            
    def manejar_accion(self):
        if self.al_click_accion:
            self.al_click_accion()
            
    def manejar_click_perfil(self):
        if self.al_click_perfil:
            self.al_click_perfil()
            
    def actualizar_tema(self, *args):
        self._actualizar_fondo()
        self.lbl_titulo.color = tema.texto_principal
        self.lbl_subtitulo.color = tema.texto_secundario
        self._redibujar_pildora(self.pildora_fecha)
        self.ico_cal.color = tema.primario
        self.lbl_f.color = tema.texto_secundario
        self._redibujar_btn_accion(self.btn_accion)
        self.btn_perfil._actualizar_fondo()
