"""
CENTS - Pantalla de Presupuestos y Categorías
Tarjetas de límites por categoría con porcentajes y barras de progreso.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Line
from tema import tema
from estado_app import estado
from componentes.tarjetas import TarjetaBase, TarjetaMetrica, TarjetaPresupuestoCategoria
from componentes.modales import ModalNuevoPresupuesto

class VistaPresupuestos(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(do_scroll_x=False, **kwargs)
        self._construir_ui()
        estado.bind(presupuestos=self.refrescar_grid)
        
    def _construir_ui(self):
        contenedor = BoxLayout(
            orientation="vertical",
            spacing=20,
            padding=[24, 20, 24, 24],
            size_hint_y=None
        )
        contenedor.bind(minimum_height=contenedor.setter('height'))
        
        # 1. Fila de acciones superiores
        fila_acciones = BoxLayout(orientation="horizontal", size_hint_y=None, height=38)
        self.lbl_sub = Label(text="Controla cuánto puedes gastar en cada área.", font_size="13sp", color=tema.texto_secundario, halign="left")
        self.lbl_sub.bind(size=self.lbl_sub.setter('text_size'))
        fila_acciones.add_widget(self.lbl_sub)
        
        caja_btn = BoxLayout(orientation="horizontal", spacing=10, size_hint=(None, 1))
        caja_btn.bind(minimum_width=caja_btn.setter('width'))
        
        self.btn_editar = Button(text="Editar límites", font_size="12sp", color=tema.texto_principal, background_color=[0, 0, 0, 0], size_hint=(None, 1), width=110)
        with self.btn_editar.canvas.before:
            Color(*tema.borde)
            Line(rounded_rectangle=(self.btn_editar.x, self.btn_editar.y, self.btn_editar.width, self.btn_editar.height, 8), width=1)
        self.btn_editar.bind(pos=lambda w, *a: self._redibujar_btn_contorno(w), size=lambda w, *a: self._redibujar_btn_contorno(w))
        caja_btn.add_widget(self.btn_editar)
        
        self.btn_nuevo = Button(text="＋ Nuevo presupuesto", font_size="12sp", bold=True, color=[1, 1, 1, 1], background_color=[0, 0, 0, 0], size_hint=(None, 1), width=160)
        with self.btn_nuevo.canvas.before:
            Color(*tema.primario)
            RoundedRectangle(pos=self.btn_nuevo.pos, size=self.btn_nuevo.size, radius=[8])
        self.btn_nuevo.bind(pos=lambda w, *a: self._redibujar_btn_primario(w), size=lambda w, *a: self._redibujar_btn_primario(w))
        self.btn_nuevo.bind(on_release=lambda *a: self.abrir_modal_nuevo_presupuesto())
        caja_btn.add_widget(self.btn_nuevo)
        
        fila_acciones.add_widget(caja_btn)
        contenedor.add_widget(fila_acciones)
        
        # 2. Tres Tarjetas de Resumen
        fila_kpi = GridLayout(cols=3, spacing=16, size_hint_y=None, height=115)
        
        self.tarjeta_total = TarjetaMetrica(
            titulo="Presupuesto mensual total",
            valor=f"$ {estado.presupuesto_total:,.2f}"
        )
        pct = int((estado.total_gastado / estado.presupuesto_total) * 100) if estado.presupuesto_total > 0 else 0
        self.tarjeta_gastado = TarjetaMetrica(
            titulo="Gastado",
            valor=f"$ {estado.total_gastado:,.2f}",
            texto_badge=f"{pct}% utilizado",
            es_positivo=False
        )
        self.tarjeta_disp = TarjetaMetrica(
            titulo="Disponible",
            valor=f"$ {estado.presupuesto_total - estado.total_gastado:,.2f}"
        )
        
        fila_kpi.add_widget(self.tarjeta_total)
        fila_kpi.add_widget(self.tarjeta_gastado)
        fila_kpi.add_widget(self.tarjeta_disp)
        contenedor.add_widget(fila_kpi)
        
        # 3. Sección: Límites por categoría
        self.lbl_sec1 = Label(text="[b]Límites por categoría[/b]", markup=True, font_size="16sp", color=tema.texto_principal, size_hint_y=None, height=28, halign="left")
        self.lbl_sec1.bind(size=self.lbl_sec1.setter('text_size'))
        contenedor.add_widget(self.lbl_sec1)
        
        self.cuadricula = GridLayout(cols=3, spacing=16, size_hint_y=None)
        self.cuadricula.bind(minimum_height=self.cuadricula.setter('height'))
        self._cargar_cuadricula()
        contenedor.add_widget(self.cuadricula)
        
        # 4. Sección: Tus categorías
        self.tarjeta_cat = TarjetaBase(orientation="vertical", padding=[20, 16, 20, 16], spacing=12, size_hint_y=None, height=120)
        self.lbl_c_tit = Label(text="[b]Tus categorías[/b]", markup=True, font_size="15sp", color=tema.texto_principal, size_hint_y=None, height=20, halign="left")
        self.lbl_c_tit.bind(size=self.lbl_c_tit.setter('text_size'))
        self.lbl_c_sub = Label(text="Organiza tus gastos con categorías personalizadas.", font_size="12sp", color=tema.texto_atenuado, size_hint_y=None, height=18, halign="left")
        self.lbl_c_sub.bind(size=self.lbl_c_sub.setter('text_size'))
        self.tarjeta_cat.add_widget(self.lbl_c_tit)
        self.tarjeta_cat.add_widget(self.lbl_c_sub)
        
        self.fila_chips = BoxLayout(orientation="horizontal", spacing=8, size_hint_y=None, height=32)
        self._cargar_chips()
        self.tarjeta_cat.add_widget(self.fila_chips)
        contenedor.add_widget(self.tarjeta_cat)
        
        self.add_widget(contenedor)
        
    def _cargar_cuadricula(self):
        self.cuadricula.clear_widgets()
        for p in estado.presupuestos:
            tarjeta = TarjetaPresupuestoCategoria(
                nombre_categoria=p["categoria"],
                gastado=p["gastado"],
                limite=p["limite"],
                porcentaje=p["porcentaje"],
                estado=p["estado"],
                color=p["color"],
                size_hint_y=None,
                height=130
            )
            self.cuadricula.add_widget(tarjeta)
            
    def _redibujar_btn_contorno(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.borde)
            Line(rounded_rectangle=(w.x, w.y, w.width, w.height, 8), width=1)
            
    def _redibujar_btn_primario(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.primario)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[8])
            
    def _redibujar_chip(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.fondo_sutil)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[16])
            Color(*tema.borde)
            Line(rounded_rectangle=(w.x, w.y, w.width, w.height, 16), width=1)
            
    def _cargar_chips(self):
        self.fila_chips.clear_widgets()
        for cat in estado.categorias:
            chip = Button(text=cat, font_size="12sp", color=tema.texto_secundario, background_color=[0, 0, 0, 0], size_hint=(None, 1))
            chip.bind(texture_size=lambda *a, c=chip: setattr(c, 'width', c.texture_size[0] + 24))
            with chip.canvas.before:
                Color(*tema.fondo_sutil)
                RoundedRectangle(pos=chip.pos, size=chip.size, radius=[16])
                Color(*tema.borde)
                Line(rounded_rectangle=(chip.x, chip.y, chip.width, chip.height, 16), width=1)
            chip.bind(pos=lambda w, *a: self._redibujar_chip(w), size=lambda w, *a: self._redibujar_chip(w))
            self.fila_chips.add_widget(chip)
            
        self.btn_nueva_cat = Button(text="＋ Nueva categoría", font_size="12sp", bold=True, color=tema.primario, background_color=[0, 0, 0, 0], size_hint=(None, 1), width=140)
        with self.btn_nueva_cat.canvas.before:
            Color(*tema.borde)
            Line(rounded_rectangle=(self.btn_nueva_cat.x, self.btn_nueva_cat.y, self.btn_nueva_cat.width, self.btn_nueva_cat.height, 16), width=1)
        self.btn_nueva_cat.bind(pos=lambda w, *a: self._redibujar_chip(w), size=lambda w, *a: self._redibujar_chip(w))
        self.fila_chips.add_widget(self.btn_nueva_cat)
        
    def abrir_modal_nuevo_presupuesto(self):
        dialogo = ModalNuevoPresupuesto(al_guardar=self._cargar_cuadricula)
        dialogo.open()
        
    def refrescar_grid(self, *args):
        self._cargar_cuadricula()
        
    def actualizar_tema(self, *args):
        self.lbl_sub.color = tema.texto_secundario
        self._redibujar_btn_contorno(self.btn_editar)
        self.btn_editar.color = tema.texto_principal
        self._redibujar_btn_primario(self.btn_nuevo)
        self.tarjeta_total.actualizar_tema()
        self.tarjeta_gastado.actualizar_tema()
        self.tarjeta_disp.actualizar_tema()
        self.lbl_sec1.color = tema.texto_principal
        self.lbl_c_tit.color = tema.texto_principal
        self.lbl_c_sub.color = tema.texto_atenuado
        self._cargar_cuadricula()
        self._cargar_chips()
