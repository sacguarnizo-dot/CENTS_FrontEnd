"""
CENTS - Pantalla de Ingresos
Métricas de ingresos, filtros interactivos (mes, categoría y método de cobro), búsqueda en vivo,
paginación real y tabla de transacciones con edición de cada ingreso.
"""

import math
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Line
from tema import tema
from estado_app import estado, CATEGORIAS_INGRESO, METODOS_INGRESO
from iconos import con_icono
from kivymd.icon_definitions import md_icons
from utilidades import mes_de, nombre_mes, etiqueta_mes_menu, meses_disponibles, fecha_orden
from componentes.tarjetas import TarjetaBase, TarjetaMetrica, EntradaTexto, EntradaEstilizada
from componentes.menu_filtro import abrir_menu
from componentes.paginacion import FilaPaginacion
from componentes.modales_edicion import ModalEditarIngreso

TAMANO_PAGINA = 7
ETIQUETA_MES = "Este mes"
ETIQUETA_CATEGORIA = "Categoría"
ETIQUETA_METODO = "Método de cobro"

class VistaIngresos(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(do_scroll_x=False, **kwargs)
        self.filtro_busqueda = ""
        self.filtro_mes = None
        self.filtro_categoria = None
        self.filtro_metodo = None
        self.pagina = 1
        self._construir_ui()
        estado.bind(ingresos=self.refrescar_tabla, total_ingresado=self._actualizar_kpis, ingreso_mes_actual=self._actualizar_kpis)
        
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
            texto_badge=con_icono("18.2% vs. mes anterior", "trending-up"),
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
            texto_badge=con_icono("3.5% de tus gastos", "trending-up"),
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
        
        self.btn_mes = self._crear_boton_filtro()
        self.btn_cat = self._crear_boton_filtro()
        self.btn_met = self._crear_boton_filtro()
        self.btn_mes.bind(on_release=lambda *a: self._abrir_menu_mes())
        self.btn_cat.bind(on_release=lambda *a: self._abrir_menu_categoria())
        self.btn_met.bind(on_release=lambda *a: self._abrir_menu_metodo())
        self.botones_filtros = [self.btn_mes, self.btn_cat, self.btn_met]
        for bf in self.botones_filtros:
            filtros.add_widget(bf)
        self._actualizar_botones_filtros()
        
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
        
        # Paginación (se crea antes de cargar las filas porque estas la actualizan)
        self.paginacion = FilaPaginacion(unidad="ingresos", tamano=TAMANO_PAGINA, al_cambiar=self._al_cambiar_pagina, tam_boton=28, alto=36, padding=[8, 8, 8, 0])
        
        # Contenedor de Filas
        self.caja_filas = BoxLayout(orientation="vertical", spacing=2, size_hint_y=None)
        self.caja_filas.bind(minimum_height=self.caja_filas.setter('height'))
        self._cargar_filas()
        self.tarjeta.add_widget(self.caja_filas)
        
        self.tarjeta.add_widget(self.paginacion)
        contenedor.add_widget(self.tarjeta)
        self.add_widget(contenedor)
        
    def _crear_celda_enc(self, texto, size_hint_x=0.2, alineacion="left"):
        lbl = Label(text=texto, font_size="11sp", bold=True, color=tema.texto_atenuado, size_hint_x=size_hint_x, halign=alineacion)
        lbl.bind(size=lbl.setter('text_size'))
        tema.bind(texto_atenuado=lambda *a, l=lbl: setattr(l, 'color', tema.texto_atenuado))
        return lbl
        
    def _crear_boton_filtro(self):
        b = Button(text="", markup=True, font_size="12sp", color=tema.texto_secundario, background_color=[0, 0, 0, 0], size_hint=(None, 1), width=115)
        b.filtro_activo = False
        b.bind(pos=lambda w, *a: self._redibujar_btn_filtro(w), size=lambda w, *a: self._redibujar_btn_filtro(w))
        return b
        
    def _redibujar_btn_filtro(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            if getattr(w, "filtro_activo", False):
                Color(*tema.fondo_resaltado)
                RoundedRectangle(pos=w.pos, size=w.size, radius=[8])
                Color(*tema.primario)
            else:
                Color(*tema.borde)
            Line(rounded_rectangle=(w.x, w.y, w.width, w.height, 8), width=1)
            
    def _redibujar_enc(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.fondo_sutil)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[6])
            
    # ------------------------------------------------------------------ filtros
    def _actualizar_botones_filtros(self):
        """Pone en cada botón el filtro elegido (o su nombre por defecto) y lo resalta si está activo."""
        estados = [
            (self.btn_mes, nombre_mes(self.filtro_mes) if self.filtro_mes else ETIQUETA_MES, self.filtro_mes is not None),
            (self.btn_cat, self.filtro_categoria or ETIQUETA_CATEGORIA, self.filtro_categoria is not None),
            (self.btn_met, self.filtro_metodo or ETIQUETA_METODO, self.filtro_metodo is not None),
        ]
        for b, etiqueta, activo in estados:
            b.filtro_activo = activo
            b.text = con_icono(etiqueta, "chevron-down", derecha=True)
            b.bold = activo
            b.color = tema.primario if activo else tema.texto_secundario
            b.texture_update()
            b.width = max(115, b.texture_size[0] + 34)
            self._redibujar_btn_filtro(b)
            
    def _opciones_unicas(self, base, campo):
        """Opciones fijas del formulario más cualquier valor que exista en los datos."""
        vistos = list(base)
        for i in estado.ingresos:
            if i[campo] not in vistos:
                vistos.append(i[campo])
        return vistos
        
    def _abrir_menu_mes(self):
        meses = meses_disponibles([i["fecha"] for i in estado.ingresos])
        opciones = [(None, "Todos los meses")] + [(m, etiqueta_mes_menu(m)) for m in meses]
        abrir_menu(self.btn_mes, opciones, self.filtro_mes, self._elegir_mes, ancho=230)
        
    def _abrir_menu_categoria(self):
        opciones = [(None, "Todas las categorías")] + [(c, c) for c in self._opciones_unicas(CATEGORIAS_INGRESO, "categoria")]
        abrir_menu(self.btn_cat, opciones, self.filtro_categoria, self._elegir_categoria, ancho=210)
        
    def _abrir_menu_metodo(self):
        opciones = [(None, "Todos los métodos")] + [(m, m) for m in self._opciones_unicas(METODOS_INGRESO, "metodo")]
        abrir_menu(self.btn_met, opciones, self.filtro_metodo, self._elegir_metodo, ancho=210)
        
    def _elegir_mes(self, valor):
        self.filtro_mes = valor
        self._aplicar_filtros()
        
    def _elegir_categoria(self, valor):
        self.filtro_categoria = valor
        self._aplicar_filtros()
        
    def _elegir_metodo(self, valor):
        self.filtro_metodo = valor
        self._aplicar_filtros()
        
    def _aplicar_filtros(self):
        self.pagina = 1
        self._actualizar_botones_filtros()
        self._cargar_filas()
        
    def _registros_filtrados(self):
        """Ingresos que cumplen búsqueda y filtros, del más reciente al más antiguo."""
        q = self.filtro_busqueda.lower()
        resultado = []
        for i in estado.ingresos:
            if q and q not in i["descripcion"].lower() and q not in i["categoria"].lower():
                continue
            if self.filtro_categoria is not None and i["categoria"] != self.filtro_categoria:
                continue
            if self.filtro_metodo is not None and i["metodo"] != self.filtro_metodo:
                continue
            if self.filtro_mes is not None and mes_de(i["fecha"]) != self.filtro_mes:
                continue
            resultado.append(i)
        return sorted(resultado, key=lambda r: fecha_orden(r["fecha"]), reverse=True)
        
    # -------------------------------------------------------------------- tabla
    def _cargar_filas(self):
        self.caja_filas.clear_widgets()
        filtrados = self._registros_filtrados()
        total = len(filtrados)
        self.pagina = min(self.pagina, max(1, math.ceil(total / TAMANO_PAGINA)))
        inicio = (self.pagina - 1) * TAMANO_PAGINA
        visibles = filtrados[inicio:inicio + TAMANO_PAGINA]
        
        if not visibles:
            vacio = Label(text="No hay ingresos que coincidan con los filtros.", font_size="13sp", color=tema.texto_atenuado, size_hint_y=None, height=70)
            self.caja_filas.add_widget(vacio)
        
        for item in visibles:
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
            
            btn_editar = Button(text=md_icons.get("pencil-outline", ""), font_name="Icons", font_size="15sp", color=tema.primario, background_color=[0, 0, 0, 0], size_hint_x=0.08)
            btn_editar.bind(on_release=lambda *a, it=item: self._abrir_editar(it))
            fila.add_widget(btn_editar)
            
            self.caja_filas.add_widget(fila)
            
        self.paginacion.actualizar(total, self.pagina)
            
    def _redibujar_linea_fila(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.borde_claro)
            Line(points=[w.x, w.y, w.x + w.width, w.y], width=1)
            
    def _abrir_editar(self, item):
        ModalEditarIngreso(item).open()
        
    def _al_cambiar_pagina(self, pagina):
        self.pagina = pagina
        self._cargar_filas()
            
    def _al_buscar(self, instance, value):
        self.filtro_busqueda = value.strip()
        self.pagina = 1
        self._cargar_filas()
        
    def _limpiar_filtros(self):
        self.filtro_busqueda = ""
        self.filtro_mes = None
        self.filtro_categoria = None
        self.filtro_metodo = None
        self.pagina = 1
        self.in_buscar.text = ""
        self._actualizar_botones_filtros()
        self._cargar_filas()
        
    def _actualizar_kpis(self, *args):
        self.tarjeta1.actualizar_valor(f"$ {estado.total_ingresado:,.2f}")
        self.tarjeta3.actualizar_valor(f"$ {estado.ingreso_mes_actual:,.2f}")
        
    def refrescar_tabla(self, *args):
        self._cargar_filas()
        
    def actualizar_tema(self, *args):
        self.tarjeta1.actualizar_tema()
        self.tarjeta2.actualizar_tema()
        self.tarjeta3.actualizar_tema()
        self.lbl_t.color = tema.texto_principal
        self.in_buscar._al_cambiar_tema()
        self._actualizar_botones_filtros()
        self.btn_limpiar.color = tema.texto_atenuado
        self._redibujar_enc(self.enc)
        for c in self.celdas_enc:
            c.color = tema.texto_atenuado
        self.paginacion.actualizar_tema()
        self._cargar_filas()
