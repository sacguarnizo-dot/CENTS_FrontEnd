"""
CENTS - Paneles de Configuración: Notificaciones, Seguridad y Privacidad
Cada panel se muestra a la derecha del menú de Configuración con el mismo estilo de tarjetas
del resto de la app. Los interruptores guardan su estado en `estado`.
"""
import os
import sys
_dir_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _dir_raiz not in sys.path:
    sys.path.insert(0, _dir_raiz)

from kivy.graphics import Color, Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from tema import tema
from estado_app import estado
from componentes.tarjetas import TarjetaBase, BotonPildora, InsigniaIcono
from componentes.interruptor import Interruptor

_ROLES = {
    "principal": lambda: tema.texto_principal,
    "secundario": lambda: tema.texto_secundario,
    "atenuado": lambda: tema.texto_atenuado,
}


def _parrafo(texto, tam="12sp", rol="secundario", bold=False):
    """Label de varias líneas que ajusta su alto al texto."""
    lbl = Label(text=f"[b]{texto}[/b]" if bold else texto, markup=bold, font_size=tam, color=_ROLES[rol](),
                halign="left", valign="top", size_hint_y=None, line_height=1.15)
    lbl.rol = rol
    lbl.bind(width=lambda w, v: setattr(w, "text_size", (v, None)))
    lbl.bind(texture_size=lambda w, ts: setattr(w, "height", ts[1]))
    return lbl


class FilaOpcion(BoxLayout):
    """Una opción: icono, título, descripción y un control a la derecha (interruptor o botón)."""
    def __init__(self, titulo, descripcion, control, icono=None, ultimo=False, **kwargs):
        super().__init__(orientation="horizontal", spacing=14, size_hint_y=None, height=66, padding=[0, 8, 0, 8], **kwargs)
        self.ultimo = ultimo
        self.control = control
        if icono:
            self.add_widget(InsigniaIcono(icono, tam=38, pos_hint={"center_y": 0.5}))
        col = BoxLayout(orientation="vertical", spacing=2)
        self.lbl_t = Label(text=f"[b]{titulo}[/b]", markup=True, font_size="13sp", color=tema.texto_principal, halign="left", valign="bottom")
        self.lbl_d = Label(text=descripcion, font_size="11sp", color=tema.texto_secundario, halign="left", valign="top")
        self.lbl_t.bind(size=self.lbl_t.setter("text_size"))
        self.lbl_d.bind(size=self.lbl_d.setter("text_size"))
        col.add_widget(self.lbl_t)
        col.add_widget(self.lbl_d)
        self.add_widget(col)
        control.pos_hint = {"center_y": 0.5}
        self.add_widget(control)
        self.bind(pos=self._linea, size=self._linea)

    def _linea(self, *args):
        self.canvas.before.clear()
        if not self.ultimo:
            with self.canvas.before:
                Color(*tema.borde_claro)
                Line(points=[self.x, self.y, self.x + self.width, self.y], width=1)

    def actualizar_tema(self):
        self.lbl_t.color = tema.texto_principal
        self.lbl_d.color = tema.texto_secundario
        self._linea()
        if isinstance(self.control, Interruptor):
            self.control._dibujar()


class _PanelBase(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=18, size_hint_y=None, **kwargs)
        self.bind(minimum_height=self.setter("height"))
        self._cabeceras = []
        self._filas = []
        self._parrafos = []

    def _tarjeta(self, titulo, subtitulo):
        tarjeta = TarjetaBase(orientation="vertical", padding=[24, 20, 24, 14], spacing=8, size_hint_y=None)
        tarjeta.bind(minimum_height=tarjeta.setter("height"))
        enc = BoxLayout(orientation="vertical", spacing=2, size_hint_y=None, height=44)
        lbl_t = Label(text=f"[b]{titulo}[/b]", markup=True, font_size="16sp", color=tema.texto_principal, halign="left")
        lbl_s = Label(text=subtitulo, font_size="12sp", color=tema.texto_atenuado, halign="left")
        lbl_t.bind(size=lbl_t.setter("text_size"))
        lbl_s.bind(size=lbl_s.setter("text_size"))
        enc.add_widget(lbl_t)
        enc.add_widget(lbl_s)
        tarjeta.add_widget(enc)
        self._cabeceras.append((lbl_t, lbl_s))
        self.add_widget(tarjeta)
        return tarjeta

    def _fila(self, tarjeta, titulo, descripcion, control, icono, ultimo=False):
        fila = FilaOpcion(titulo, descripcion, control, icono=icono, ultimo=ultimo)
        self._filas.append(fila)
        tarjeta.add_widget(fila)
        return fila

    def actualizar_tema(self, *args):
        for lbl_t, lbl_s in self._cabeceras:
            lbl_t.color = tema.texto_principal
            lbl_s.color = tema.texto_atenuado
        for fila in self._filas:
            fila.actualizar_tema()
        for p in self._parrafos:
            p.color = _ROLES[p.rol]()


