"""
CENTS - Barra Lateral de Navegación (Sidebar)
Navegación profesional estilo SaaS con iconos nativos Material Design
y adaptación dinámica a Modo Claro y Modo Oscuro.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivymd.icon_definitions import md_icons
from tema import tema
from estado_app import estado
from componentes.tarjetas import AvatarCircular

class BotonElementoMenu(ButtonBehavior, BoxLayout):
    activo = BooleanProperty(False)
    pantalla_destino = StringProperty("")
    
    def __init__(self, texto="", clave_icono="view-dashboard-outline", destino="", **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=44,
            padding=[12, 6, 12, 6],
            spacing=12,
            **kwargs
        )
        self.contenido_texto = texto
        self.clave_icono = clave_icono
        self.pantalla_destino = destino
        
        # Icono nativo de Material Design (Icons)
        self.ico = Label(
            text=md_icons.get(clave_icono, "●"),
            font_name="Icons",
            font_size="18sp",
            size_hint=(None, 1),
            width=26,
            halign="center",
            valign="middle"
        )
        self.ico.bind(size=self.ico.setter('text_size'))
        self.add_widget(self.ico)
        
        # Etiqueta de texto
        self.lbl = Label(
            text=texto,
            font_size="13sp",
            size_hint_x=1,
            halign="left",
            valign="middle"
        )
        self.lbl.bind(size=self.lbl.setter('text_size'))
        self.add_widget(self.lbl)
        
        self.bind(pos=self._actualizar_fondo, size=self._actualizar_fondo, state=self._actualizar_fondo, activo=self._actualizar_fondo)
        tema.bind(modo=self._actualizar_fondo)
        self._actualizar_fondo()
        
    def _actualizar_fondo(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.activo:
                Color(*tema.fondo_resaltado)
                RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
                Color(*tema.primario)
                RoundedRectangle(pos=(self.x, self.y + 6), size=(4, self.height - 12), radius=[2])
                self.ico.color = tema.primario
                self.lbl.color = tema.primario
                self.lbl.bold = True
            else:
                if self.state == 'down':
                    Color(*tema.fondo_sutil)
                    RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
                else:
                    Color(0, 0, 0, 0)
                    RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
                self.ico.color = tema.texto_secundario
                self.lbl.color = tema.texto_secundario
                self.lbl.bold = False

class MenuLateral(BoxLayout):
    """Barra lateral fija de navegación."""
    al_navegar = ObjectProperty(None)
    al_mostrar_consejos = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint=(None, 1),
            width=250,
            padding=[16, 20, 16, 20],
            spacing=16,
            **kwargs
        )
        self.botones_menu = {}
        self.bind(pos=self._actualizar_fondo, size=self._actualizar_fondo)
        tema.bind(modo=self._actualizar_fondo)
        self._construir_ui()
        
    def _actualizar_fondo(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*tema.fondo_barra_lateral)
            Rectangle(pos=self.pos, size=self.size)
            Color(*tema.borde)
            Line(points=[self.x + self.width, self.y, self.x + self.width, self.y + self.height], width=1)
            
    def _construir_ui(self):
        # 1. Logotipo: [C] CENTS
        caja_logo = BoxLayout(orientation="horizontal", spacing=12, size_hint_y=None, height=44)
        
        self.logo_avatar = AvatarCircular(
            texto="C",
            diametro=38,
            color_fondo=[0.145, 0.388, 0.922, 1],
            pos_hint={"center_y": 0.5}
        )
        caja_logo.add_widget(self.logo_avatar)
        
        self.lbl_cents = Label(
            text="[b]CENTS[/b]",
            markup=True,
            font_size="20sp",
            color=tema.texto_principal,
            halign="left",
            valign="middle"
        )
        self.lbl_cents.bind(size=self.lbl_cents.setter('text_size'))
        caja_logo.add_widget(self.lbl_cents)
        self.add_widget(caja_logo)
        
        # 2. Encabezado de Sección: MENÚ PRINCIPAL
        self.lbl_sec = Label(
            text="MENÚ PRINCIPAL",
            font_size="11sp",
            bold=True,
            color=tema.texto_atenuado,
            size_hint_y=None,
            height=26,
            halign="left"
        )
        self.lbl_sec.bind(size=self.lbl_sec.setter('text_size'))
        self.add_widget(self.lbl_sec)
        
        # 3. Lista de Opciones de Navegación con Material Design Icons
        elementos = [
            ("Inicio", "view-dashboard-outline", "inicio"),
            ("Ingresos", "wallet-outline", "ingresos"),
            ("Gastos", "cash-minus", "gastos"),
            ("Presupuestos", "chart-pie", "presupuestos"),
            ("Inversiones", "trending-up", "inversiones"),
            ("Configuración", "cog-outline", "configuracion"),
        ]
        
        contenedor_nav = BoxLayout(orientation="vertical", spacing=4, size_hint_y=None)
        contenedor_nav.bind(minimum_height=contenedor_nav.setter('height'))
        
        for texto, clave_ico, destino in elementos:
            btn = BotonElementoMenu(texto=texto, clave_icono=clave_ico, destino=destino)
            btn.bind(on_release=lambda b, d=destino: self.manejar_navegacion(d))
            self.botones_menu[destino] = btn
            contenedor_nav.add_widget(btn)
            
        self.add_widget(contenedor_nav)
        
        # Espaciador flexible
        self.add_widget(Widget())
        
        # 4. Tarjeta Inferior: Consejo del día
        self.tarjeta_consejo = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=130,
            padding=[14, 12, 14, 12],
            spacing=6
        )
        self.tarjeta_consejo.bind(pos=lambda w, *a: self._redibujar_tarjeta_consejo(w), size=lambda w, *a: self._redibujar_tarjeta_consejo(w))
        
        fila_tit_c = BoxLayout(orientation="horizontal", spacing=6, size_hint_y=None, height=22)
        self.ico_consejo = Label(
            text=md_icons.get("lightbulb-on-outline", "💡"),
            font_name="Icons",
            font_size="16sp",
            color=tema.primario,
            size_hint=(None, 1),
            width=20
        )
        self.tit_consejo = Label(
            text="[b]Consejo del día[/b]",
            markup=True,
            font_size="13sp",
            color=tema.primario,
            halign="left"
        )
        self.tit_consejo.bind(size=self.tit_consejo.setter('text_size'))
        fila_tit_c.add_widget(self.ico_consejo)
        fila_tit_c.add_widget(self.tit_consejo)
        self.tarjeta_consejo.add_widget(fila_tit_c)
        
        self.txt_consejo = Label(
            text="Revisa tus gastos cada semana para mantener tu presupuesto.",
            font_size="11sp",
            color=tema.texto_secundario,
            halign="left",
            valign="top"
        )
        self.txt_consejo.bind(size=self.txt_consejo.setter('text_size'))
        self.tarjeta_consejo.add_widget(self.txt_consejo)
        
        self.btn_ver_consejos = Button(
            text="Ver consejos →",
            font_size="12sp",
            bold=True,
            color=tema.primario,
            background_normal="",
            background_down="",
            background_color=[0, 0, 0, 0],
            size_hint_y=None,
            height=26,
            halign="left"
        )
        self.btn_ver_consejos.bind(size=self.btn_ver_consejos.setter('text_size'))
        self.btn_ver_consejos.bind(on_release=lambda *a: self.mostrar_consejos())
        self.tarjeta_consejo.add_widget(self.btn_ver_consejos)
        
        self.add_widget(self.tarjeta_consejo)
        self._redibujar_tarjeta_consejo(self.tarjeta_consejo)
        self.establecer_activo("inicio")
        
    def _redibujar_tarjeta_consejo(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            if tema.modo == 'oscuro':
                Color(0.10, 0.15, 0.24, 1)
                RoundedRectangle(pos=w.pos, size=w.size, radius=[12])
                Color(0.20, 0.28, 0.42, 1)
                Line(rounded_rectangle=(w.x, w.y, w.width, w.height, 12), width=1)
            else:
                Color(0.937, 0.965, 1.0, 1)
                RoundedRectangle(pos=w.pos, size=w.size, radius=[12])
                Color(*tema.borde)
                Line(rounded_rectangle=(w.x, w.y, w.width, w.height, 12), width=1)
                
    def establecer_activo(self, destino):
        for d, btn in self.botones_menu.items():
            btn.activo = (d == destino)
            
    def manejar_navegacion(self, destino):
        self.establecer_activo(destino)
        if self.al_navegar:
            self.al_navegar(destino)
            
    def mostrar_consejos(self):
        if self.al_mostrar_consejos:
            self.al_mostrar_consejos()
            
    def actualizar_tema(self, *args):
        self._actualizar_fondo()
        self.lbl_cents.color = tema.texto_principal
        self.lbl_sec.color = tema.texto_atenuado
        for btn in self.botones_menu.values():
            btn._actualizar_fondo()
        self._redibujar_tarjeta_consejo(self.tarjeta_consejo)
        self.ico_consejo.color = tema.primario
        self.tit_consejo.color = tema.primario
        self.txt_consejo.color = tema.texto_secundario
        self.btn_ver_consejos.color = tema.primario
