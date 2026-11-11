"""
CENTS - Pantalla Portal Principal
Integra la barra lateral fija (MenuLateral), la barra superior dinámica (BarraSuperior)
y el conmutador de pantallas y modales.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle
from tema import tema
from estado_app import estado
from componentes.barra_lateral import MenuLateral
from componentes.barra_superior import BarraSuperior
from componentes.modales import ModalNuevoGasto, ModalNuevoIngreso, ModalConsejos
from pantallas.pantalla_inicio import VistaInicio
from pantallas.pantalla_ingresos import VistaIngresos
from pantallas.pantalla_gastos import VistaGastos
from pantallas.pantalla_presupuestos import VistaPresupuestos
from pantallas.pantalla_inversiones import VistaInversiones
from pantallas.pantalla_perfil import VistaMiPerfil, VistaEditarPerfil, VistaCambiarContrasena
from pantallas.pantalla_configuracion import VistaConfiguracion

class PantallaPortalPrincipal(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vista_activa_nombre = "inicio"
        self._construir_ui()
        
    def _construir_ui(self):
        self.raiz = BoxLayout(orientation="horizontal")
        with self.raiz.canvas.before:
            Color(*tema.fondo_app)
            Rectangle(pos=self.raiz.pos, size=self.raiz.size)
        self.raiz.bind(pos=lambda w, *a: self._redibujar_raiz(w), size=lambda w, *a: self._redibujar_raiz(w))
        tema.bind(modo=self.al_cambiar_modo_global)
        
        # 1. Barra Lateral Izquierda
        self.barra_lateral = MenuLateral()
        self.barra_lateral.al_navegar = self.navegar_a
        self.barra_lateral.al_mostrar_consejos = self.mostrar_dialogo_consejos
        self.raiz.add_widget(self.barra_lateral)
        
        # 2. Panel Derecho (Barra Superior + Contenido)
        panel_derecho = BoxLayout(orientation="vertical")
        
        self.barra_superior = BarraSuperior()
        self.barra_superior.al_click_accion = self.manejar_accion_superior
        self.barra_superior.al_click_perfil = lambda: self.navegar_a("perfil")
        panel_derecho.add_widget(self.barra_superior)
        
        # Contenedor de la vista activa
        self.contenedor_vistas = BoxLayout(orientation="vertical")
        panel_derecho.add_widget(self.contenedor_vistas)
        
        self.raiz.add_widget(panel_derecho)
        self.add_widget(self.raiz)
        
        # Instanciar todas las vistas
        self.vistas = {
            "inicio": VistaInicio(al_ver_todos_los_gastos=lambda: self.navegar_a("gastos")),
            "ingresos": VistaIngresos(),
            "gastos": VistaGastos(),
            "presupuestos": VistaPresupuestos(),
            "inversiones": VistaInversiones(),
            "configuracion": VistaConfiguracion(),
            "perfil": VistaMiPerfil(
                al_editar=lambda: self.navegar_a("editar_perfil"),
                al_cambiar_clave=lambda: self.navegar_a("cambiar_contrasena"),
                al_cerrar_sesion=self.cerrar_sesion,
                al_volver=lambda: self.navegar_a("inicio")
            ),
            "editar_perfil": VistaEditarPerfil(
                al_guardar=lambda: self.navegar_a("perfil"),
                al_cancelar=lambda: self.navegar_a("perfil")
            ),
            "cambiar_contrasena": VistaCambiarContrasena(
                al_actualizar=lambda: self.navegar_a("perfil"),
                al_cancelar=lambda: self.navegar_a("perfil")
            )
        }
        
        self.navegar_a("inicio")
        
    def _redibujar_raiz(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.fondo_app)
            Rectangle(pos=w.pos, size=w.size)
            
    def al_cambiar_modo_global(self, *args):
        self._redibujar_raiz(self.raiz)
        if hasattr(self, 'barra_lateral') and self.barra_lateral:
            self.barra_lateral.actualizar_tema()
        if hasattr(self, 'barra_superior') and self.barra_superior:
            self.barra_superior.actualizar_tema()
        if hasattr(self, 'vistas'):
            for nombre, vista in self.vistas.items():
                if hasattr(vista, 'actualizar_tema'):
                    try:
                        vista.actualizar_tema()
                    except Exception as e:
                        pass
            
    def navegar_a(self, nombre_vista):
        if nombre_vista not in self.vistas:
            return
            
        self.vista_activa_nombre = nombre_vista
        self.contenedor_vistas.clear_widgets()
        self.contenedor_vistas.add_widget(self.vistas[nombre_vista])
        
        if nombre_vista in ["inicio", "ingresos", "gastos", "presupuestos", "inversiones", "configuracion"]:
            self.barra_lateral.establecer_activo(nombre_vista)
            
        # Encabezados y botones de acción
        if nombre_vista == "inicio":
            self.barra_superior.actualizar_encabezado("Panel financiero", "Resumen general de tus finanzas", texto_accion="＋ Nuevo gasto")
        elif nombre_vista == "ingresos":
            self.barra_superior.actualizar_encabezado("Ingresos", "Registra y analiza tus fuentes de ingresos.", texto_accion="＋ Nuevo ingreso")
        elif nombre_vista == "gastos":
            self.barra_superior.actualizar_encabezado("Gastos", "Historial completo de tus movimientos.", texto_accion="＋ Nuevo gasto")
        elif nombre_vista == "presupuestos":
            self.barra_superior.actualizar_encabezado("Presupuestos y categorías", "Controla cuánto puedes gastar en cada área.", texto_accion=None)
        elif nombre_vista == "inversiones":
            self.barra_superior.actualizar_encabezado("Inversiones", "Historial completo de tus movimientos.", texto_accion=None)
        elif nombre_vista == "configuracion":
            self.barra_superior.actualizar_encabezado("Configuración", "Administra tu perfil, seguridad y preferencias.", texto_accion=None)
        elif nombre_vista == "perfil":
            self.barra_superior.actualizar_encabezado("Mi perfil", "Consulta y administra la información de tu cuenta.", texto_accion=None)
        elif nombre_vista == "editar_perfil":
            self.barra_superior.actualizar_encabezado("Editar perfil", "Actualiza la información personal asociada a tu cuenta.", texto_accion=None)
        elif nombre_vista == "cambiar_contrasena":
            self.barra_superior.actualizar_encabezado("Cambiar contraseña", "Actualiza tu contraseña para mantener protegida tu cuenta.", texto_accion=None)
            
    def manejar_accion_superior(self):
        if self.vista_activa_nombre in ["inicio", "gastos"]:
            dlg = ModalNuevoGasto(al_guardar=self._al_guardar_gasto)
            dlg.open()
        elif self.vista_activa_nombre == "ingresos":
            dlg = ModalNuevoIngreso(al_guardar=self._al_guardar_ingreso)
            dlg.open()
            
    def _al_guardar_gasto(self):
        self.vistas["inicio"].actualizar_datos()
        self.vistas["gastos"].refrescar_tabla()
        self.vistas["presupuestos"].refrescar_grid()
        
    def _al_guardar_ingreso(self):
        self.vistas["ingresos"].refrescar_tabla()
        
    def mostrar_dialogo_consejos(self):
        dlg = ModalConsejos()
        dlg.open()
        
    def cerrar_sesion(self):
        self.manager.current = "login"
