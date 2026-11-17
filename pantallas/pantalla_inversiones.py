"""
CENTS - Pantalla de Inversiones
Tablas de Renta Fija y Renta Variable con tasas, plazos, cantidades, comisiones y costos.
Los filtros (mes, entidad/broker y monto) y la búsqueda se aplican a las dos tablas; cada tabla
tiene su propia paginación real y la edición de cada inversión.
"""

import math
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Line
from tema import tema
from estado_app import estado
from iconos import con_icono
from kivymd.icon_definitions import md_icons
from utilidades import mes_de, nombre_mes, etiqueta_mes_menu, meses_disponibles, fecha_orden
from componentes.tarjetas import TarjetaBase, EntradaTexto
from componentes.menu_filtro import abrir_menu
from componentes.paginacion import FilaPaginacion
from componentes.modales_edicion import ModalEditarInversionFija, ModalEditarInversionVariable

TAMANO_PAGINA = 5
ETIQUETA_MES = "Este mes"
ETIQUETA_ENTIDAD = "Entidad"
ETIQUETA_MONTO = "Monto"

# (mínimo, máximo) -> texto. El máximo no se incluye; None = sin tope.
RANGOS_MONTO = [
    ((0, 100), "Menos de $100"),
    ((100, 500), "$100 – $500"),
    ((500, 1000), "$500 – $1,000"),
    ((1000, None), "Más de $1,000"),
]

