"""
CENTS - Definición de Temas y Estilos Visuales
Soporta Modo Claro y Modo Oscuro dinámico en toda la aplicación.
"""

from kivy.event import EventDispatcher
from kivy.properties import ListProperty, StringProperty

class GestorTema(EventDispatcher):
    modo = StringProperty("claro")  # "claro" o "oscuro"
    
    # Fondos
    fondo_app = ListProperty([0.972, 0.98, 0.988, 1])          # #F8FAFC
    fondo_tarjeta = ListProperty([1.0, 1.0, 1.0, 1])          # #FFFFFF
    fondo_barra_lateral = ListProperty([1.0, 1.0, 1.0, 1])    # #FFFFFF
    fondo_barra_superior = ListProperty([1.0, 1.0, 1.0, 1])   # #FFFFFF
    fondo_entrada = ListProperty([0.985, 0.988, 0.996, 1])    # #FBFCFE
    fondo_sutil = ListProperty([0.945, 0.961, 0.976, 1])      # #F1F5F9
    fondo_resaltado = ListProperty([0.937, 0.965, 1.0, 1])    # #EFF6FF
    
    # Bordes
    borde = ListProperty([0.886, 0.909, 0.941, 1])            # #E2E8F0
    borde_claro = ListProperty([0.945, 0.961, 0.976, 1])      # #F1F5F9
    
    # Colores principales (Azul Real)
    primario = ListProperty([0.145, 0.388, 0.922, 1])         # #2563EB
    primario_hover = ListProperty([0.114, 0.306, 0.847, 1])   # #1D4ED8
    texto_primario_boton = ListProperty([1.0, 1.0, 1.0, 1])
    
    # Textos
    texto_principal = ListProperty([0.059, 0.090, 0.165, 1])  # #0F172A
    texto_secundario = ListProperty([0.392, 0.455, 0.545, 1]) # #64748B
    texto_atenuado = ListProperty([0.58, 0.639, 0.722, 1])    # #94A3B8
    texto_placeholder = ListProperty([0.65, 0.70, 0.78, 1])
    
    # Estados
    exito = ListProperty([0.063, 0.725, 0.506, 1])            # #10B981
    exito_fondo = ListProperty([0.925, 0.988, 0.957, 1])      # #ECFDF5
    advertencia = ListProperty([0.96, 0.62, 0.043, 1])        # #F59E0B
    advertencia_fondo = ListProperty([1.0, 0.984, 0.922, 1])  # #FEF3C7
    peligro = ListProperty([0.937, 0.267, 0.267, 1])          # #EF4444
    peligro_fondo = ListProperty([0.996, 0.949, 0.949, 1])    # #FEF2F2

    def cambiar_tema(self, modo_solicitado):
        """
        Cambia el tema visual actualizando primero todos los atributos de color
        y finalmente la propiedad 'modo' para que todos los observadores
        lean los colores actualizados inmediatamente.
        """
        es_oscuro = modo_solicitado in ["oscuro", "dark", "☾ Oscuro", "☾ oscuro"]
        nuevo_modo = "oscuro" if es_oscuro else "claro"
        
        if es_oscuro:
            self.fondo_app = [0.05, 0.07, 0.11, 1]           # #0D121C
            self.fondo_tarjeta = [0.10, 0.14, 0.21, 1]        # #1A2436
            self.fondo_barra_lateral = [0.08, 0.11, 0.17, 1] # #141C2B
            self.fondo_barra_superior = [0.08, 0.11, 0.17, 1]
            self.fondo_entrada = [0.07, 0.10, 0.16, 1]       # #121929
            self.fondo_sutil = [0.12, 0.16, 0.24, 1]         # #1E293D
            self.fondo_resaltado = [0.14, 0.24, 0.42, 1]     # #243D6B
            
            self.borde = [0.20, 0.27, 0.38, 1]               # #334561
            self.borde_claro = [0.15, 0.21, 0.30, 1]
            
            self.primario = [0.231, 0.51, 0.965, 1]          # #3B82F6
            self.primario_hover = [0.145, 0.388, 0.922, 1]
            
            self.texto_principal = [0.972, 0.98, 0.988, 1]   # #F8FAFC
            self.texto_secundario = [0.75, 0.82, 0.92, 1]    # #C0D1EB
            self.texto_atenuado = [0.55, 0.63, 0.75, 1]      # #8CA1BF
            self.texto_placeholder = [0.42, 0.50, 0.62, 1]
            
            self.exito = [0.133, 0.773, 0.369, 1]
            self.exito_fondo = [0.06, 0.22, 0.15, 1]
            self.advertencia = [0.98, 0.745, 0.212, 1]
            self.advertencia_fondo = [0.28, 0.20, 0.06, 1]
            self.peligro = [0.973, 0.443, 0.443, 1]
            self.peligro_fondo = [0.28, 0.10, 0.10, 1]
        else:
            self.fondo_app = [0.972, 0.98, 0.988, 1]
            self.fondo_tarjeta = [1.0, 1.0, 1.0, 1]
            self.fondo_barra_lateral = [1.0, 1.0, 1.0, 1]
            self.fondo_barra_superior = [1.0, 1.0, 1.0, 1]
            self.fondo_entrada = [0.985, 0.988, 0.996, 1]
            self.fondo_sutil = [0.945, 0.961, 0.976, 1]
            self.fondo_resaltado = [0.937, 0.965, 1.0, 1]
            
            self.borde = [0.886, 0.909, 0.941, 1]
            self.borde_claro = [0.945, 0.961, 0.976, 1]
            
            self.primario = [0.145, 0.388, 0.922, 1]
            self.primario_hover = [0.114, 0.306, 0.847, 1]
            
            self.texto_principal = [0.059, 0.090, 0.165, 1]
            self.texto_secundario = [0.392, 0.455, 0.545, 1]
            self.texto_atenuado = [0.58, 0.639, 0.722, 1]
            self.texto_placeholder = [0.65, 0.70, 0.78, 1]
            
            self.exito = [0.063, 0.725, 0.506, 1]
            self.exito_fondo = [0.925, 0.988, 0.957, 1]
            self.advertencia = [0.96, 0.62, 0.043, 1]
            self.advertencia_fondo = [1.0, 0.984, 0.922, 1]
            self.peligro = [0.937, 0.267, 0.267, 1]
            self.peligro_fondo = [0.996, 0.949, 0.949, 1]

        # Actualizar modo al final para que los observadores lean los nuevos colores
        modo_anterior = self.modo
        self.modo = nuevo_modo
        # Si el modo ya era el mismo, forzar el despacho para refrescar la UI
        if modo_anterior == nuevo_modo:
            self.property('modo').dispatch(self)

tema = GestorTema()
