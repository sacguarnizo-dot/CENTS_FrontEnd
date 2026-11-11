"""
CENTS - Pantalla de Inicio (Dashboard Principal)
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from kivy.graphics import Color, RoundedRectangle, Line
from tema import tema
from estado_app import estado
from componentes.tarjetas import TarjetaBase, TarjetaMetrica
from componentes.graficos import ContenedorGraficoDonut, WidgetGraficoBarras

class VistaInicio(ScrollView):
    al_ver_todos_los_gastos = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(do_scroll_x=False, **kwargs)
        self._construir_ui()
        estado.bind(total_gastado=self.actualizar_datos)
        
    def _construir_ui(self):
        contenedor = BoxLayout(
            orientation="vertical",
            spacing=20,
            padding=[24, 20, 24, 24],
            size_hint_y=None
        )
        contenedor.bind(minimum_height=contenedor.setter('height'))
        
        # 1. Cuatro tarjetas métricas superiores (KPIs)
        fila_kpi = GridLayout(cols=4, spacing=16, size_hint_y=None, height=115)
        
        self.tarjeta1 = TarjetaMetrica(
            titulo="Total gastado",
            valor=f"$ {estado.total_gastado:,.2f}",
            texto_badge="↑ 8.2% vs. mes anterior",
            es_positivo=True
        )
        self.tarjeta2 = TarjetaMetrica(
            titulo="Presupuesto restante",
            valor=f"$ {estado.presupuesto_total - estado.total_gastado:,.2f}",
            subtitulo=f"De $ {estado.presupuesto_total:,.2f}"
        )
        self.tarjeta3 = TarjetaMetrica(
            titulo="Gasto promedio diario",
            valor=f"$ {estado.gasto_promedio_diario:,.2f}",
            subtitulo="En los últimos 30 días"
        )
        self.tarjeta4 = TarjetaMetrica(
            titulo="Mayor categoría",
            valor="Alimentación",
            subtitulo="32% de tus gastos"
        )
        
        fila_kpi.add_widget(self.tarjeta1)
        fila_kpi.add_widget(self.tarjeta2)
        fila_kpi.add_widget(self.tarjeta3)
        fila_kpi.add_widget(self.tarjeta4)
        contenedor.add_widget(fila_kpi)
        
        # 2. Fila de Gráficos (Dona y Barras de 6 Meses)
        fila_graficos = GridLayout(cols=2, spacing=16, size_hint_y=None, height=270)
        
        # Gráfico Izquierdo: Gastos por categoría
        self.tarjeta_dona = TarjetaBase(orientation="vertical", padding=[20, 16, 20, 16], spacing=10)
        enc_d = BoxLayout(orientation="vertical", size_hint_y=None, height=40, spacing=2)
        self.lbl_dt = Label(text="[b]Gastos por categoría[/b]", markup=True, font_size="15sp", color=tema.texto_principal, halign="left")
        self.lbl_dt.bind(size=self.lbl_dt.setter('text_size'))
        self.lbl_dsub = Label(text="Distribución de tus consumos", font_size="12sp", color=tema.texto_atenuado, halign="left")
        self.lbl_dsub.bind(size=self.lbl_dsub.setter('text_size'))
        enc_d.add_widget(self.lbl_dt)
        enc_d.add_widget(self.lbl_dsub)
        self.tarjeta_dona.add_widget(enc_d)
        self.donut_widget = ContenedorGraficoDonut()
        self.tarjeta_dona.add_widget(self.donut_widget)
        fila_graficos.add_widget(self.tarjeta_dona)
        
        # Gráfico Derecho: Historial de gastos
        self.tarjeta_barras = TarjetaBase(orientation="vertical", padding=[20, 16, 20, 16], spacing=10)
        enc_b = BoxLayout(orientation="vertical", size_hint_y=None, height=40, spacing=2)
        self.lbl_bt = Label(text="[b]Historial de gastos[/b]", markup=True, font_size="15sp", color=tema.texto_principal, halign="left")
        self.lbl_bt.bind(size=self.lbl_bt.setter('text_size'))
        self.lbl_bsub = Label(text="Comparativa de los últimos 6 meses", font_size="12sp", color=tema.texto_atenuado, halign="left")
        self.lbl_bsub.bind(size=self.lbl_bsub.setter('text_size'))
        enc_b.add_widget(self.lbl_bt)
        enc_b.add_widget(self.lbl_bsub)
        self.tarjeta_barras.add_widget(enc_b)
        
        self.grafico_barras = WidgetGraficoBarras(size_hint=(1, 1))
        self.tarjeta_barras.add_widget(self.grafico_barras)
        
        fila_meses = BoxLayout(orientation="horizontal", size_hint_y=None, height=20, padding=[24, 0, 24, 0])
        self.labels_meses = []
        for m in ["Jun", "Jul", "Ago", "Sep", "Oct", "Nov"]:
            lbl_m = Label(text=m, font_size="11sp", color=tema.texto_atenuado, halign="center")
            self.labels_meses.append(lbl_m)
            fila_meses.add_widget(lbl_m)
        self.tarjeta_barras.add_widget(fila_meses)
        
        fila_graficos.add_widget(self.tarjeta_barras)
        contenedor.add_widget(fila_graficos)
        
        # 3. Tarjeta Inferior: Últimos movimientos
        self.tarjeta_tabla = TarjetaBase(orientation="vertical", padding=[20, 16, 20, 16], spacing=12, size_hint_y=None)
        self.tarjeta_tabla.bind(minimum_height=self.tarjeta_tabla.setter('height'))
        
        enc_t = BoxLayout(orientation="horizontal", size_hint_y=None, height=32)
        self.lbl_tt = Label(text="[b]Últimos movimientos[/b]", markup=True, font_size="16sp", color=tema.texto_principal, halign="left")
        self.lbl_tt.bind(size=self.lbl_tt.setter('text_size'))
        enc_t.add_widget(self.lbl_tt)
        
        self.btn_ver_todos = Button(
            text="Ver todos →",
            font_size="13sp",
            bold=True,
            color=tema.primario,
            background_color=[0, 0, 0, 0],
            size_hint=(None, 1),
            width=100
        )
        self.btn_ver_todos.bind(on_release=lambda *a: self.ver_todos())
        enc_t.add_widget(self.btn_ver_todos)
        self.tarjeta_tabla.add_widget(enc_t)
        
        # Encabezado de la tabla
        self.enc_col = BoxLayout(orientation="horizontal", size_hint_y=None, height=32, padding=[12, 0, 12, 0])
        with self.enc_col.canvas.before:
            Color(*tema.fondo_sutil)
            RoundedRectangle(pos=self.enc_col.pos, size=self.enc_col.size, radius=[6])
        self.enc_col.bind(pos=lambda w, *a: self._redibujar_enc_col(w), size=lambda w, *a: self._redibujar_enc_col(w))
        
        self.celdas_enc = [
            self._crear_celda_enc("DESCRIPCIÓN", size_hint_x=0.4),
            self._crear_celda_enc("CATEGORÍA", size_hint_x=0.25),
            self._crear_celda_enc("FECHA", size_hint_x=0.2),
            self._crear_celda_enc("MONTO", size_hint_x=0.15, alineacion="right")
        ]
        for c in self.celdas_enc:
            self.enc_col.add_widget(c)
        self.tarjeta_tabla.add_widget(self.enc_col)
        
        # Filas
        self.caja_filas = BoxLayout(orientation="vertical", spacing=2, size_hint_y=None)
        self.caja_filas.bind(minimum_height=self.caja_filas.setter('height'))
        self._cargar_filas()
        self.tarjeta_tabla.add_widget(self.caja_filas)
        
        contenedor.add_widget(self.tarjeta_tabla)
        self.add_widget(contenedor)
        
    def _crear_celda_enc(self, texto, size_hint_x=0.25, alineacion="left"):
        lbl = Label(text=texto, font_size="11sp", bold=True, color=tema.texto_atenuado, size_hint_x=size_hint_x, halign=alineacion)
        lbl.bind(size=lbl.setter('text_size'))
        tema.bind(texto_atenuado=lambda *a, l=lbl: setattr(l, 'color', tema.texto_atenuado))
        return lbl
        
    def _redibujar_enc_col(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.fondo_sutil)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[6])
            
    def _cargar_filas(self):
        self.caja_filas.clear_widgets()
        recientes = estado.gastos[:5]
        for item in recientes:
            fila = BoxLayout(orientation="horizontal", size_hint_y=None, height=44, padding=[12, 0, 12, 0])
            with fila.canvas.before:
                Color(*tema.borde_claro)
                Line(points=[fila.x, fila.y, fila.x + fila.width, fila.y], width=1)
            fila.bind(pos=lambda w, *a: self._redibujar_linea_fila(w), size=lambda w, *a: self._redibujar_linea_fila(w))
            
            lbl_desc = Label(text=f"[b]{item['descripcion']}[/b]", markup=True, font_size="13sp", color=tema.texto_principal, size_hint_x=0.4, halign="left")
            lbl_desc.bind(size=lbl_desc.setter('text_size'))
            tema.bind(texto_principal=lambda *a, l=lbl_desc: setattr(l, 'color', tema.texto_principal))
            fila.add_widget(lbl_desc)
            
            lbl_cat = Label(text=item['categoria'], font_size="13sp", color=tema.texto_secundario, size_hint_x=0.25, halign="left")
            lbl_cat.bind(size=lbl_cat.setter('text_size'))
            tema.bind(texto_secundario=lambda *a, l=lbl_cat: setattr(l, 'color', tema.texto_secundario))
            fila.add_widget(lbl_cat)
            
            lbl_fecha = Label(text=item['fecha'], font_size="12sp", color=tema.texto_atenuado, size_hint_x=0.2, halign="left")
            lbl_fecha.bind(size=lbl_fecha.setter('text_size'))
            tema.bind(texto_atenuado=lambda *a, l=lbl_fecha: setattr(l, 'color', tema.texto_atenuado))
            fila.add_widget(lbl_fecha)
            
            lbl_monto = Label(text=f"[b]$ {item['monto']:,.2f}[/b]", markup=True, font_size="13sp", color=tema.texto_principal, size_hint_x=0.15, halign="right")
            lbl_monto.bind(size=lbl_monto.setter('text_size'))
            tema.bind(texto_principal=lambda *a, l=lbl_monto: setattr(l, 'color', tema.texto_principal))
            fila.add_widget(lbl_monto)
            
            self.caja_filas.add_widget(fila)
            
    def _redibujar_linea_fila(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.borde_claro)
            Line(points=[w.x, w.y, w.x + w.width, w.y], width=1)
            
    def actualizar_datos(self, *args):
        self._cargar_filas()
        
    def actualizar_tema(self, *args):
        self.tarjeta1.actualizar_tema()
        self.tarjeta2.actualizar_tema()
        self.tarjeta3.actualizar_tema()
        self.tarjeta4.actualizar_tema()
        self.lbl_dt.color = tema.texto_principal
        self.lbl_dsub.color = tema.texto_atenuado
        self.donut_widget.actualizar_tema()
        self.lbl_bt.color = tema.texto_principal
        self.lbl_bsub.color = tema.texto_atenuado
        self.grafico_barras.actualizar_canvas()
        for lbl_m in self.labels_meses:
            lbl_m.color = tema.texto_atenuado
        self.lbl_tt.color = tema.texto_principal
        self.btn_ver_todos.color = tema.primario
        self._redibujar_enc_col(self.enc_col)
        for c in self.celdas_enc:
            c.color = tema.texto_atenuado
        self._cargar_filas()
        
    def ver_todos(self):
        if self.al_ver_todos_los_gastos:
            self.al_ver_todos_los_gastos()