class VistaInversiones(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(do_scroll_x=False, **kwargs)
        self.filtro_busqueda = ""
        self.filtro_mes = None
        self.filtro_entidad = None
        self.filtro_monto = None
        self.pagina_f = 1
        self.pagina_v = 1
        self._construir_ui()
        estado.bind(inversiones_renta_fija=self.refrescar_tablas, inversiones_renta_variable=self.refrescar_tablas)
        
    def _construir_ui(self):
        contenedor = BoxLayout(
            orientation="vertical",
            spacing=20,
            padding=[24, 20, 24, 24],
            size_hint_y=None
        )
        contenedor.bind(minimum_height=contenedor.setter('height'))
        
        # 1. Barra de Filtros y Exportar
        barra_filtros = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=38)
        
        self.in_buscar = EntradaTexto(text="", hint_text="Buscar inversión o descripción...", size_hint_x=0.35)
        self.in_buscar.bind(text=self._al_buscar)
        barra_filtros.add_widget(self.in_buscar)
        
        self.btn_mes = self._crear_boton_filtro()
        self.btn_ent = self._crear_boton_filtro()
        self.btn_mon = self._crear_boton_filtro()
        self.btn_mes.bind(on_release=lambda *a: self._abrir_menu_mes())
        self.btn_ent.bind(on_release=lambda *a: self._abrir_menu_entidad())
        self.btn_mon.bind(on_release=lambda *a: self._abrir_menu_monto())
        self.botones_filtros = [self.btn_mes, self.btn_ent, self.btn_mon]
        for bf in self.botones_filtros:
            barra_filtros.add_widget(bf)
        self._actualizar_botones_filtros()
        
        self.btn_limpiar = Button(text="Limpiar filtros", font_size="12sp", color=tema.texto_atenuado, background_color=[0, 0, 0, 0], size_hint=(None, 1), width=95)
        self.btn_limpiar.bind(on_release=lambda *a: self._limpiar_filtros())
        barra_filtros.add_widget(self.btn_limpiar)
        
        self.btn_exportar = Button(text=con_icono("Exportar historial", "tray-arrow-down"), markup=True, font_size="13sp", bold=True, color=tema.texto_principal, background_color=[0, 0, 0, 0], size_hint=(None, 1), width=145)
        with self.btn_exportar.canvas.before:
            Color(*tema.borde)
            Line(rounded_rectangle=(self.btn_exportar.x, self.btn_exportar.y, self.btn_exportar.width, self.btn_exportar.height, 8), width=1)
        self.btn_exportar.bind(pos=lambda w, *a: self._redibujar_btn_contorno(w), size=lambda w, *a: self._redibujar_btn_contorno(w))
        barra_filtros.add_widget(self.btn_exportar)
        
        contenedor.add_widget(barra_filtros)
        
        # 2. Tabla 1: Renta Fija
        self.tarjeta_fija = TarjetaBase(orientation="vertical", padding=[20, 16, 20, 16], spacing=12, size_hint_y=None)
        self.tarjeta_fija.bind(minimum_height=self.tarjeta_fija.setter('height'))
        
        fila_rf = BoxLayout(orientation="horizontal", size_hint_y=None, height=28)
        self.lbl_rf = Label(text="[b]Todas las transacciones de Renta Fija[/b]", markup=True, font_size="15sp", color=tema.texto_principal, halign="left")
        self.lbl_rf.bind(size=self.lbl_rf.setter('text_size'))
        fila_rf.add_widget(self.lbl_rf)
        
        self.lbl_conteo_rf = Label(text="", font_size="12sp", color=tema.texto_atenuado, size_hint=(None, 1), width=100, halign="right")
        self.lbl_conteo_rf.bind(size=self.lbl_conteo_rf.setter('text_size'))
        fila_rf.add_widget(self.lbl_conteo_rf)
        self.tarjeta_fija.add_widget(fila_rf)
        
        self.enc_f = BoxLayout(orientation="horizontal", size_hint_y=None, height=34, padding=[12, 0, 12, 0])
        with self.enc_f.canvas.before:
            Color(*tema.fondo_sutil)
            RoundedRectangle(pos=self.enc_f.pos, size=self.enc_f.size, radius=[6])
        self.enc_f.bind(pos=lambda w, *a: self._redibujar_enc(w), size=lambda w, *a: self._redibujar_enc(w))
        
        self.celdas_enc_f = [
            self._crear_celda_enc("FECHA", 0.12),
            self._crear_celda_enc("DESCRIPCIÓN", 0.28),
            self._crear_celda_enc("ENTIDAD", 0.22),
            self._crear_celda_enc("TASA", 0.10),
            self._crear_celda_enc("DIAS", 0.08),
            self._crear_celda_enc("MONTO", 0.14, alineacion="right"),
            self._crear_celda_enc("ACCIONES", 0.06, alineacion="center")
        ]
        for c in self.celdas_enc_f:
            self.enc_f.add_widget(c)
        self.tarjeta_fija.add_widget(self.enc_f)
        
        self.pag_f = FilaPaginacion(unidad="movimientos", tamano=TAMANO_PAGINA, al_cambiar=self._al_cambiar_pagina_f, tam_boton=26, alto=32, padding=[8, 6, 8, 0])
        
        self.caja_filas_fija = BoxLayout(orientation="vertical", spacing=2, size_hint_y=None)
        self.caja_filas_fija.bind(minimum_height=self.caja_filas_fija.setter('height'))
        self._cargar_filas_fija()
        self.tarjeta_fija.add_widget(self.caja_filas_fija)
        self.tarjeta_fija.add_widget(self.pag_f)
        
        contenedor.add_widget(self.tarjeta_fija)
        
        # 3. Tabla 2: Renta Variable
        self.tarjeta_var = TarjetaBase(orientation="vertical", padding=[20, 16, 20, 16], spacing=12, size_hint_y=None)
        self.tarjeta_var.bind(minimum_height=self.tarjeta_var.setter('height'))
        
        fila_rv = BoxLayout(orientation="horizontal", size_hint_y=None, height=28)
        self.lbl_rv = Label(text="[b]Todas las transacciones de Renta Variable[/b]", markup=True, font_size="15sp", color=tema.texto_principal, halign="left")
        self.lbl_rv.bind(size=self.lbl_rv.setter('text_size'))
        fila_rv.add_widget(self.lbl_rv)
        
        self.lbl_conteo_rv = Label(text="", font_size="12sp", color=tema.texto_atenuado, size_hint=(None, 1), width=100, halign="right")
        self.lbl_conteo_rv.bind(size=self.lbl_conteo_rv.setter('text_size'))
        fila_rv.add_widget(self.lbl_conteo_rv)
        self.tarjeta_var.add_widget(fila_rv)
        
        self.enc_v = BoxLayout(orientation="horizontal", size_hint_y=None, height=34, padding=[12, 0, 12, 0])
        with self.enc_v.canvas.before:
            Color(*tema.fondo_sutil)
            RoundedRectangle(pos=self.enc_v.pos, size=self.enc_v.size, radius=[6])
        self.enc_v.bind(pos=lambda w, *a: self._redibujar_enc(w), size=lambda w, *a: self._redibujar_enc(w))
        
        self.celdas_enc_v = [
            self._crear_celda_enc("FECHA", 0.10),
            self._crear_celda_enc("ACCION", 0.28),
            self._crear_celda_enc("BROKER", 0.14),
            self._crear_celda_enc("COSTO", 0.08),
            self._crear_celda_enc("CANT", 0.07),
            self._crear_celda_enc("MONTO", 0.11, alineacion="right"),
            self._crear_celda_enc("COMISION", 0.09, alineacion="right"),
            self._crear_celda_enc("COSTO TOTAL", 0.11, alineacion="right"),
            self._crear_celda_enc("ACC", 0.05, alineacion="center")
        ]
        for c in self.celdas_enc_v:
            self.enc_v.add_widget(c)
        self.tarjeta_var.add_widget(self.enc_v)
        
        self.pag_v = FilaPaginacion(unidad="movimientos", tamano=TAMANO_PAGINA, al_cambiar=self._al_cambiar_pagina_v, tam_boton=26, alto=32, padding=[8, 6, 8, 0])
        
        self.caja_filas_var = BoxLayout(orientation="vertical", spacing=2, size_hint_y=None)
        self.caja_filas_var.bind(minimum_height=self.caja_filas_var.setter('height'))
        self._cargar_filas_var()
        self.tarjeta_var.add_widget(self.caja_filas_var)
        self.tarjeta_var.add_widget(self.pag_v)
        
        contenedor.add_widget(self.tarjeta_var)
        self.add_widget(contenedor)
        
    def _crear_celda_enc(self, texto, size_hint_x=0.2, alineacion="left"):
        lbl = Label(text=texto, font_size="11sp", bold=True, color=tema.texto_atenuado, size_hint_x=size_hint_x, halign=alineacion)
        lbl.bind(size=lbl.setter('text_size'))
        tema.bind(texto_atenuado=lambda *a, l=lbl: setattr(l, 'color', tema.texto_atenuado))
        return lbl
        
    def _crear_boton_filtro(self):
        b = Button(text="", markup=True, font_size="12sp", color=tema.texto_secundario, background_color=[0, 0, 0, 0], size_hint=(None, 1), width=105)
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
        
    def _redibujar_btn_contorno(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.borde)
            Line(rounded_rectangle=(w.x, w.y, w.width, w.height, 8), width=1)
            
    def _redibujar_enc(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.fondo_sutil)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[6])
            
    # ------------------------------------------------------------------ filtros
    def _texto_monto(self):
        for rango, texto in RANGOS_MONTO:
            if rango == self.filtro_monto:
                return texto
        return ETIQUETA_MONTO
        
    def _actualizar_botones_filtros(self):
        """Pone en cada botón el filtro elegido (o su nombre por defecto) y lo resalta si está activo."""
        estados = [
            (self.btn_mes, nombre_mes(self.filtro_mes) if self.filtro_mes else ETIQUETA_MES, self.filtro_mes is not None, True),
            (self.btn_ent, self.filtro_entidad or ETIQUETA_ENTIDAD, self.filtro_entidad is not None, False),
            (self.btn_mon, self._texto_monto(), self.filtro_monto is not None, False),
        ]
        for b, etiqueta, activo, icono_izquierda in estados:
            b.filtro_activo = activo
            if icono_izquierda:
                b.text = con_icono(etiqueta, "calendar-month-outline")
            else:
                b.text = con_icono(etiqueta, "chevron-down", derecha=True)
            b.bold = activo
            b.color = tema.primario if activo else tema.texto_secundario
            b.texture_update()
            b.width = max(105, b.texture_size[0] + 34)
            self._redibujar_btn_filtro(b)
            
    def _abrir_menu_mes(self):
        fechas = [i["fecha"] for i in estado.inversiones_renta_fija] + [i["fecha"] for i in estado.inversiones_renta_variable]
        opciones = [(None, "Todos los meses")] + [(m, etiqueta_mes_menu(m)) for m in meses_disponibles(fechas)]
        abrir_menu(self.btn_mes, opciones, self.filtro_mes, self._elegir_mes, ancho=230)
        
    def _abrir_menu_entidad(self):
        entidades = {i["entidad"] for i in estado.inversiones_renta_fija} | {i["broker"] for i in estado.inversiones_renta_variable}
        opciones = [(None, "Todas las entidades")] + [(e, e) for e in sorted(entidades, key=str.lower)]
        abrir_menu(self.btn_ent, opciones, self.filtro_entidad, self._elegir_entidad, ancho=240)
        
    def _abrir_menu_monto(self):
        opciones = [(None, "Cualquier monto")] + [(rango, texto) for rango, texto in RANGOS_MONTO]
        abrir_menu(self.btn_mon, opciones, self.filtro_monto, self._elegir_monto, ancho=200)
        
    def _elegir_mes(self, valor):
        self.filtro_mes = valor
        self._aplicar_filtros()
        
    def _elegir_entidad(self, valor):
        self.filtro_entidad = valor
        self._aplicar_filtros()
        
    def _elegir_monto(self, valor):
        self.filtro_monto = valor
        self._aplicar_filtros()
        
    def _aplicar_filtros(self):
        self.pagina_f = 1
        self.pagina_v = 1
        self._actualizar_botones_filtros()
        self._cargar_filas_fija()
        self._cargar_filas_var()
        
    def _pasa_filtros(self, item, campos_busqueda, entidad):
        q = self.filtro_busqueda.lower()
        if q and not any(q in str(item[c]).lower() for c in campos_busqueda):
            return False
        if self.filtro_mes is not None and mes_de(item["fecha"]) != self.filtro_mes:
            return False
        if self.filtro_entidad is not None and entidad != self.filtro_entidad:
            return False
        if self.filtro_monto is not None:
            minimo, maximo = self.filtro_monto
            if item["monto"] < minimo or (maximo is not None and item["monto"] >= maximo):
                return False
        return True
        
    def _filtrados_fija(self):
        lista = [i for i in estado.inversiones_renta_fija if self._pasa_filtros(i, ("descripcion", "entidad"), i["entidad"])]
        return sorted(lista, key=lambda r: fecha_orden(r["fecha"]), reverse=True)
        
    def _filtrados_var(self):
        lista = [i for i in estado.inversiones_renta_variable if self._pasa_filtros(i, ("accion", "broker"), i["broker"])]
        return sorted(lista, key=lambda r: fecha_orden(r["fecha"]), reverse=True)
        
    # ------------------------------------------------------------------- tablas
    def _cargar_filas_fija(self):
        self.caja_filas_fija.clear_widgets()
        filtrados = self._filtrados_fija()
        total = len(filtrados)
        self.pagina_f = min(self.pagina_f, max(1, math.ceil(total / TAMANO_PAGINA)))
        inicio = (self.pagina_f - 1) * TAMANO_PAGINA
        visibles = filtrados[inicio:inicio + TAMANO_PAGINA]
        
        if not visibles:
            self.caja_filas_fija.add_widget(Label(text="No hay inversiones que coincidan con los filtros.", font_size="13sp", color=tema.texto_atenuado, size_hint_y=None, height=70))
        
        for item in visibles:
            fila = BoxLayout(orientation="horizontal", size_hint_y=None, height=42, padding=[12, 0, 12, 0])
            with fila.canvas.before:
                Color(*tema.borde_claro)
                Line(points=[fila.x, fila.y, fila.x + fila.width, fila.y], width=1)
            fila.bind(pos=lambda w, *a: self._redibujar_linea_fila(w), size=lambda w, *a: self._redibujar_linea_fila(w))
            
            lbl_d = Label(text=item['fecha'], font_size="12sp", color=tema.texto_atenuado, size_hint_x=0.12, halign="left")
            lbl_d.bind(size=lbl_d.setter('text_size'))
            fila.add_widget(lbl_d)
            
            lbl_desc = Label(text=f"[b]{item['descripcion']}[/b]", markup=True, font_size="13sp", color=tema.texto_principal, size_hint_x=0.28, halign="left")
            lbl_desc.bind(size=lbl_desc.setter('text_size'))
            fila.add_widget(lbl_desc)
            
            lbl_ent = Label(text=item['entidad'], font_size="12sp", color=tema.texto_secundario, size_hint_x=0.22, halign="left")
            lbl_ent.bind(size=lbl_ent.setter('text_size'))
            fila.add_widget(lbl_ent)
            
            lbl_tasa = Label(text=item['tasa'], font_size="12sp", color=tema.texto_secundario, size_hint_x=0.10, halign="left")
            lbl_tasa.bind(size=lbl_tasa.setter('text_size'))
            fila.add_widget(lbl_tasa)
            
            lbl_dias = Label(text=item['dias'], font_size="12sp", color=tema.texto_secundario, size_hint_x=0.08, halign="left")
            lbl_dias.bind(size=lbl_dias.setter('text_size'))
            fila.add_widget(lbl_dias)
            
            lbl_m = Label(text=f"[b]$ {item['monto']:,.2f}[/b]", markup=True, font_size="13sp", color=tema.texto_principal, size_hint_x=0.14, halign="right")
            lbl_m.bind(size=lbl_m.setter('text_size'))
            fila.add_widget(lbl_m)
            
            btn_editar = Button(text=md_icons.get("pencil-outline", ""), font_name="Icons", font_size="14sp", color=tema.primario, background_color=[0, 0, 0, 0], size_hint_x=0.06)
            btn_editar.bind(on_release=lambda *a, it=item: ModalEditarInversionFija(it).open())
            fila.add_widget(btn_editar)
            
            self.caja_filas_fija.add_widget(fila)
            
        self.lbl_conteo_rf.text = f"{total} movimientos"
        self.pag_f.actualizar(total, self.pagina_f)
            
    def _cargar_filas_var(self):
        self.caja_filas_var.clear_widgets()
        filtrados = self._filtrados_var()
        total = len(filtrados)
        self.pagina_v = min(self.pagina_v, max(1, math.ceil(total / TAMANO_PAGINA)))
        inicio = (self.pagina_v - 1) * TAMANO_PAGINA
        visibles = filtrados[inicio:inicio + TAMANO_PAGINA]
        
        if not visibles:
            self.caja_filas_var.add_widget(Label(text="No hay inversiones que coincidan con los filtros.", font_size="13sp", color=tema.texto_atenuado, size_hint_y=None, height=70))
        
        for item in visibles:
            fila = BoxLayout(orientation="horizontal", size_hint_y=None, height=42, padding=[12, 0, 12, 0])
            with fila.canvas.before:
                Color(*tema.borde_claro)
                Line(points=[fila.x, fila.y, fila.x + fila.width, fila.y], width=1)
            fila.bind(pos=lambda w, *a: self._redibujar_linea_fila(w), size=lambda w, *a: self._redibujar_linea_fila(w))
            
            lbl_d = Label(text=item['fecha'], font_size="11sp", color=tema.texto_atenuado, size_hint_x=0.10, halign="left")
            lbl_d.bind(size=lbl_d.setter('text_size'))
            fila.add_widget(lbl_d)
            
            lbl_acc = Label(text=f"[b]{item['accion']}[/b]", markup=True, font_size="12sp", color=tema.texto_principal, size_hint_x=0.28, halign="left")
            lbl_acc.bind(size=lbl_acc.setter('text_size'))
            fila.add_widget(lbl_acc)
            
            lbl_brk = Label(text=item['broker'], font_size="11sp", color=tema.texto_secundario, size_hint_x=0.14, halign="left")
            lbl_brk.bind(size=lbl_brk.setter('text_size'))
            fila.add_widget(lbl_brk)
            
            lbl_cst = Label(text=f"{item['costo']:.2f}", font_size="11sp", color=tema.texto_secundario, size_hint_x=0.08, halign="left")
            lbl_cst.bind(size=lbl_cst.setter('text_size'))
            fila.add_widget(lbl_cst)
            
            lbl_cant = Label(text=str(item['cantidad']), font_size="11sp", color=tema.texto_secundario, size_hint_x=0.07, halign="left")
            lbl_cant.bind(size=lbl_cant.setter('text_size'))
            fila.add_widget(lbl_cant)
            
            lbl_m = Label(text=f"$ {item['monto']:,.2f}", font_size="12sp", color=tema.texto_principal, size_hint_x=0.11, halign="right")
            lbl_m.bind(size=lbl_m.setter('text_size'))
            fila.add_widget(lbl_m)
            
            lbl_com = Label(text=f"$ {item['comision']:,.2f}", font_size="11sp", color=tema.texto_atenuado, size_hint_x=0.09, halign="right")
            lbl_com.bind(size=lbl_com.setter('text_size'))
            fila.add_widget(lbl_com)
            
            lbl_tot = Label(text=f"[b]$ {item['costo_total']:,.2f}[/b]", markup=True, font_size="12sp", color=tema.texto_principal, size_hint_x=0.11, halign="right")
            lbl_tot.bind(size=lbl_tot.setter('text_size'))
            fila.add_widget(lbl_tot)
            
            btn_editar = Button(text=md_icons.get("pencil-outline", ""), font_name="Icons", font_size="14sp", color=tema.primario, background_color=[0, 0, 0, 0], size_hint_x=0.05)
            btn_editar.bind(on_release=lambda *a, it=item: ModalEditarInversionVariable(it).open())
            fila.add_widget(btn_editar)
            
            self.caja_filas_var.add_widget(fila)
            
        self.lbl_conteo_rv.text = f"{total} movimientos"
        self.pag_v.actualizar(total, self.pagina_v)
            
    def _redibujar_linea_fila(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.borde_claro)
            Line(points=[w.x, w.y, w.x + w.width, w.y], width=1)
            
    def _al_cambiar_pagina_f(self, pagina):
        self.pagina_f = pagina
        self._cargar_filas_fija()
        
    def _al_cambiar_pagina_v(self, pagina):
        self.pagina_v = pagina
        self._cargar_filas_var()
            
    def _al_buscar(self, instance, value):
        self.filtro_busqueda = value.strip()
        self.pagina_f = 1
        self.pagina_v = 1
        self._cargar_filas_fija()
        self._cargar_filas_var()
        
    def _limpiar_filtros(self):
        self.filtro_busqueda = ""
        self.filtro_mes = None
        self.filtro_entidad = None
        self.filtro_monto = None
        self.pagina_f = 1
        self.pagina_v = 1
        self.in_buscar.text = ""
        self._actualizar_botones_filtros()
        self._cargar_filas_fija()
        self._cargar_filas_var()
        
    def refrescar_tablas(self, *args):
        self._cargar_filas_fija()
        self._cargar_filas_var()
        
    def actualizar_tema(self, *args):
        self.in_buscar._al_cambiar_tema()
        self._actualizar_botones_filtros()
        self.btn_limpiar.color = tema.texto_atenuado
        self._redibujar_btn_contorno(self.btn_exportar)
        self.btn_exportar.color = tema.texto_principal
        self.lbl_rf.color = tema.texto_principal
        self.lbl_conteo_rf.color = tema.texto_atenuado
        self._redibujar_enc(self.enc_f)
        for c in self.celdas_enc_f:
            c.color = tema.texto_atenuado
        self.pag_f.actualizar_tema()
        self.lbl_rv.color = tema.texto_principal
        self.lbl_conteo_rv.color = tema.texto_atenuado
        self._redibujar_enc(self.enc_v)
        for c in self.celdas_enc_v:
            c.color = tema.texto_atenuado
        self.pag_v.actualizar_tema()
        self._cargar_filas_fija()
        self._cargar_filas_var()
