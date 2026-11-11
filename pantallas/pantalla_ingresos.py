"""
CENTS - Pantalla de Ingresos
Métricas de ingresos, filtros interactivos y tabla de transacciones de ingresos.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Line
from tema import tema
from estado_app import estado
from componentes.tarjetas import TarjetaBase, TarjetaMetrica, EntradaTexto, EntradaEstilizada

class VistaIngresos(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(do_scroll_x=False, **kwargs)
        self.filtro_busqueda = ""
        self._construir_ui()
        estado.bind(ingresos=self.refrescar_tabla)
        
    def _construir_ui(self):
        contenedor = BoxLayout(
            orientation="vertical",
            spacing=20,
            padding=[24, 20, 24, 24],
            size_hint_y=None
        )
        contenedor.bind(minimum_height=contenedor.setter('height'))
        
        # 1. Tres tarjetas métricas KPI
        fila_kpi = GridLayout(cols=3, spacing=16, size_hint_y=None, height=115)
        
        self.tarjeta1 = TarjetaMetrica(
            titulo="Total Ingresado",
            valor=f"$ {estado.total_ingresado:,.2f}",
            texto_badge="↑ 18.2% vs. mes anterior",
            es_positivo=True
        )
        self.tarjeta2 = TarjetaMetrica(
            titulo="Ingreso Promedio Diario",
            valor=f"$ {estado.ingreso_promedio_diario:,.2f}",
            subtitulo="En los últimos 30 días"
        )
        self.tarjeta3 = TarjetaMetrica(
            titulo="Ingresos del Mes Actual",
            valor=f"$ {estado.ingreso_mes_actual:,.2f}",
            texto_badge="↑ 3.5% de tus gastos",
            es_positivo=True
        )
        
        fila_kpi.add_widget(self.tarjeta1)
        fila_kpi.add_widget(self.tarjeta2)
        fila_kpi.add_widget(self.tarjeta3)
        contenedor.add_widget(fila_kpi)
        
        # 2. Tarjeta Principal: Todas las transacciones de Ingresos
        self.tarjeta = TarjetaBase(orientation="vertical", padding=[20, 20, 20, 20], spacing=16, size_hint_y=None)
        self.tarjeta.bind(minimum_height=self.tarjeta.setter('height'))
        
        self.lbl_t = Label(text="[b]Todas las transacciones de Ingresos[/b]", markup=True, font_size="16sp", color=tema.texto_principal, size_hint_y=None, height=28, halign="left")
        self.lbl_t.bind(size=self.lbl_t.setter('text_size'))
        self.tarjeta.add_widget(self.lbl_t)
        
        # Fila de filtros
        filtros = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=38)
        
        self.in_buscar = EntradaTexto(text="", hint_text="Buscar ingreso o descripción...", size_hint_x=0.45)
        self.in_buscar.bind(text=self._al_buscar)
        filtros.add_widget(self.in_buscar)
        
        self.botones_filtros = [
            self._crear_boton_filtro("Este mes ⌄"),
            self._crear_boton_filtro("Categoría ⌄"),
            self._crear_boton_filtro("Método de cobro ⌄")
        ]
        for bf in self.botones_filtros:
            filtros.add_widget(bf)
        
        self.btn_limpiar = Button(text="Limpiar filtros", font_size="12sp", color=tema.texto_atenuado, background_color=[0,0,0,0], size_hint=(None, 1), width=90)
        self.btn_limpiar.bind(on_release=lambda *a: self._limpiar_filtros())
        filtros.add_widget(self.btn_limpiar)
        
        self.tarjeta.add_widget(filtros)
        
        # Encabezado de Columnas
        self.enc = BoxLayout(orientation="horizontal", size_hint_y=None, height=36, padding=[12, 0, 12, 0])
        with self.enc.canvas.before:
            Color(*tema.fondo_sutil)
            RoundedRectangle(pos=self.enc.pos, size=self.enc.size, radius=[6])
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
        
        # Contenedor de Filas
        self.caja_filas = BoxLayout(orientation="vertical", spacing=2, size_hint_y=None)
        self.caja_filas.bind(minimum_height=self.caja_filas.setter('height'))
        self._cargar_filas()
        self.tarjeta.add_widget(self.caja_filas)
        
        # Paginación
        fila_pag = BoxLayout(orientation="horizontal", size_hint_y=None, height=36, padding=[8, 8, 8, 0])
        self.lbl_pag = Label(text="Mostrando 1 - 7 de 24 ingresos", font_size="12sp", color=tema.texto_atenuado, halign="left")
        self.lbl_pag.bind(size=self.lbl_pag.setter('text_size'))
        fila_pag.add_widget(self.lbl_pag)
        
        caja_paginas = BoxLayout(orientation="horizontal", spacing=6, size_hint=(None, 1))
        caja_paginas.bind(minimum_width=caja_paginas.setter('width'))
        self.botones_pag = []
        for p in ["1", "2", "3"]:
            pb = Button(text=p, font_size="12sp", bold=True, size_hint=(None, None), size=(28, 28), background_color=[0, 0, 0, 0])
            self._estilizar_boton_pag(pb, activo=(p == "1"))
            self.botones_pag.append((pb, p))
            caja_paginas.add_widget(pb)
        fila_pag.add_widget(caja_paginas)
        
        self.tarjeta.add_widget(fila_pag)
        contenedor.add_widget(self.tarjeta)
        self.add_widget(contenedor)
        
    def _crear_celda_enc(self, texto, size_hint_x=0.2, alineacion="left"):
        lbl = Label(text=texto, font_size="11sp", bold=True, color=tema.texto_atenuado, size_hint_x=size_hint_x, halign=alineacion)
        lbl.bind(size=lbl.setter('text_size'))
        tema.bind(texto_atenuado=lambda *a, l=lbl: setattr(l, 'color', tema.texto_atenuado))
        return lbl
        
    def _crear_boton_filtro(self, texto):
        b = Button(text=texto, font_size="12sp", color=tema.texto_secundario, background_color=[0, 0, 0, 0], size_hint=(None, 1), width=115)
        with b.canvas.before:
            Color(*tema.borde)
            Line(rounded_rectangle=(b.x, b.y, b.width, b.height, 8), width=1)
        b.bind(pos=lambda w, *a: self._redibujar_btn_filtro(w), size=lambda w, *a: self._redibujar_btn_filtro(w))
        return b
        
    def _redibujar_btn_filtro(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.borde)
            Line(rounded_rectangle=(w.x, w.y, w.width, w.height, 8), width=1)
            
    def _redibujar_enc(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.fondo_sutil)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[6])
            
    def _estilizar_boton_pag(self, btn, activo):
        btn.canvas.before.clear()
        with btn.canvas.before:
            if activo:
                Color(*tema.primario)
                RoundedRectangle(pos=btn.pos, size=btn.size, radius=[6])
                btn.color = [1, 1, 1, 1]
            else:
                Color(*tema.borde)
                Line(rounded_rectangle=(btn.x, btn.y, btn.width, btn.height, 6), width=1)
                btn.color = tema.texto_secundario
                
    def _cargar_filas(self):
        self.caja_filas.clear_widgets()
        filtrados = [
            i for i in estado.ingresos 
            if self.filtro_busqueda.lower() in i["descripcion"].lower() or self.filtro_busqueda.lower() in i["categoria"].lower()
        ]
        
        for item in filtrados:
            fila = BoxLayout(orientation="horizontal", size_hint_y=None, height=44, padding=[12, 0, 12, 0])
            with fila.canvas.before:
                Color(*tema.borde_claro)
                Line(points=[fila.x, fila.y, fila.x + fila.width, fila.y], width=1)
            fila.bind(pos=lambda w, *a: self._redibujar_linea_fila(w), size=lambda w, *a: self._redibujar_linea_fila(w))
            
            lbl_fecha = Label(text=item['fecha'], font_size="12sp", color=tema.texto_atenuado, size_hint_x=0.15, halign="left")
            lbl_fecha.bind(size=lbl_fecha.setter('text_size'))
            fila.add_widget(lbl_fecha)
            
            lbl_desc = Label(text=f"[b]{item['descripcion']}[/b]", markup=True, font_size="13sp", color=tema.texto_principal, size_hint_x=0.32, halign="left")
            lbl_desc.bind(size=lbl_desc.setter('text_size'))
            tema.bind(texto_principal=lambda *a, l=lbl_desc: setattr(l, 'color', tema.texto_principal))
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
            
            btn_editar = Button(text="✎", font_size="14sp", color=tema.primario, background_color=[0, 0, 0, 0], size_hint_x=0.08)
            fila.add_widget(btn_editar)
            
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
        
    def actualizar_tema(self, *args):
        self.tarjeta1.actualizar_tema()
        self.tarjeta2.actualizar_tema()
        self.tarjeta3.actualizar_tema()
        self.lbl_t.color = tema.texto_principal
        self.in_buscar._al_cambiar_tema()
        for b in self.botones_filtros:
            self._redibujar_btn_filtro(b)
            b.color = tema.texto_secundario
        self.btn_limpiar.color = tema.texto_atenuado
        self._redibujar_enc(self.enc)
        for c in self.celdas_enc:
            c.color = tema.texto_atenuado
        self.lbl_pag.color = tema.texto_atenuado
        for pb, p in self.botones_pag:
            self._estilizar_boton_pag(pb, activo=(p == "1"))
        self._cargar_filas()
