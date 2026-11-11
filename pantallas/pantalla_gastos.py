"""
CENTS - Pantalla de Gastos
Historial completo de gastos con filtros, búsqueda en vivo y botón para exportar historial.
Adaptado a Modo Claro y Modo Oscuro con alta legibilidad.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Line
from kivymd.icon_definitions import md_icons
from tema import tema
from estado_app import estado
from componentes.tarjetas import TarjetaBase, EntradaTexto, BotonPildora

class VistaGastos(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(do_scroll_x=False, **kwargs)
        self.filtro_busqueda = ""
        self._construir_ui()
        estado.bind(gastos=self.refrescar_tabla)
        
    def _construir_ui(self):
        contenedor = BoxLayout(
            orientation="vertical",
            spacing=16,
            padding=[24, 20, 24, 24],
            size_hint_y=None
        )
        contenedor.bind(minimum_height=contenedor.setter('height'))
        
        # 1. Encabezado con Botón de Exportar
        fila_acciones = BoxLayout(orientation="horizontal", size_hint_y=None, height=38)
        self.lbl_info = Label(text="Historial completo de tus movimientos.", font_size="13sp", color=tema.texto_secundario, halign="left")
        self.lbl_info.bind(size=self.lbl_info.setter('text_size'))
        fila_acciones.add_widget(self.lbl_info)
        
        self.btn_exportar = Button(
            text=f"{md_icons.get('tray-arrow-down', '↓')}  Exportar historial",
            font_size="13sp",
            bold=True,
            color=tema.texto_principal,
            background_normal="",
            background_down="",
            background_color=[0, 0, 0, 0],
            size_hint=(None, 1),
            width=160
        )
        self.btn_exportar.bind(pos=lambda w, *a: self._redibujar_btn_contorno(w), size=lambda w, *a: self._redibujar_btn_contorno(w), state=lambda w, *a: self._redibujar_btn_contorno(w))
        fila_acciones.add_widget(self.btn_exportar)
        contenedor.add_widget(fila_acciones)
        
        # 2. Tarjeta Principal: Todas las transacciones
        self.tarjeta = TarjetaBase(orientation="vertical", padding=[20, 20, 20, 20], spacing=16, size_hint_y=None)
        self.tarjeta.bind(minimum_height=self.tarjeta.setter('height'))
        
        fila_t = BoxLayout(orientation="horizontal", size_hint_y=None, height=28)
        self.lbl_t = Label(text="[b]Todas las transacciones[/b]", markup=True, font_size="16sp", color=tema.texto_principal, halign="left")
        self.lbl_t.bind(size=self.lbl_t.setter('text_size'))
        fila_t.add_widget(self.lbl_t)
        
        self.lbl_conteo = Label(text=f"{len(estado.gastos)} movimientos", font_size="12sp", color=tema.texto_atenuado, size_hint=(None, 1), width=120, halign="right")
        self.lbl_conteo.bind(size=self.lbl_conteo.setter('text_size'))
        fila_t.add_widget(self.lbl_conteo)
        self.tarjeta.add_widget(fila_t)
        
        # Barra de filtros
        filtros = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=40)
        
        self.in_buscar = EntradaTexto(text="", hint_text="Buscar gasto o descripción...", size_hint_x=0.42)
        self.in_buscar.bind(text=self._al_buscar)
        filtros.add_widget(self.in_buscar)
        
        self.botones_filtros = [
            self._crear_boton_filtro("Este mes ▼"),
            self._crear_boton_filtro("Categoría ▼"),
            self._crear_boton_filtro("Método de pago ▼")
        ]
        for bf in self.botones_filtros:
            filtros.add_widget(bf)
        
        self.btn_limpiar = Button(
            text="Limpiar filtros",
            font_size="12sp",
            color=tema.texto_atenuado,
            background_normal="",
            background_down="",
            background_color=[0, 0, 0, 0],
            size_hint=(None, 1),
            width=100
        )
        self.btn_limpiar.bind(on_release=lambda *a: self._limpiar_filtros())
        filtros.add_widget(self.btn_limpiar)
        
        self.tarjeta.add_widget(filtros)
        
        # Encabezado de Columnas
        self.enc = BoxLayout(orientation="horizontal", size_hint_y=None, height=36, padding=[12, 0, 12, 0])
        self.enc.bind(pos=lambda w, *a: self._redibujar_enc(w), size=lambda w, *a: self._redibujar_enc(w))
        
        self.celdas_enc = [
            self._crear_celda_enc("FECHA", size_hint_x=0.15),
            self._crear_celda_enc("DESCRIPCIÓN", size_hint_x=0.32),
            self._crear_celda_enc("CATEGORÍA", size_hint_x=0.18),
            self._crear_celda_enc("MÉTODO", size_hint_x=0.15),
            self._crear_celda_enc("MONTO", size_hint_x=0.12, alineacion="right"),
            self._crear_celda_enc("ACCIONES", size_hint_x=0.08, alineacion="center")
        ]
        for c in self.celdas_enc:
            self.enc.add_widget(c)
        self.tarjeta.add_widget(self.enc)
        self._redibujar_enc(self.enc)
        
        # Filas
        self.caja_filas = BoxLayout(orientation="vertical", spacing=2, size_hint_y=None)
        self.caja_filas.bind(minimum_height=self.caja_filas.setter('height'))
        self._cargar_filas()
        self.tarjeta.add_widget(self.caja_filas)
        
        # Paginación
        fila_pag = BoxLayout(orientation="horizontal", size_hint_y=None, height=36, padding=[8, 8, 8, 0])
        self.lbl_p = Label(text="Mostrando 1 - 10 de 24 movimientos", font_size="12sp", color=tema.texto_atenuado, halign="left")
        self.lbl_p.bind(size=self.lbl_p.setter('text_size'))
        fila_pag.add_widget(self.lbl_p)
        
        caja_paginas = BoxLayout(orientation="horizontal", spacing=6, size_hint=(None, 1))
        caja_paginas.bind(minimum_width=caja_paginas.setter('width'))
        self.botones_pag = []
        for p in ["1", "2", "3", "→"]:
            pb = BotonPildora(texto=p, activo=(p == "1"), size_hint=(None, None), size=(32, 32))
            self.botones_pag.append((pb, p))
            caja_paginas.add_widget(pb)
        fila_pag.add_widget(caja_paginas)
        
        self.tarjeta.add_widget(fila_pag)
        contenedor.add_widget(self.tarjeta)
        self.add_widget(contenedor)
        
    def _crear_celda_enc(self, texto, size_hint_x=0.2, alineacion="left"):
        lbl = Label(text=texto, font_size="11sp", bold=True, color=tema.texto_atenuado, size_hint_x=size_hint_x, halign=alineacion)
        lbl.bind(size=lbl.setter('text_size'))
        return lbl
        
    def _crear_boton_filtro(self, texto):
        b = Button(
            text=texto,
            font_size="12sp",
            color=tema.texto_secundario,
            background_normal="",
            background_down="",
            background_color=[0, 0, 0, 0],
            size_hint=(None, 1),
            width=120
        )
        b.bind(pos=lambda w, *a: self._redibujar_btn_contorno(w), size=lambda w, *a: self._redibujar_btn_contorno(w), state=lambda w, *a: self._redibujar_btn_contorno(w))
        return b
        
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
            
    def _redibujar_enc(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.fondo_sutil)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[6])
            
    def _cargar_filas(self):
        self.caja_filas.clear_widgets()
        filtrados = [
            e for e in estado.gastos 
            if self.filtro_busqueda.lower() in e["descripcion"].lower() or self.filtro_busqueda.lower() in e["categoria"].lower()
        ]
        
        for item in filtrados:
            fila = BoxLayout(orientation="horizontal", size_hint_y=None, height=44, padding=[12, 0, 12, 0])
            fila.bind(pos=lambda w, *a: self._redibujar_linea_fila(w), size=lambda w, *a: self._redibujar_linea_fila(w))
            
            lbl_fecha = Label(text=item['fecha'], font_size="12sp", color=tema.texto_atenuado, size_hint_x=0.15, halign="left")
            lbl_fecha.bind(size=lbl_fecha.setter('text_size'))
            fila.add_widget(lbl_fecha)
            
            lbl_desc = Label(text=f"[b]{item['descripcion']}[/b]", markup=True, font_size="13sp", color=tema.texto_principal, size_hint_x=0.32, halign="left")
            lbl_desc.bind(size=lbl_desc.setter('text_size'))
            fila.add_widget(lbl_desc)
            
            lbl_cat = Label(text=item['categoria'], font_size="13sp", color=tema.texto_secundario, size_hint_x=0.18, halign="left")
            lbl_cat.bind(size=lbl_cat.setter('text_size'))
            fila.add_widget(lbl_cat)
            
            lbl_met = Label(text=item['metodo'], font_size="12sp", color=tema.texto_secundario, size_hint_x=0.15, halign="left")
            lbl_met.bind(size=lbl_met.setter('text_size'))
            fila.add_widget(lbl_met)
            
            lbl_monto = Label(text=f"[b]$ {item['monto']:,.2f}[/b]", markup=True, font_size="13sp", color=tema.texto_principal, size_hint_x=0.12, halign="right")
            lbl_monto.bind(size=lbl_monto.setter('text_size'))
            fila.add_widget(lbl_monto)
            
            btn_editar = Button(
                text=md_icons.get("pencil-outline", "✎"),
                font_name="Icons",
                font_size="16sp",
                color=tema.primario,
                background_normal="",
                background_down="",
                background_color=[0, 0, 0, 0],
                size_hint_x=0.08
            )
            fila.add_widget(btn_editar)
            
            self._redibujar_linea_fila(fila)
            self.caja_filas.add_widget(fila)
            
    def _redibujar_linea_fila(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.borde_claro)
            Line(points=[w.x, w.y, w.x + w.width, w.y], width=1)
            
    def _al_buscar(self, instance, value):
        self.filtro_busqueda = value.strip()
        self._cargar_filas()
        
    def _limpiar_filtros(self):
        self.in_buscar.text = ""
        self.filtro_busqueda = ""
        self._cargar_filas()
        
    def refrescar_tabla(self, *args):
        self._cargar_filas()
        self.lbl_conteo.text = f"{len(estado.gastos)} movimientos"
        
    def actualizar_tema(self, *args):
        self.lbl_info.color = tema.texto_secundario
        self._redibujar_btn_contorno(self.btn_exportar)
        self.btn_exportar.color = tema.texto_principal
        self.lbl_t.color = tema.texto_principal
        self.lbl_conteo.color = tema.texto_atenuado
        self.in_buscar._al_cambiar_tema()
        for bf in self.botones_filtros:
            self._redibujar_btn_contorno(bf)
            bf.color = tema.texto_secundario
        self.btn_limpiar.color = tema.texto_atenuado
        self._redibujar_enc(self.enc)
        for c in self.celdas_enc:
            c.color = tema.texto_atenuado
        self.lbl_p.color = tema.texto_atenuado
        for pb, p in self.botones_pag:
            pb._actualizar_fondo()
        self._cargar_filas()
