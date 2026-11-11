"""
CENTS - Pantallas de Autenticación
- PantallaLogin ("Bienvenido de nuevo")
- PantallaRegistro ("Crear una cuenta")
- PantallaRecuperarContrasena ("Recuperar contraseña")
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.checkbox import CheckBox
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse
from tema import tema
from estado_app import estado
from componentes.tarjetas import BotonPrimario, EntradaTexto, EntradaEstilizada

class BannerMarca(BoxLayout):
    """Banner visual lateral con logotipo CENTS y mensaje principal."""
    def __init__(self, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint=(0.42, 1),
            padding=[44, 48, 44, 48],
            spacing=20,
            **kwargs
        )
        self.bind(pos=self._actualizar_fondo, size=self._actualizar_fondo)
        self._construir_ui()
        
    def _actualizar_fondo(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.114, 0.306, 0.847, 1)  # #1D4ED8
            Rectangle(pos=self.pos, size=self.size)
            
            # Círculos decorativos financieros
            Color(0.18, 0.40, 0.95, 0.35)
            Ellipse(pos=(self.x - 60, self.y - 60), size=(self.width * 1.3, self.width * 1.3))
            
            Color(0.24, 0.48, 1.0, 0.25)
            Ellipse(pos=(self.x + 40, self.y + 30), size=(self.width * 0.9, self.width * 0.9))
            
            Color(0.30, 0.55, 1.0, 0.18)
            Ellipse(pos=(self.x - 20, self.y + self.height * 0.4), size=(self.width * 0.8, self.width * 0.8))
            
    def _construir_ui(self):
        # 1. Logotipo
        caja_logo = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=44)
        
        insignia = Widget(size_hint=(None, None), size=(36, 36), pos_hint={"center_y": 0.5})
        with insignia.canvas:
            Color(1, 1, 1, 0.22)
            RoundedRectangle(pos=insignia.pos, size=insignia.size, radius=[10])
        insignia.bind(pos=lambda w, *a: self._redibujar_insignia(w))
        
        lbl_c = Label(text="[b]C[/b]", markup=True, font_size="20sp", color=[1, 1, 1, 1], size_hint=(None, None), size=(36, 36), pos_hint={"center_y": 0.5})
        
        from kivy.uix.floatlayout import FloatLayout
        icono_fl = FloatLayout(size_hint=(None, None), size=(36, 36))
        icono_fl.add_widget(insignia)
        icono_fl.add_widget(lbl_c)
        caja_logo.add_widget(icono_fl)
        
        lbl_marca = Label(text="[b]CENTS[/b]", markup=True, font_size="22sp", color=[1, 1, 1, 1], halign="left", valign="middle")
        lbl_marca.bind(size=lbl_marca.setter('text_size'))
        caja_logo.add_widget(lbl_marca)
        self.add_widget(caja_logo)
        
        self.add_widget(Widget(size_hint_y=0.25))
        
        # 2. Título principal
        lbl_tit = Label(
            text="[b]Tus finanzas,\nmás claras y bajo control.[/b]",
            markup=True,
            font_size="32sp",
            line_height=1.2,
            color=[1, 1, 1, 1],
            size_hint_y=None,
            height=110,
            halign="left"
        )
        lbl_tit.bind(size=lbl_tit.setter('text_size'))
        self.add_widget(lbl_tit)
        
        # 3. Subtítulo
        lbl_sub = Label(
            text="Organiza tus gastos, crea presupuestos y\nalcanza tus metas con tranquilidad.",
            font_size="15sp",
            line_height=1.3,
            color=[0.90, 0.94, 1.0, 0.88],
            size_hint_y=None,
            height=60,
            halign="left"
        )
        lbl_sub.bind(size=lbl_sub.setter('text_size'))
        self.add_widget(lbl_sub)
        
        self.add_widget(Widget(size_hint_y=0.45))
        
    def _redibujar_insignia(self, w):
        w.canvas.clear()
        with w.canvas:
            Color(1, 1, 1, 0.22)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[10])

class PantallaLogin(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._construir_ui()
        
    def _construir_ui(self):
        raiz = BoxLayout(orientation="horizontal")
        raiz.add_widget(BannerMarca())
        
        panel_der = BoxLayout(
            orientation="vertical",
            size_hint=(0.58, 1),
            padding=[64, 48, 64, 48],
            spacing=16
        )
        with panel_der.canvas.before:
            Color(*tema.fondo_tarjeta)
            Rectangle(pos=panel_der.pos, size=panel_der.size)
        panel_der.bind(pos=lambda w, *a: self._redibujar_der(w), size=lambda w, *a: self._redibujar_der(w))
        tema.bind(modo=lambda *a: self._redibujar_der(panel_der))
        
        panel_der.add_widget(Widget(size_hint_y=0.15))
        
        encabezado = BoxLayout(orientation="vertical", spacing=4, size_hint_y=None, height=60)
        lbl_t = Label(text="[b]Bienvenido de nuevo[/b]", markup=True, font_size="26sp", color=tema.texto_principal, halign="left")
        lbl_t.bind(size=lbl_t.setter('text_size'))
        lbl_sub = Label(text="Ingresa a tu cuenta para continuar.", font_size="14sp", color=tema.texto_secundario, halign="left")
        lbl_sub.bind(size=lbl_sub.setter('text_size'))
        encabezado.add_widget(lbl_t)
        encabezado.add_widget(lbl_sub)
        panel_der.add_widget(encabezado)
        
        formulario = BoxLayout(orientation="vertical", spacing=14, size_hint_y=None, height=260)
        
        formulario.add_widget(self._crear_etiqueta("CORREO ELECTRÓNICO"))
        self.in_correo = EntradaTexto(hint_text="nombre@gmail.com")
        formulario.add_widget(self.in_correo)
        
        formulario.add_widget(self._crear_etiqueta("CONTRASEÑA"))
        self.in_clave = EntradaTexto(hint_text="Ingresa tu contraseña", password=True)
        formulario.add_widget(self.in_clave)
        
        btn_iniciar = BotonPrimario(text="Iniciar sesión", size_hint_y=None, height=44)
        btn_iniciar.bind(on_release=lambda *a: self.iniciar_sesion())
        formulario.add_widget(btn_iniciar)
        
        btn_olvido = Button(
            text="¿Olvidaste tu contraseña?",
            font_size="13sp",
            color=tema.primario,
            background_color=[0, 0, 0, 0],
            size_hint_y=None,
            height=28
        )
        btn_olvido.bind(on_release=lambda *a: self.ir_a("recuperar_contrasena"))
        formulario.add_widget(btn_olvido)
        panel_der.add_widget(formulario)
        
        pie = BoxLayout(orientation="horizontal", spacing=6, size_hint_y=None, height=36, pos_hint={"center_x": 0.5})
        lbl_no_cuenta = Label(text="¿Todavía no tienes una cuenta?", font_size="13sp", color=tema.texto_secundario, size_hint=(None, 1))
        lbl_no_cuenta.bind(texture_size=lambda *a: setattr(lbl_no_cuenta, 'width', lbl_no_cuenta.texture_size[0]))
        
        btn_registro = Button(
            text="[b]Crear una cuenta[/b]",
            markup=True,
            font_size="13sp",
            color=tema.primario,
            background_color=[0, 0, 0, 0],
            size_hint=(None, 1)
        )
        btn_registro.bind(texture_size=lambda *a: setattr(btn_registro, 'width', btn_registro.texture_size[0]))
        btn_registro.bind(on_release=lambda *a: self.ir_a("registro"))
        
        pie.add_widget(lbl_no_cuenta)
        pie.add_widget(btn_registro)
        panel_der.add_widget(pie)
        
        panel_der.add_widget(Widget(size_hint_y=0.2))
        raiz.add_widget(panel_der)
        self.add_widget(raiz)
        
    def _crear_etiqueta(self, texto):
        lbl = Label(text=texto, font_size="11sp", bold=True, color=tema.texto_atenuado, size_hint_y=None, height=18, halign="left")
        lbl.bind(size=lbl.setter('text_size'))
        return lbl
        
    def _redibujar_der(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.fondo_tarjeta)
            Rectangle(pos=w.pos, size=w.size)
            
    def iniciar_sesion(self):
        self.manager.current = "portal_principal"
        
    def ir_a(self, nombre_pantalla):
        self.manager.current = nombre_pantalla

class PantallaRegistro(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._construir_ui()
        
    def _construir_ui(self):
        raiz = BoxLayout(orientation="horizontal")
        raiz.add_widget(BannerMarca())
        
        panel_der = BoxLayout(
            orientation="vertical",
            size_hint=(0.58, 1),
            padding=[64, 32, 64, 32],
            spacing=12
        )
        with panel_der.canvas.before:
            Color(*tema.fondo_tarjeta)
            Rectangle(pos=panel_der.pos, size=panel_der.size)
        panel_der.bind(pos=lambda w, *a: self._redibujar_der(w), size=lambda w, *a: self._redibujar_der(w))
        tema.bind(modo=lambda *a: self._redibujar_der(panel_der))
        
        encabezado = BoxLayout(orientation="vertical", spacing=4, size_hint_y=None, height=54)
        lbl_t = Label(text="[b]Crear una cuenta[/b]", markup=True, font_size="26sp", color=tema.texto_principal, halign="left")
        lbl_t.bind(size=lbl_t.setter('text_size'))
        lbl_sub = Label(text="Regístrate para comenzar a organizar tu dinero.", font_size="13sp", color=tema.texto_secundario, halign="left")
        lbl_sub.bind(size=lbl_sub.setter('text_size'))
        encabezado.add_widget(lbl_t)
        encabezado.add_widget(lbl_sub)
        panel_der.add_widget(encabezado)
        
        desplazable = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        formulario = BoxLayout(orientation="vertical", spacing=10, size_hint_y=None)
        formulario.bind(minimum_height=formulario.setter('height'))
        
        # Nombre
        formulario.add_widget(self._crear_etiqueta("NOMBRE COMPLETO"))
        self.in_nombre = EntradaTexto(hint_text="Ingresa tu nombre completo")
        formulario.add_widget(self.in_nombre)
        
        # Correo
        formulario.add_widget(self._crear_etiqueta("CORREO ELECTRÓNICO"))
        self.in_correo = EntradaTexto(hint_text="nombre@correo.com")
        formulario.add_widget(self.in_correo)
        
        # Contraseña
        formulario.add_widget(self._crear_etiqueta("CONTRASEÑA"))
        self.in_clave = EntradaTexto(hint_text="Crea una contraseña", password=True)
        formulario.add_widget(self.in_clave)
        
        # Confirmar Contraseña
        formulario.add_widget(self._crear_etiqueta("CONFIRMAR CONTRASEÑA"))
        self.in_clave2 = EntradaTexto(hint_text="Repite tu contraseña", password=True)
        formulario.add_widget(self.in_clave2)
        
        # Checkbox términos
        fila_chk = BoxLayout(orientation="horizontal", spacing=8, size_hint_y=None, height=28)
        self.chk = CheckBox(active=True, size_hint=(None, None), size=(24, 24), color=tema.primario)
        lbl_term = Label(text="Acepto los términos y condiciones", font_size="12sp", color=tema.texto_secundario, halign="left")
        lbl_term.bind(size=lbl_term.setter('text_size'))
        fila_chk.add_widget(self.chk)
        fila_chk.add_widget(lbl_term)
        formulario.add_widget(fila_chk)
        
        btn_crear = BotonPrimario(text="Crear cuenta", size_hint_y=None, height=44)
        btn_crear.bind(on_release=lambda *a: self.registrar())
        formulario.add_widget(btn_crear)
        
        pie = BoxLayout(orientation="horizontal", spacing=6, size_hint_y=None, height=36, pos_hint={"center_x": 0.5})
        lbl_tiene = Label(text="¿Ya tienes una cuenta?", font_size="13sp", color=tema.texto_secundario, size_hint=(None, 1))
        lbl_tiene.bind(texture_size=lambda *a: setattr(lbl_tiene, 'width', lbl_tiene.texture_size[0]))
        
        btn_iniciar = Button(
            text="[b]Iniciar sesión[/b]",
            markup=True,
            font_size="13sp",
            color=tema.primario,
            background_color=[0, 0, 0, 0],
            size_hint=(None, 1)
        )
        btn_iniciar.bind(texture_size=lambda *a: setattr(btn_iniciar, 'width', btn_iniciar.texture_size[0]))
        btn_iniciar.bind(on_release=lambda *a: self.ir_a("login"))
        
        pie.add_widget(lbl_tiene)
        pie.add_widget(btn_iniciar)
        formulario.add_widget(pie)
        
        desplazable.add_widget(formulario)
        panel_der.add_widget(desplazable)
        raiz.add_widget(panel_der)
        self.add_widget(raiz)
        
    def _crear_etiqueta(self, texto):
        lbl = Label(text=texto, font_size="11sp", bold=True, color=tema.texto_atenuado, size_hint_y=None, height=18, halign="left")
        lbl.bind(size=lbl.setter('text_size'))
        return lbl
        
    def _redibujar_der(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.fondo_tarjeta)
            Rectangle(pos=w.pos, size=w.size)
            
    def registrar(self):
        self.manager.current = "portal_principal"
        
    def ir_a(self, nombre_pantalla):
        self.manager.current = nombre_pantalla

class PantallaRecuperarContrasena(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._construir_ui()
        
    def _construir_ui(self):
        raiz = BoxLayout(orientation="horizontal")
        raiz.add_widget(BannerMarca())
        
        panel_der = BoxLayout(
            orientation="vertical",
            size_hint=(0.58, 1),
            padding=[64, 48, 64, 48],
            spacing=16
        )
        with panel_der.canvas.before:
            Color(*tema.fondo_tarjeta)
            Rectangle(pos=panel_der.pos, size=panel_der.size)
        panel_der.bind(pos=lambda w, *a: self._redibujar_der(w), size=lambda w, *a: self._redibujar_der(w))
        tema.bind(modo=lambda *a: self._redibujar_der(panel_der))
        
        panel_der.add_widget(Widget(size_hint_y=0.15))
        
        # Icono sobre
        caja_icono = Widget(size_hint=(None, None), size=(48, 48), pos_hint={"center_x": 0.5})
        with caja_icono.canvas:
            Color(0.937, 0.965, 1.0, 1)
            RoundedRectangle(pos=caja_icono.pos, size=caja_icono.size, radius=[24])
        lbl_env = Label(text="✉", font_size="22sp", color=tema.primario, size_hint=(None, None), size=(48, 48), pos_hint={"center_x": 0.5})
        
        from kivy.uix.floatlayout import FloatLayout
        env_fl = FloatLayout(size_hint=(None, None), size=(48, 48), pos_hint={"center_x": 0.5})
        env_fl.add_widget(caja_icono)
        env_fl.add_widget(lbl_env)
        panel_der.add_widget(env_fl)
        
        encabezado = BoxLayout(orientation="vertical", spacing=4, size_hint_y=None, height=54)
        lbl_t = Label(text="[b]Recuperar contraseña[/b]", markup=True, font_size="24sp", color=tema.texto_principal, halign="center")
        lbl_t.bind(size=lbl_t.setter('text_size'))
        lbl_sub = Label(text="Te enviaremos un enlace para restablecer tu acceso.", font_size="13sp", color=tema.texto_secundario, halign="center")
        lbl_sub.bind(size=lbl_sub.setter('text_size'))
        encabezado.add_widget(lbl_t)
        encabezado.add_widget(lbl_sub)
        panel_der.add_widget(encabezado)
        
        formulario = BoxLayout(orientation="vertical", spacing=14, size_hint_y=None, height=200)
        
        formulario.add_widget(self._crear_etiqueta("CORREO ELECTRÓNICO"))
        self.in_correo = EntradaTexto(hint_text="nombre@gmail.com")
        formulario.add_widget(self.in_correo)
        
        btn_enviar = BotonPrimario(text="Enviar enlace de recuperación", size_hint_y=None, height=44)
        btn_enviar.bind(on_release=lambda *a: self.enviar())
        formulario.add_widget(btn_enviar)
        
        lbl_nota = Label(text="Revisa también tu carpeta de correo no deseado.", font_size="12sp", color=tema.texto_atenuado, halign="center")
        lbl_nota.bind(size=lbl_nota.setter('text_size'))
        formulario.add_widget(lbl_nota)
        panel_der.add_widget(formulario)
        
        btn_volver = Button(
            text="← Volver a iniciar sesión",
            font_size="13sp",
            bold=True,
            color=tema.primario,
            background_color=[0, 0, 0, 0],
            size_hint_y=None,
            height=36
        )
        btn_volver.bind(on_release=lambda *a: self.ir_a("login"))
        panel_der.add_widget(btn_volver)
        
        panel_der.add_widget(Widget(size_hint_y=0.25))
        raiz.add_widget(panel_der)
        self.add_widget(raiz)
        
    def _crear_etiqueta(self, texto):
        lbl = Label(text=texto, font_size="11sp", bold=True, color=tema.texto_atenuado, size_hint_y=None, height=18, halign="left")
        lbl.bind(size=lbl.setter('text_size'))
        return lbl
        
    def _redibujar_der(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.fondo_tarjeta)
            Rectangle(pos=w.pos, size=w.size)
            
    def enviar(self):
        self.ir_a("login")
        
    def ir_a(self, nombre_pantalla):
        self.manager.current = nombre_pantalla