# ------------------------------------------------------------------ Notificaciones
class PanelNotificaciones(_PanelBase):
    OPCIONES = [
        ("general", "Recibir notificaciones de CENTS", "Activa o desactiva todas las alertas de la aplicación.", "bell-outline"),
        ("presupuesto", "Alertas de presupuesto", "Te avisamos cuando estés cerca de superar el límite de una categoría.", "wallet-outline"),
        ("pagos", "Recordatorios de pagos", "Recibe un aviso antes de las fechas de tus pagos y servicios.", "calendar-clock-outline"),
        ("resumen", "Resumen semanal", "Un resumen de tus ingresos y gastos cada semana.", "chart-line"),
        ("consejos", "Consejos financieros", "Recomendaciones prácticas para cuidar tu dinero.", "lightbulb-on-outline"),
        ("novedades", "Novedades de CENTS", "Entérate de nuevas funciones y mejoras de la aplicación.", "bullhorn-outline"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        tarjeta = self._tarjeta("Notificaciones", "Elige qué avisos quieres recibir de CENTS.")
        self._interruptores = {}
        self._filas_por_clave = {}
        for i, (clave, titulo, desc, icono) in enumerate(self.OPCIONES):
            sw = Interruptor(activo=estado.notificaciones.get(clave, False), al_cambiar=lambda v, c=clave: self._al_cambiar(c, v))
            self._interruptores[clave] = sw
            self._filas_por_clave[clave] = self._fila(tarjeta, titulo, desc, sw, icono, ultimo=(i == len(self.OPCIONES) - 1))
        nota = _parrafo("Los cambios se guardan automáticamente.", tam="11sp", rol="atenuado")
        self._parrafos.append(nota)
        tarjeta.add_widget(nota)
        self._sincronizar()

    def _al_cambiar(self, clave, valor):
        estado.notificaciones[clave] = valor
        if clave == "general":
            self._sincronizar()

    def _sincronizar(self):
        """Con el interruptor general apagado, las demás opciones quedan apagadas y bloqueadas (conservan su valor)."""
        general = estado.notificaciones.get("general", True)
        for clave, sw in self._interruptores.items():
            if clave == "general":
                continue
            sw.disabled = not general
            sw.establecer(estado.notificaciones.get(clave, False) and general)
            self._filas_por_clave[clave].opacity = 1 if general else 0.55


# ---------------------------------------------------------------------- Seguridad
class PanelSeguridad(_PanelBase):
    def __init__(self, al_cambiar_clave=None, al_cerrar_sesion=None, **kwargs):
        super().__init__(**kwargs)
        tarjeta = self._tarjeta("Contraseña y acceso", "Protege tu cuenta y controla cómo se inicia sesión.")
        btn_clave = BotonPildora(texto="Cambiar", size_hint=(None, None), size=(110, 34))
        btn_clave.bind(on_release=lambda *a: al_cambiar_clave() if al_cambiar_clave else None)
        self._fila(tarjeta, "Cambiar contraseña", "Actualiza tu contraseña periódicamente para proteger tu cuenta.", btn_clave, "lock-outline")
        sw_dos = Interruptor(activo=estado.seguridad.get("dos_pasos", False), al_cambiar=lambda v: estado.seguridad.__setitem__("dos_pasos", v))
        self._fila(tarjeta, "Verificación en dos pasos", "Solicita un código adicional cada vez que inicies sesión.", sw_dos, "shield-check-outline")
        sw_alerta = Interruptor(activo=estado.seguridad.get("alertas_acceso", True), al_cambiar=lambda v: estado.seguridad.__setitem__("alertas_acceso", v))
        self._fila(tarjeta, "Alertas de inicio de sesión", "Te avisamos cuando se acceda a tu cuenta desde un dispositivo nuevo.", sw_alerta, "bell-ring-outline", ultimo=True)

        tarjeta2 = self._tarjeta("Sesión", "Administra tu sesión en este dispositivo.")
        btn_salir = BotonPildora(texto="Cerrar sesión", size_hint=(None, None), size=(120, 34))
        btn_salir.bind(on_release=lambda *a: al_cerrar_sesion() if al_cerrar_sesion else None)
        self._fila(tarjeta2, "Cerrar sesión", "Sal de tu cuenta en este dispositivo.", btn_salir, "logout", ultimo=True)


# --------------------------------------------------------------------- Privacidad
TERMINOS = [
    ("1. Aceptación de los términos", "Al crear una cuenta o utilizar CENTS, el usuario declara haber leído, comprendido y aceptado los presentes Términos y Condiciones. Si no está de acuerdo con alguna de sus disposiciones, deberá abstenerse de utilizar la aplicación."),
    ("2. Descripción del servicio", "CENTS es una herramienta de gestión financiera personal que permite registrar ingresos, gastos, presupuestos e inversiones con fines informativos y organizativos. La aplicación no constituye asesoría financiera, contable, legal ni tributaria."),
    ("3. Registro y seguridad de la cuenta", "El usuario es responsable de la veracidad de los datos proporcionados y de mantener la confidencialidad de sus credenciales de acceso. Cualquier actividad realizada desde su cuenta se presumirá efectuada por el propio usuario."),
    ("4. Uso adecuado", "El usuario se compromete a utilizar la aplicación de forma lícita y a no intentar vulnerar su seguridad, alterar su funcionamiento ni acceder a información de terceros."),
    ("5. Propiedad intelectual", "El software, el diseño, las marcas y los contenidos de CENTS pertenecen a sus titulares y se encuentran protegidos por la normativa aplicable. Se concede al usuario una licencia limitada, personal, revocable y no exclusiva para su uso."),
    ("6. Limitación de responsabilidad", "CENTS se ofrece «tal cual», sin garantía de disponibilidad ininterrumpida. Sus titulares no serán responsables por las decisiones financieras adoptadas con base en la información registrada ni por las pérdidas derivadas del uso de la aplicación."),
    ("7. Modificaciones", "Los presentes términos podrán ser actualizados en cualquier momento. El uso continuado de la aplicación tras la publicación de los cambios implicará su aceptación."),
    ("8. Legislación aplicable", "Estos términos se rigen por la legislación vigente del país del titular del servicio y cualquier controversia se someterá a los tribunales competentes."),
]

PRIVACIDAD = [
    ("Datos que recopilamos", "CENTS trata los datos que el usuario registra voluntariamente: información de perfil, ingresos, gastos, presupuestos e inversiones, así como las preferencias de configuración de la aplicación."),
    ("Finalidad del tratamiento", "Los datos se utilizan exclusivamente para prestar las funciones de la aplicación, personalizar la experiencia del usuario y mejorar el servicio. No se comercializan ni se ceden a terceros sin consentimiento previo."),
    ("Conservación y seguridad", "La información se conserva durante el tiempo que la cuenta permanezca activa y se protege mediante medidas técnicas y organizativas razonables para evitar accesos no autorizados, pérdida o alteración."),
    ("Derechos del usuario", "El usuario puede solicitar el acceso, la rectificación o la eliminación de sus datos personales, así como oponerse a su tratamiento, conforme a la normativa de protección de datos aplicable."),
    ("Contacto", "Para cualquier consulta sobre privacidad, el usuario podrá comunicarse con el equipo de CENTS a través de los canales de soporte de la aplicación."),
]


class PanelPrivacidad(_PanelBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._bloque("Términos y condiciones", "Última actualización: 1 de noviembre de 2026", TERMINOS)
        self._bloque("Política de privacidad", "Cómo tratamos y protegemos tu información.", PRIVACIDAD)

    def _bloque(self, titulo, subtitulo, secciones):
        tarjeta = self._tarjeta(titulo, subtitulo)
        for encabezado, cuerpo in secciones:
            h = _parrafo(encabezado, tam="13sp", rol="principal", bold=True)
            c = _parrafo(cuerpo, tam="12sp", rol="secundario")
            self._parrafos += [h, c]
            tarjeta.add_widget(h)
            tarjeta.add_widget(c)
