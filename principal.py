"""
CENTS - Aplicación Principal de Gestión Financiera
Frontend desarrollado en Python 3.10 con Kivy 2.3.1 y KivyMD 1.2.0.
"""

import os
import sys
import ctypes

# Habilitar DPI Awareness en Windows para evitar que la interfaz se vea borrosa o estirada
if sys.platform == "win32":
    try:
        # Per-monitor DPI awareness (Windows 8.1+)
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            # System DPI awareness (Windows Vista+)
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

# Configuración de directorio KIVY_HOME local para evitar problemas de permisos en Windows
directorio_base = os.path.dirname(os.path.abspath(__file__))
if directorio_base not in sys.path:
    sys.path.insert(0, directorio_base)

if "KIVY_HOME" not in os.environ:
    os.environ["KIVY_HOME"] = os.path.join(directorio_base, ".kivy")

from kivy.config import Config
Config.set('graphics', 'width', '1280')
Config.set('graphics', 'height', '760')
Config.set('graphics', 'minimum_width', '1024')
Config.set('graphics', 'minimum_height', '640')
Config.set('graphics', 'resizable', '1')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, FadeTransition

from tema import tema
from estado_app import estado
from pantallas.pantallas_autenticacion import PantallaLogin, PantallaRegistro, PantallaRecuperarContrasena
from pantallas.portal_principal import PantallaPortalPrincipal

class AplicacionCents(MDApp):
    def build(self):
        self.title = "CENTS - Finanzas Bajo Control"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        Window.clearcolor = tema.fondo_app
        tema.bind(fondo_app=lambda *a: setattr(Window, 'clearcolor', tema.fondo_app))
        
        # Administrador de pantallas con transiciones suaves
        sm = ScreenManager(transition=FadeTransition(duration=0.15))
        
        # 1. Pantallas de Autenticación
        sm.add_widget(PantallaLogin(name="login"))
        sm.add_widget(PantallaRegistro(name="registro"))
        sm.add_widget(PantallaRecuperarContrasena(name="recuperar_contrasena"))
        
        # 2. Portal Principal (Inicio, Ingresos, Gastos, Presupuestos, Inversiones, Perfil, Configuración)
        self.portal = PantallaPortalPrincipal(name="portal_principal")
        sm.add_widget(self.portal)
        
        # Iniciar en el portal principal
        sm.current = "portal_principal"
        
        return sm

if __name__ == "__main__":
    AplicacionCents().run()
