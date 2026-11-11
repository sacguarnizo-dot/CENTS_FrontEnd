"""
CENTS - Pantallas de Perfil y Seguridad
- VistaMiPerfil ("Mi perfil")
- VistaEditarPerfil ("Editar perfil")
- VistaCambiarContrasena ("Cambiar contraseña")
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.properties import ObjectProperty
from kivymd.icon_definitions import md_icons
from tema import tema
from estado_app import estado
from componentes.tarjetas import TarjetaBase, BotonPrimario, EntradaTexto, AvatarCircular

class VistaMiPerfil(ScrollView):
    al_editar = ObjectProperty(None)
    al_cambiar_clave = ObjectProperty(None)
    al_cerrar_sesion = ObjectProperty(None)
    al_volver = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(do_scroll_x=False, **kwargs)
        self.etiquetas_campo = []
        self._construir_ui()
        estado.bind(usuario_actual=self.refrescar_perfil)
        
    def _construir_ui(self):
        contenedor = BoxLayout(
            orientation="vertical",
            spacing=18,
            padding=[24, 20, 24, 24],
            size_hint_y=None
        )
        contenedor.bind(minimum_height=contenedor.setter('height'))
        
        self.lbl_sub = Label(text="Consulta y administra la información de tu cuenta.", font_size="13sp", color=tema.texto_secundario, size_hint_y=None, height=20, halign="left")
        self.lbl_sub.bind(size=self.lbl_sub.setter('text_size'))
        contenedor.add_widget(self.lbl_sub)
        
        # 1. Tarjeta Avatar con AvatarCircular
        self.tarjeta_av = TarjetaBase(orientation="horizontal", padding=[20, 16, 20, 16], spacing=16, size_hint_y=None, height=84)
        
        self.avatar = AvatarCircular(
            texto=estado.usuario_actual.get('iniciales', 'SG')[:2],
            diametro=52,
            pos_hint={"center_y": 0.5}
        )
        self.tarjeta_av.add_widget(self.avatar)
        
        info_u = BoxLayout(orientation="vertical", spacing=2, pos_hint={"center_y": 0.5})
        self.lbl_tarjeta_nom = Label(text=f"[b]{estado.usuario_actual['nombre']}[/b]", markup=True, font_size="16sp", color=tema.texto_principal, halign="left")
        self.lbl_tarjeta_nom.bind(size=self.lbl_tarjeta_nom.setter('text_size'))
        self.lbl_tarjeta_correo = Label(text=estado.usuario_actual['correo'], font_size="13sp", color=tema.texto_secundario, halign="left")
        self.lbl_tarjeta_correo.bind(size=self.lbl_tarjeta_correo.setter('text_size'))
        info_u.add_widget(self.lbl_tarjeta_nom)
        info_u.add_widget(self.lbl_tarjeta_correo)
        self.tarjeta_av.add_widget(info_u)
        
        self.btn_cambiar_foto = Button(
            text="Cambiar foto",
            font_size="13sp",
            bold=True,
            color=tema.primario,
            background_normal="",
            background_down="",
            background_color=[0, 0, 0, 0],
            size_hint=(None, None),
            size=(110, 36),
            pos_hint={"center_y": 0.5}
        )
        self.btn_cambiar_foto.bind(pos=lambda w, *a: self._redibujar_btn_contorno(w), size=lambda w, *a: self._redibujar_btn_contorno(w), state=lambda w, *a: self._redibujar_btn_contorno(w))
        self.tarjeta_av.add_widget(self.btn_cambiar_foto)
        contenedor.add_widget(self.tarjeta_av)
        
        # 2. Tarjeta: Información personal
        self.tarjeta_p = TarjetaBase(orientation="vertical", padding=[20, 18, 20, 18], spacing=14, size_hint_y=None, height=170)
        self.lbl_p_tit = Label(text="[b]Información personal[/b]", markup=True, font_size="15sp", color=tema.texto_principal, size_hint_y=None, height=22, halign="left")
        self.lbl_p_tit.bind(size=self.lbl_p_tit.setter('text_size'))
        self.tarjeta_p.add_widget(self.lbl_p_tit)
        
        grid_p = GridLayout(cols=2, spacing=16, size_hint_y=None, height=100)
        self.val_p_nom = self._crear_campo_dato("NOMBRE COMPLETO", estado.usuario_actual["nombre"], grid_p)
        self.val_p_tel = self._crear_campo_dato("TELÉFONO", estado.usuario_actual["telefono"], grid_p)
        self.val_p_cor = self._crear_campo_dato("CORREO ELECTRÓNICO", estado.usuario_actual["correo"], grid_p)
        self.val_p_tip = self._crear_campo_dato("TIPO DE CUENTA", estado.usuario_actual["tipo_cuenta"], grid_p)
        self.tarjeta_p.add_widget(grid_p)
        contenedor.add_widget(self.tarjeta_p)
        
        # 3. Tarjeta: Datos de la cuenta
        self.tarjeta_d = TarjetaBase(orientation="vertical", padding=[20, 18, 20, 18], spacing=14, size_hint_y=None, height=180)
        self.lbl_d_tit = Label(text="[b]Datos de la cuenta[/b]", markup=True, font_size="15sp", color=tema.texto_principal, size_hint_y=None, height=22, halign="left")
        self.lbl_d_tit.bind(size=self.lbl_d_tit.setter('text_size'))
        self.tarjeta_d.add_widget(self.lbl_d_tit)
        
        grid_d = GridLayout(cols=2, spacing=16, size_hint_y=None, height=90)
        self.val_d_id = self._crear_campo_dato("ID DE USUARIO", estado.usuario_actual["id"], grid_d)
        self.val_d_fec = self._crear_campo_dato("FECHA DE REGISTRO", estado.usuario_actual["fecha_registro"], grid_d)
        self.val_d_mon = self._crear_campo_dato("MONEDA PRINCIPAL", f"{estado.usuario_actual['moneda']} Dólar estadounidense", grid_d)
        self.val_d_not = self._crear_campo_dato("NOTA", "Tu información se utiliza para personalizar tu experiencia.", grid_d)
        self.tarjeta_d.add_widget(grid_d)
        contenedor.add_widget(self.tarjeta_d)
        
        # 4. Tarjeta: Seguridad
        self.tarjeta_s = TarjetaBase(orientation="vertical", padding=[20, 18, 20, 18], spacing=10, size_hint_y=None, height=120)
        self.lbl_s_tit = Label(text="[b]Seguridad[/b]", markup=True, font_size="15sp", color=tema.texto_principal, size_hint_y=None, height=22, halign="left")
        self.lbl_s_tit.bind(size=self.lbl_s_tit.setter('text_size'))
        self.tarjeta_s.add_widget(self.lbl_s_tit)
        
        fila_s = BoxLayout(orientation="horizontal", size_hint_y=None, height=36)
        self.lbl_s_info = Label(text="Contraseña\n[size=11][color=#94A3B8]Última actualización: hace 30 días[/color][/size]", markup=True, font_size="13sp", color=tema.texto_principal, halign="left")
        self.lbl_s_info.bind(size=self.lbl_s_info.setter('text_size'))
        fila_s.add_widget(self.lbl_s_info)
        
        self.btn_chg_s = Button(
            text="Cambiar contraseña",
            font_size="13sp",
            bold=True,
            color=tema.primario,
            background_normal="",
            background_down="",
            background_color=[0, 0, 0, 0],
            size_hint=(None, 1),
            width=160
        )
        self.btn_chg_s.bind(pos=lambda w, *a: self._redibujar_btn_contorno(w), size=lambda w, *a: self._redibujar_btn_contorno(w), state=lambda w, *a: self._redibujar_btn_contorno(w))
        self.btn_chg_s.bind(on_release=lambda *a: self.ir_cambiar_clave())
        fila_s.add_widget(self.btn_chg_s)
        self.tarjeta_s.add_widget(fila_s)
        contenedor.add_widget(self.tarjeta_s)
        
        # 5. Fila de Acciones: Cerrar sesión, Regresar, Editar perfil
        fila_acciones = BoxLayout(orientation="horizontal", spacing=14, size_hint_y=None, height=44)
        
        self.btn_salir = Button(
            text="Cerrar sesión",
            font_size="13sp",
            bold=True,
            color=tema.peligro,
            background_normal="",
            background_down="",
            background_color=[0, 0, 0, 0],
            size_hint=(None, 1),
            width=130
        )
        self.btn_salir.bind(pos=lambda w, *a: self._redibujar_btn_peligro(w), size=lambda w, *a: self._redibujar_btn_peligro(w), state=lambda w, *a: self._redibujar_btn_peligro(w))
        self.btn_salir.bind(on_release=lambda *a: self.cerrar_sesion())
        fila_acciones.add_widget(self.btn_salir)
        
        fila_acciones.add_widget(Widget())
        
        self.btn_regresar = Button(
            text="Regresar",
            font_size="13sp",
            bold=True,
            color=tema.texto_secundario,
            background_normal="",
            background_down="",
            background_color=[0, 0, 0, 0],
            size_hint=(None, 1),
            width=120
        )
        self.btn_regresar.bind(pos=lambda w, *a: self._redibujar_btn_contorno(w), size=lambda w, *a: self._redibujar_btn_contorno(w), state=lambda w, *a: self._redibujar_btn_contorno(w))
        self.btn_regresar.bind(on_release=lambda *a: self.volver())
        fila_acciones.add_widget(self.btn_regresar)
        
        self.btn_editar = BotonPrimario(text="Editar perfil", size_hint=(None, 1), width=140)
        self.btn_editar.bind(on_release=lambda *a: self.ir_editar_perfil())
        fila_acciones.add_widget(self.btn_editar)
        
        contenedor.add_widget(fila_acciones)
        self.add_widget(contenedor)
        
    def _crear_campo_dato(self, etiqueta, valor, padre):
        col = BoxLayout(orientation="vertical", spacing=2)
        lbl_k = Label(text=etiqueta, font_size="11sp", bold=True, color=tema.texto_atenuado, halign="left")
        lbl_k.bind(size=lbl_k.setter('text_size'))
        lbl_v = Label(text=valor, font_size="13sp", color=tema.texto_principal, halign="left")
        lbl_v.bind(size=lbl_v.setter('text_size'))
        self.etiquetas_campo.append((lbl_k, lbl_v))
        col.add_widget(lbl_k)
        col.add_widget(lbl_v)
        padre.add_widget(col)
        return lbl_v
        
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
            
    def _redibujar_btn_peligro(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            if w.state == 'down':
                Color(0.9, 0.2, 0.2, 0.15)
            else:
                Color(0, 0, 0, 0)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[8])
            Color(*tema.peligro)
            Line(rounded_rectangle=(w.x, w.y, w.width, w.height, 8), width=1)
            
    def ir_editar_perfil(self):
        if self.al_editar:
            self.al_editar()
            
    def ir_cambiar_clave(self):
        if self.al_cambiar_clave:
            self.al_cambiar_clave()
            
    def cerrar_sesion(self):
        if self.al_cerrar_sesion:
            self.al_cerrar_sesion()
            
    def volver(self):
        if self.al_volver:
            self.al_volver()
            
    def refrescar_perfil(self, *args):
        u = estado.usuario_actual
        self.lbl_tarjeta_nom.text = f"[b]{u['nombre']}[/b]"
        self.lbl_tarjeta_correo.text = u['correo']
        self.val_p_nom.text = u['nombre']
        self.val_p_tel.text = u['telefono']
        self.val_p_cor.text = u['correo']
        self.val_p_tip.text = u['tipo_cuenta']
        self.val_d_id.text = u['id']
        self.val_d_fec.text = u['fecha_registro']
        self.val_d_mon.text = f"{u['moneda']} Dólar estadounidense"
        self.avatar.establecer_texto(u.get('iniciales', 'SG')[:2])
        
    def actualizar_tema(self, *args):
        self.lbl_sub.color = tema.texto_secundario
        self.lbl_tarjeta_nom.color = tema.texto_principal
        self.lbl_tarjeta_correo.color = tema.texto_secundario
        self._redibujar_btn_contorno(self.btn_cambiar_foto)
        self.btn_cambiar_foto.color = tema.primario
        self.lbl_p_tit.color = tema.texto_principal
        self.lbl_d_tit.color = tema.texto_principal
        self.lbl_s_tit.color = tema.texto_principal
        self.lbl_s_info.color = tema.texto_principal
        self._redibujar_btn_contorno(self.btn_chg_s)
        self.btn_chg_s.color = tema.primario
        self._redibujar_btn_peligro(self.btn_salir)
        self._redibujar_btn_contorno(self.btn_regresar)
        self.btn_regresar.color = tema.texto_secundario
        self.btn_editar._actualizar_fondo()
        for lbl_k, lbl_v in self.etiquetas_campo:
            lbl_k.color = tema.texto_atenuado
            lbl_v.color = tema.texto_principal


class VistaEditarPerfil(ScrollView):
    al_guardar = ObjectProperty(None)
    al_cancelar = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(do_scroll_x=False, **kwargs)
        self.etiquetas_input = []
        self._construir_ui()
        
    def _construir_ui(self):
        contenedor = BoxLayout(
            orientation="vertical",
            spacing=18,
            padding=[24, 20, 24, 24],
            size_hint_y=None
        )
        contenedor.bind(minimum_height=contenedor.setter('height'))
        
        self.lbl_sub = Label(text="Actualiza tu información personal.", font_size="13sp", color=tema.texto_secundario, size_hint_y=None, height=20, halign="left")
        self.lbl_sub.bind(size=self.lbl_sub.setter('text_size'))
        contenedor.add_widget(self.lbl_sub)
        
        tarjeta = TarjetaBase(orientation="vertical", padding=[24, 24, 24, 24], spacing=16, size_hint_y=None)
        tarjeta.bind(minimum_height=tarjeta.setter('height'))
        
        self.lbl_foto_tit = Label(text="Fotografía de perfil", font_size="12sp", bold=True, color=tema.texto_atenuado, size_hint_y=None, height=18, halign="left")
        self.lbl_foto_tit.bind(size=self.lbl_foto_tit.setter('text_size'))
        tarjeta.add_widget(self.lbl_foto_tit)
        
        fila_foto = BoxLayout(orientation="horizontal", spacing=14, size_hint_y=None, height=54)
        self.avatar_ed = AvatarCircular(texto="SG", diametro=48, color_fondo=[0.25, 0.45, 0.90, 1], pos_hint={"center_y": 0.5})
        fila_foto.add_widget(self.avatar_ed)
        
        self.btn_foto = Button(
            text="Cambiar fotografía",
            font_size="13sp",
            bold=True,
            color=tema.primario,
            background_normal="",
            background_down="",
            background_color=[0, 0, 0, 0],
            size_hint=(None, None),
            size=(150, 36),
            pos_hint={"center_y": 0.5}
        )
        self.btn_foto.bind(pos=lambda w, *a: self._redibujar_btn_contorno(w), size=lambda w, *a: self._redibujar_btn_contorno(w), state=lambda w, *a: self._redibujar_btn_contorno(w))
        fila_foto.add_widget(self.btn_foto)
        tarjeta.add_widget(fila_foto)
        
        # Campos de texto interactivos
        grid = GridLayout(cols=2, spacing=16, size_hint_y=None, height=140)
        
        col_n = BoxLayout(orientation="vertical", spacing=4)
        col_n.add_widget(self._crear_etiqueta("NOMBRE"))
        self.in_nombre = EntradaTexto(text=estado.usuario_actual["primer_nombre"])
        col_n.add_widget(self.in_nombre)
        grid.add_widget(col_n)
        
        col_a = BoxLayout(orientation="vertical", spacing=4)
        col_a.add_widget(self._crear_etiqueta("APELLIDO"))
        self.in_apellido = EntradaTexto(text=estado.usuario_actual["apellido"])
        col_a.add_widget(self.in_apellido)
        grid.add_widget(col_a)
        
        col_c = BoxLayout(orientation="vertical", spacing=4)
        col_c.add_widget(self._crear_etiqueta("CORREO ELECTRÓNICO"))
        self.in_correo = EntradaTexto(text=estado.usuario_actual["correo"])
        col_c.add_widget(self.in_correo)
        grid.add_widget(col_c)
        
        col_t = BoxLayout(orientation="vertical", spacing=4)
        col_t.add_widget(self._crear_etiqueta("TELÉFONO"))
        self.in_telefono = EntradaTexto(text=estado.usuario_actual["telefono"])
        col_t.add_widget(self.in_telefono)
        grid.add_widget(col_t)
        
        tarjeta.add_widget(grid)
        
        # Botones de Guardar / Cancelar
        fila_btn = BoxLayout(orientation="horizontal", spacing=12, size_hint_y=None, height=44)
        fila_btn.add_widget(Widget())
        
        self.btn_cancelar = Button(
            text="Cancelar",
            font_size="13sp",
            bold=True,
            color=tema.texto_secundario,
            background_normal="",
            background_down="",
            background_color=[0, 0, 0, 0],
            size_hint=(None, 1),
            width=110
        )
        self.btn_cancelar.bind(pos=lambda w, *a: self._redibujar_btn_contorno(w), size=lambda w, *a: self._redibujar_btn_contorno(w), state=lambda w, *a: self._redibujar_btn_contorno(w))
        self.btn_cancelar.bind(on_release=lambda *a: self.cancelar())
        fila_btn.add_widget(self.btn_cancelar)
        
        self.btn_guardar = BotonPrimario(text="Guardar cambios", size_hint=(None, 1), width=160)
        self.btn_guardar.bind(on_release=lambda *a: self.guardar())
        fila_btn.add_widget(self.btn_guardar)
        
        tarjeta.add_widget(fila_btn)
        contenedor.add_widget(tarjeta)
        self.add_widget(contenedor)
        
    def _crear_etiqueta(self, texto):
        lbl = Label(text=texto, font_size="11sp", bold=True, color=tema.texto_atenuado, size_hint_y=None, height=18, halign="left")
        lbl.bind(size=lbl.setter('text_size'))
        self.etiquetas_input.append(lbl)
        return lbl
        
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
            
    def cancelar(self):
        if self.al_cancelar:
            self.al_cancelar()
            
    def guardar(self):
        p_nom = self.in_nombre.text.strip()
        p_ape = self.in_apellido.text.strip()
        nom_comp = f"{p_nom} {p_ape}".strip()
        cor = self.in_correo.text.strip()
        tel = self.in_telefono.text.strip()
        
        estado.actualizar_perfil(nom_comp, cor, tel)
        estado.usuario_actual["primer_nombre"] = p_nom
        estado.usuario_actual["apellido"] = p_ape
        ini = (p_nom[0] if p_nom else "") + (p_ape[0] if p_ape else "")
        estado.usuario_actual["iniciales"] = ini.upper() if ini else "U"
        
        if self.al_guardar:
            self.al_guardar()
            
    def actualizar_tema(self, *args):
        self.lbl_sub.color = tema.texto_secundario
        self.lbl_foto_tit.color = tema.texto_atenuado
        self._redibujar_btn_contorno(self.btn_foto)
        self.btn_foto.color = tema.primario
        for lbl in self.etiquetas_input:
            lbl.color = tema.texto_atenuado
        self.in_nombre._al_cambiar_tema()
        self.in_apellido._al_cambiar_tema()
        self.in_correo._al_cambiar_tema()
        self.in_telefono._al_cambiar_tema()
        self._redibujar_btn_contorno(self.btn_cancelar)
        self.btn_cancelar.color = tema.texto_secundario
        self.btn_guardar._actualizar_fondo()


class VistaCambiarContrasena(ScrollView):
    al_actualizar = ObjectProperty(None)
    al_cancelar = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(do_scroll_x=False, **kwargs)
        self.etiquetas_input = []
        self._construir_ui()
        
    def _construir_ui(self):
        contenedor = BoxLayout(
            orientation="vertical",
            spacing=18,
            padding=[24, 20, 24, 24],
            size_hint_y=None
        )
        contenedor.bind(minimum_height=contenedor.setter('height'))
        
        self.lbl_sub = Label(text="Actualiza tu contraseña para mantener protegida tu cuenta.", font_size="13sp", color=tema.texto_secundario, size_hint_y=None, height=20, halign="left")
        self.lbl_sub.bind(size=self.lbl_sub.setter('text_size'))
        contenedor.add_widget(self.lbl_sub)
        
        tarjeta = TarjetaBase(orientation="vertical", padding=[32, 28, 32, 28], spacing=16, size_hint=(None, None), width=480, pos_hint={"center_x": 0.5})
        tarjeta.bind(minimum_height=tarjeta.setter('height'))
        
        # Icono de candado centrado sin FloatLayout
        self.caja_icono = BoxLayout(
            orientation="vertical",
            size_hint=(None, None),
            size=(52, 52),
            pos_hint={"center_x": 0.5}
        )
        self.caja_icono.bind(pos=lambda w, *a: self._redibujar_icono_candado(w), size=lambda w, *a: self._redibujar_icono_candado(w))
        self.lbl_candado = Label(
            text=md_icons.get("lock-outline", "🔒"),
            font_name="Icons",
            font_size="24sp",
            color=tema.primario,
            halign="center",
            valign="middle"
        )
        self.lbl_candado.bind(size=self.lbl_candado.setter('text_size'))
        self.caja_icono.add_widget(self.lbl_candado)
        tarjeta.add_widget(self.caja_icono)
        self._redibujar_icono_candado(self.caja_icono)
        
        self.lbl_tit_card = Label(text="[b]Actualiza tu contraseña[/b]", markup=True, font_size="18sp", color=tema.texto_principal, halign="center", size_hint_y=None, height=26)
        self.lbl_tit_card.bind(size=self.lbl_tit_card.setter('text_size'))
        tarjeta.add_widget(self.lbl_tit_card)
        
        formulario = BoxLayout(orientation="vertical", spacing=12, size_hint_y=None)
        formulario.bind(minimum_height=formulario.setter('height'))
        
        formulario.add_widget(self._crear_etiqueta("CONTRASEÑA ACTUAL"))
        self.in_actual = EntradaTexto(text="", hint_text="Ingresa tu contraseña actual", password=True)
        formulario.add_widget(self.in_actual)
        
        formulario.add_widget(self._crear_etiqueta("NUEVA CONTRASEÑA"))
        self.in_nueva = EntradaTexto(text="", hint_text="Ingresa tu nueva contraseña", password=True)
        formulario.add_widget(self.in_nueva)
        
        formulario.add_widget(self._crear_etiqueta("CONFIRMAR NUEVA CONTRASEÑA"))
        self.in_conf = EntradaTexto(text="", hint_text="Repite tu nueva contraseña", password=True)
        formulario.add_widget(self.in_conf)
        
        self.lbl_pautas = Label(text="Mínimo 8 caracteres, incluyendo letras y números.", font_size="12sp", color=tema.texto_atenuado, size_hint_y=None, height=20, halign="left")
        self.lbl_pautas.bind(size=self.lbl_pautas.setter('text_size'))
        formulario.add_widget(self.lbl_pautas)
        tarjeta.add_widget(formulario)
        
        fila_btn = BoxLayout(orientation="horizontal", spacing=12, size_hint_y=None, height=44)
        fila_btn.add_widget(Widget())
        
        self.btn_cancelar = Button(
            text="Cancelar",
            font_size="13sp",
            bold=True,
            color=tema.texto_secundario,
            background_normal="",
            background_down="",
            background_color=[0, 0, 0, 0],
            size_hint=(None, 1),
            width=110
        )
        self.btn_cancelar.bind(pos=lambda w, *a: self._redibujar_btn_contorno(w), size=lambda w, *a: self._redibujar_btn_contorno(w), state=lambda w, *a: self._redibujar_btn_contorno(w))
        self.btn_cancelar.bind(on_release=lambda *a: self.cancelar())
        fila_btn.add_widget(self.btn_cancelar)
        
        self.btn_actualizar = BotonPrimario(text="Actualizar", size_hint=(None, 1), width=140)
        self.btn_actualizar.bind(on_release=lambda *a: self.actualizar())
        fila_btn.add_widget(self.btn_actualizar)
        
        tarjeta.add_widget(fila_btn)
        contenedor.add_widget(tarjeta)
        self.add_widget(contenedor)
        
    def _redibujar_icono_candado(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.fondo_resaltado)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[26])
            
    def _crear_etiqueta(self, texto):
        lbl = Label(text=texto, font_size="11sp", bold=True, color=tema.texto_atenuado, size_hint_y=None, height=18, halign="left")
        lbl.bind(size=lbl.setter('text_size'))
        self.etiquetas_input.append(lbl)
        return lbl
        
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
            
    def cancelar(self):
        if self.al_cancelar:
            self.al_cancelar()
            
    def actualizar(self):
        if self.al_actualizar:
            self.al_actualizar()
            
    def actualizar_tema(self, *args):
        self.lbl_sub.color = tema.texto_secundario
        self._redibujar_icono_candado(self.caja_icono)
        self.lbl_candado.color = tema.primario
        self.lbl_tit_card.color = tema.texto_principal
        for lbl in self.etiquetas_input:
            lbl.color = tema.texto_atenuado
        self.in_actual._al_cambiar_tema()
        self.in_nueva._al_cambiar_tema()
        self.in_conf._al_cambiar_tema()
        self.lbl_pautas.color = tema.texto_atenuado
        self._redibujar_btn_contorno(self.btn_cancelar)
        self.btn_cancelar.color = tema.texto_secundario
        self.btn_actualizar._actualizar_fondo()
