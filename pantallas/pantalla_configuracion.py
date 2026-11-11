"""
CENTS - Pantalla de Configuración
Pestañas de Mi Perfil, Preferencias, Moneda, Idioma y conmutador reactivo de Modo Claro y Oscuro.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.properties import BooleanProperty
from tema import tema
from estado_app import estado
from componentes.tarjetas import TarjetaBase, BotonPrimario, EntradaTexto, AvatarCircular, BotonPildora

class BotonSubPestana(ButtonBehavior, BoxLayout):
    es_activo = BooleanProperty(False)
    
    def __init__(self, titulo="", subtitulo="", activo=False, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint_y=None,
            height=54,
            padding=[16, 6, 12, 6],
            spacing=2,
            **kwargs
        )
        self.titulo_tab = titulo
        self.subtitulo_tab = subtitulo
        self.es_activo = activo
        
        self.lbl_t = Label(
            text=f"[b]{self.titulo_tab}[/b]",
            markup=True,
            font_size="13sp",
            color=tema.primario if self.es_activo else tema.texto_principal,
            halign="left"
        )
        self.lbl_t.bind(size=self.lbl_t.setter('text_size'))
        self.add_widget(self.lbl_t)
        
        self.lbl_s = Label(
            text=self.subtitulo_tab,
            font_size="11sp",
            color=tema.texto_atenuado,
            halign="left"
        )
        self.lbl_s.bind(size=self.lbl_s.setter('text_size'))
        self.add_widget(self.lbl_s)
        
        self.bind(pos=self._actualizar_fondo, size=self._actualizar_fondo, state=self._actualizar_fondo, es_activo=self._actualizar_fondo)
        tema.bind(modo=self._actualizar_fondo)
        self._actualizar_fondo()
        
    def _actualizar_fondo(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.es_activo:
                Color(*tema.fondo_resaltado)
                RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
                Color(*tema.primario)
                RoundedRectangle(pos=(self.x, self.y + 6), size=(4, self.height - 12), radius=[2])
                self.lbl_t.color = tema.primario
            else:
                if self.state == 'down':
                    Color(*tema.fondo_sutil)
                    RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
                else:
                    Color(0, 0, 0, 0)
                    RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
                self.lbl_t.color = tema.texto_principal
        self.lbl_s.color = tema.texto_atenuado

    def actualizar_tema(self):
        self._actualizar_fondo()

class VistaConfiguracion(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(do_scroll_x=False, **kwargs)
        self.moneda_seleccionada = "USD ($)"
        self.idioma_seleccionado = "Español (ES)"
        self.tema_seleccionado = "☀ Claro" if tema.modo == "claro" else "☾ Oscuro"
        self.etiquetas_campo = []
        self._construir_ui()
        
    def _construir_ui(self):
        raiz = BoxLayout(
            orientation="horizontal",
            spacing=20,
            padding=[24, 20, 24, 24],
            size_hint_y=None
        )
        raiz.bind(minimum_height=raiz.setter('height'))
        
        # 1. Pestañas de subnavegación izquierda
        tarjeta_sub = TarjetaBase(orientation="vertical", padding=[12, 12, 12, 12], spacing=4, size_hint=(None, None), width=230)
        tarjeta_sub.bind(minimum_height=tarjeta_sub.setter('height'))
        
        pestanas = [
            ("Mi perfil", "Datos personales", True),
            ("Preferencias", "Idioma y apariencia", False),
            ("Notificaciones", "Alertas y recordatorios", False),
            ("Seguridad", "Contraseña y acceso", False),
            ("Privacidad", "Datos y permisos", False),
        ]
        
        self.botones_subpestanas = []
        for t, s, act in pestanas:
            btn = BotonSubPestana(titulo=t, subtitulo=s, activo=act)
            btn.bind(on_release=lambda b, tit=t: self._seleccionar_subpestana(tit))
            self.botones_subpestanas.append(btn)
            tarjeta_sub.add_widget(btn)
            
        raiz.add_widget(tarjeta_sub)
        
        # 2. Contenido Derecho
        contenido_der = BoxLayout(orientation="vertical", spacing=18, size_hint_x=1, size_hint_y=None)
        contenido_der.bind(minimum_height=contenido_der.setter('height'))
        
        # Tarjeta 1: Información del perfil
        self.tarjeta1 = TarjetaBase(orientation="vertical", padding=[24, 20, 24, 20], spacing=16, size_hint_y=None)
        self.tarjeta1.bind(minimum_height=self.tarjeta1.setter('height'))
        
        c1_enc = BoxLayout(orientation="vertical", spacing=2, size_hint_y=None, height=40)
        self.lbl_c1_t = Label(text="[b]Información del perfil[/b]", markup=True, font_size="16sp", color=tema.texto_principal, halign="left")
        self.lbl_c1_t.bind(size=self.lbl_c1_t.setter('text_size'))
        self.lbl_c1_s = Label(text="Actualiza los datos asociados a tu cuenta.", font_size="12sp", color=tema.texto_atenuado, halign="left")
        self.lbl_c1_s.bind(size=self.lbl_c1_s.setter('text_size'))
        c1_enc.add_widget(self.lbl_c1_t)
        c1_enc.add_widget(self.lbl_c1_s)
        self.tarjeta1.add_widget(c1_enc)
        
        # Foto de perfil con AvatarCircular centrado
        self.lbl_fp = Label(text="Foto de perfil", font_size="11sp", bold=True, color=tema.texto_atenuado, size_hint_y=None, height=18, halign="left")
        self.lbl_fp.bind(size=self.lbl_fp.setter('text_size'))
        self.tarjeta1.add_widget(self.lbl_fp)
        
        fila_foto = BoxLayout(orientation="horizontal", spacing=14, size_hint_y=None, height=54)
        
        # Avatar sin desplazamientos a 0, 0
        self.avatar_foto = AvatarCircular(
            texto="SG",
            diametro=48,
            color_fondo=[0.25, 0.45, 0.90, 1],
            pos_hint={"center_y": 0.5}
        )
        fila_foto.add_widget(self.avatar_foto)
        
        self.btn_chg = Button(
            text="Cambiar foto",
            font_size="12sp",
            bold=True,
            color=tema.primario,
            background_normal="",
            background_down="",
            background_color=[0, 0, 0, 0],
            size_hint=(None, None),
            size=(110, 36),
            pos_hint={"center_y": 0.5}
        )
        self.btn_chg.bind(pos=lambda w, *a: self._redibujar_btn_contorno(w), size=lambda w, *a: self._redibujar_btn_contorno(w), state=lambda w, *a: self._redibujar_btn_contorno(w))
        fila_foto.add_widget(self.btn_chg)
        
        self.lbl_tam = Label(text="PNG o JPG máximo 5 MB", font_size="11sp", color=tema.texto_atenuado, size_hint_x=1, halign="left")
        self.lbl_tam.bind(size=self.lbl_tam.setter('text_size'))
        fila_foto.add_widget(self.lbl_tam)
        self.tarjeta1.add_widget(fila_foto)
        
        # Nombre y Correo interactivos
        fila_campos = BoxLayout(orientation="horizontal", spacing=16, size_hint_y=None, height=64)
        
        col_nc = BoxLayout(orientation="vertical", spacing=4)
        col_nc.add_widget(self._crear_etiqueta("NOMBRE COMPLETO"))
        self.in_nombre = EntradaTexto(text=estado.usuario_actual.get("primer_nombre", "Steven") + " " + estado.usuario_actual.get("apellido", "Guarnizo"))
        col_nc.add_widget(self.in_nombre)
        fila_campos.add_widget(col_nc)
        
        col_em = BoxLayout(orientation="vertical", spacing=4)
        col_em.add_widget(self._crear_etiqueta("CORREO ELECTRÓNICO"))
        self.in_correo = EntradaTexto(text=estado.usuario_actual.get("correo", "nombre@gmail.com"))
        col_em.add_widget(self.in_correo)
        fila_campos.add_widget(col_em)
        self.tarjeta1.add_widget(fila_campos)
        
        # Moneda e Idioma con BotonPildora
        fila_pildoras = BoxLayout(orientation="horizontal", spacing=16, size_hint_y=None, height=66)
        
        col_mon = BoxLayout(orientation="vertical", spacing=6)
        col_mon.add_widget(self._crear_etiqueta("MONEDA"))
        fila_mon_btn = BoxLayout(orientation="horizontal", spacing=8)
        self.botones_mon = []
        for m in ["USD ($)", "EUR (€)", "MXN (Peso)"]:
            b = BotonPildora(texto=m, activo=(m == self.moneda_seleccionada))
            b.bind(on_release=lambda btn, cur=m: self._seleccionar_moneda(cur))
            self.botones_mon.append((b, m))
            fila_mon_btn.add_widget(b)
        col_mon.add_widget(fila_mon_btn)
        fila_pildoras.add_widget(col_mon)
        
        col_idm = BoxLayout(orientation="vertical", spacing=6)
        col_idm.add_widget(self._crear_etiqueta("IDIOMA"))
        fila_idm_btn = BoxLayout(orientation="horizontal", spacing=8)
        self.botones_idm = []
        for l in ["Español (ES)", "English (EN)", "Português (PT)"]:
            b = BotonPildora(texto=l, activo=(l == self.idioma_seleccionado))
            b.bind(on_release=lambda btn, lng=l: self._seleccionar_idioma(lng))
            self.botones_idm.append((b, l))
            fila_idm_btn.add_widget(b)
        col_idm.add_widget(fila_idm_btn)
        fila_pildoras.add_widget(col_idm)
        
        self.tarjeta1.add_widget(fila_pildoras)
        contenido_der.add_widget(self.tarjeta1)
        
        # Tarjeta 2: Apariencia (Modo Claro y Oscuro)
        self.tarjeta2 = TarjetaBase(orientation="vertical", padding=[24, 20, 24, 20], spacing=14, size_hint_y=None, height=136)
        c2_enc = BoxLayout(orientation="vertical", spacing=2, size_hint_y=None, height=36)
        self.lbl_c2_t = Label(text="[b]Apariencia[/b]", markup=True, font_size="16sp", color=tema.texto_principal, halign="left")
        self.lbl_c2_t.bind(size=self.lbl_c2_t.setter('text_size'))
        self.lbl_c2_s = Label(text="Selecciona cómo quieres ver la aplicación.", font_size="12sp", color=tema.texto_atenuado, halign="left")
        self.lbl_c2_s.bind(size=self.lbl_c2_s.setter('text_size'))
        c2_enc.add_widget(self.lbl_c2_t)
        c2_enc.add_widget(self.lbl_c2_s)
        self.tarjeta2.add_widget(c2_enc)
        
        fila_tema = BoxLayout(orientation="horizontal", spacing=12, size_hint_y=None, height=40)
        self.botones_tema = []
        for opt in ["☀ Claro", "☾ Oscuro", "◐ Sistema"]:
            b = BotonPildora(texto=opt, activo=(opt == self.tema_seleccionado), size_hint_x=0.33)
            b.bind(on_release=lambda btn, t=opt: self._seleccionar_tema(t))
            self.botones_tema.append((b, opt))
            fila_tema.add_widget(b)
        self.tarjeta2.add_widget(fila_tema)
        contenido_der.add_widget(self.tarjeta2)
        
        # Botón Guardar
        self.btn_guardar = BotonPrimario(text="Guardar cambios", size_hint=(None, None), size=(160, 44))
        self.btn_guardar.bind(on_release=lambda *a: self.guardar())
        contenido_der.add_widget(self.btn_guardar)
        
        raiz.add_widget(contenido_der)
        self.add_widget(raiz)
        
    def _crear_etiqueta(self, texto):
        lbl = Label(text=texto, font_size="11sp", bold=True, color=tema.texto_atenuado, size_hint_y=None, height=18, halign="left")
        lbl.bind(size=lbl.setter('text_size'))
        self.etiquetas_campo.append(lbl)
        return lbl
        
    def _seleccionar_subpestana(self, titulo):
        for btn in self.botones_subpestanas:
            btn.es_activo = (btn.titulo_tab == titulo)
            
    def _redibujar_btn_contorno(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            if w.state == 'down':
                Color(*tema.fondo_sutil)
            else:
                Color(0, 0, 0, 0)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[8])
            Color(*tema.borde)
            Line(rounded_rectangle=(w.x, w.y, w.width, w.height, 8), width=1)
            
    def _seleccionar_moneda(self, moneda):
        self.moneda_seleccionada = moneda
        for b, m in self.botones_mon:
            b.activo = (m == moneda)
            
    def _seleccionar_idioma(self, idioma):
        self.idioma_seleccionado = idioma
        for b, l in self.botones_idm:
            b.activo = (l == idioma)
            
    def _seleccionar_tema(self, opcion_tema):
        self.tema_seleccionado = opcion_tema
        
        # 1. Aplicar cambio de tema global
        if "oscuro" in opcion_tema.lower():
            tema.cambiar_tema("oscuro")
            estado.cambiar_tema("oscuro")
        else:
            tema.cambiar_tema("claro")
            estado.cambiar_tema("claro")
            
        # 2. Actualizar estado activo de las píldoras de tema
        for b, t in self.botones_tema:
            b.activo = (t == opcion_tema)
            
    def actualizar_tema(self, *args):
        self.tema_seleccionado = "☾ Oscuro" if tema.modo == "oscuro" else "☀ Claro"
        for b in self.botones_subpestanas:
            b.actualizar_tema()
        self.lbl_c1_t.color = tema.texto_principal
        self.lbl_c1_s.color = tema.texto_atenuado
        self.lbl_fp.color = tema.texto_atenuado
        self._redibujar_btn_contorno(self.btn_chg)
        self.btn_chg.color = tema.primario
        self.lbl_tam.color = tema.texto_atenuado
        for lbl in self.etiquetas_campo:
            lbl.color = tema.texto_atenuado
        self.in_nombre._al_cambiar_tema()
        self.in_correo._al_cambiar_tema()
        for b, m in self.botones_mon:
            b.activo = (m == self.moneda_seleccionada)
            b._actualizar_fondo()
        for b, l in self.botones_idm:
            b.activo = (l == self.idioma_seleccionado)
            b._actualizar_fondo()
        self.lbl_c2_t.color = tema.texto_principal
        self.lbl_c2_s.color = tema.texto_atenuado
        for b, t in self.botones_tema:
            b.activo = (t == self.tema_seleccionado)
            b._actualizar_fondo()
        self.btn_guardar._actualizar_fondo()
        
    def guardar(self):
        nombre_completo = self.in_nombre.text.strip() or "Steven Guarnizo"
        partes = nombre_completo.split(" ", 1)
        p_nombre = partes[0]
        p_apellido = partes[1] if len(partes) > 1 else ""
        
        estado.actualizar_perfil(
            nombre=nombre_completo,
            correo=self.in_correo.text.strip() or "nombre@gmail.com",
            telefono=estado.usuario_actual.get("telefono", "+593 99 000 0000")
        )
        estado.usuario_actual["primer_nombre"] = p_nombre
        estado.usuario_actual["apellido"] = p_apellido
        estado.usuario_actual["moneda"] = self.moneda_seleccionada
        estado.usuario_actual["idioma"] = self.idioma_seleccionado
        iniciales = (p_nombre[0] if p_nombre else "U") + (p_apellido[0] if p_apellido else "")
        estado.usuario_actual["iniciales"] = iniciales.upper()
        self.avatar_foto.establecer_texto(iniciales.upper())
