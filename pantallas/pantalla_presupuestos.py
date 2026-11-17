"""
CENTS - Pantalla de Presupuestos y Categorías
Tarjetas de límites por categoría con porcentajes y barras de progreso.
"Tus categorías" funciona como filtro de las tarjetas y permite crear categorías nuevas.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Line
from tema import tema
from estado_app import estado
from iconos import con_icono
from componentes.tarjetas import TarjetaBase, TarjetaMetrica, TarjetaPresupuestoCategoria
from componentes.modales import ModalNuevoPresupuesto
from componentes.modales_edicion import ModalNuevaCategoria


class ContenedorFlujo(BoxLayout):
    """Acomoda sus elementos de izquierda a derecha y salta de línea cuando ya no caben (para los chips)."""
    def __init__(self, espaciado=8, alto_item=32, **kwargs):
        super().__init__(orientation="vertical", size_hint_y=None, spacing=espaciado, **kwargs)
        self._espaciado = espaciado
        self._alto_item = alto_item
        self._items = []
        self.bind(minimum_height=self.setter("height"))
        self.bind(width=lambda *a: self._reflujo())
        
    def establecer(self, items):
        self._items = list(items)
        self._reflujo()
        
    def _reflujo(self):
        for it in self._items:
            if it.parent is not None:
                it.parent.remove_widget(it)
        self.clear_widgets()
        fila = None
        usado = 0
        for it in self._items:
            if fila is None or (usado > 0 and usado + it.width > self.width):
                fila = BoxLayout(orientation="horizontal", spacing=self._espaciado, size_hint_y=None, height=self._alto_item)
                self.add_widget(fila)
                usado = 0
            fila.add_widget(it)
            usado += it.width + self._espaciado


class VistaPresupuestos(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(do_scroll_x=False, **kwargs)
        self.categoria_filtro = None
        self._construir_ui()
        estado.bind(presupuestos=self.refrescar_grid, categorias=self.refrescar_chips, presupuesto_total=self._actualizar_kpis, total_gastado=self._actualizar_kpis)
        
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
        
        self.btn_nuevo = Button(text=con_icono("Nuevo presupuesto", "plus-circle-outline"), markup=True, font_size="12sp", bold=True, color=[1, 1, 1, 1], background_color=[0, 0, 0, 0], size_hint=(None, 1), width=160)
        self.btn_nuevo.efecto_sobre_primario = True
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
        self.tarjeta_cat.bind(minimum_height=self.tarjeta_cat.setter('height'))
        self.lbl_c_tit = Label(text="[b]Tus categorías[/b]", markup=True, font_size="15sp", color=tema.texto_principal, size_hint_y=None, height=20, halign="left")
        self.lbl_c_tit.bind(size=self.lbl_c_tit.setter('text_size'))
        self.lbl_c_sub = Label(text="Organiza tus gastos con categorías personalizadas.", font_size="12sp", color=tema.texto_atenuado, size_hint_y=None, height=18, halign="left")
        self.lbl_c_sub.bind(size=self.lbl_c_sub.setter('text_size'))
        self.tarjeta_cat.add_widget(self.lbl_c_tit)
        self.tarjeta_cat.add_widget(self.lbl_c_sub)
        
        self.fila_chips = ContenedorFlujo(espaciado=8, alto_item=32)
        self._cargar_chips()
        self.tarjeta_cat.add_widget(self.fila_chips)
        contenedor.add_widget(self.tarjeta_cat)
        
        self.add_widget(contenedor)
        
    def _cargar_cuadricula(self):
        self.cuadricula.clear_widgets()
        if self.categoria_filtro is None:
            lista = list(estado.presupuestos)
        else:
            lista = [p for p in estado.presupuestos if p["categoria"].lower() == self.categoria_filtro.lower()]
            
        if not lista:
            vacia = TarjetaBase(orientation="vertical", padding=[20, 20, 20, 20], size_hint_y=None, height=130)
            lbl = Label(
                text=f"Aún no hay un presupuesto para «{self.categoria_filtro}».\nCrea uno con «Nuevo presupuesto».",
                font_size="12sp",
                color=tema.texto_atenuado,
                halign="left",
                valign="middle"
            )
            lbl.bind(size=lbl.setter('text_size'))
            vacia.add_widget(lbl)
            self.cuadricula.add_widget(vacia)
            return
            
        for p in lista:
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
            if getattr(w, "activo_chip", False):
                Color(*tema.primario)
                RoundedRectangle(pos=w.pos, size=w.size, radius=[16])
            else:
                Color(*tema.fondo_sutil)
                RoundedRectangle(pos=w.pos, size=w.size, radius=[16])
                Color(*tema.borde)
                Line(rounded_rectangle=(w.x, w.y, w.width, w.height, 16), width=1)
            
    def _cargar_chips(self):
        items = []
        for cat in estado.categorias:
            activo = self.categoria_filtro is not None and cat.lower() == self.categoria_filtro.lower()
            chip = Button(text=cat, font_size="12sp", bold=activo, color=[1, 1, 1, 1] if activo else tema.texto_secundario, background_color=[0, 0, 0, 0], size_hint=(None, None), height=32)
            chip.activo_chip = activo
            chip.efecto_radio = 16
            chip.efecto_sobre_primario = activo
            chip.texture_update()
            chip.width = chip.texture_size[0] + 28
            chip.bind(pos=lambda w, *a: self._redibujar_chip(w), size=lambda w, *a: self._redibujar_chip(w))
            chip.bind(on_release=lambda w, c=cat: self._elegir_categoria(c))
            self._redibujar_chip(chip)
            items.append(chip)
            
        self.btn_nueva_cat = Button(text=con_icono("Nueva categoría", "plus-circle-outline"), markup=True, font_size="12sp", bold=True, color=tema.primario, background_color=[0, 0, 0, 0], size_hint=(None, None), height=32, width=140)
        self.btn_nueva_cat.efecto_radio = 16
        self.btn_nueva_cat.bind(pos=lambda w, *a: self._redibujar_chip(w), size=lambda w, *a: self._redibujar_chip(w))
        self.btn_nueva_cat.bind(on_release=lambda *a: self.abrir_modal_nueva_categoria())
        self._redibujar_chip(self.btn_nueva_cat)
        items.append(self.btn_nueva_cat)
        
        self.fila_chips.establecer(items)
        if self.categoria_filtro is None:
            self.lbl_c_sub.text = "Organiza tus gastos con categorías personalizadas."
        else:
            self.lbl_c_sub.text = f"Mostrando solo «{self.categoria_filtro}». Toca la categoría otra vez para ver todas."
            
    def _elegir_categoria(self, cat):
        """Toca una categoría para filtrar las tarjetas; tocarla de nuevo quita el filtro."""
        if self.categoria_filtro is not None and self.categoria_filtro.lower() == cat.lower():
            self.categoria_filtro = None
        else:
            self.categoria_filtro = cat
        self._cargar_chips()
        self._cargar_cuadricula()
        
    def abrir_modal_nuevo_presupuesto(self):
        dialogo = ModalNuevoPresupuesto(al_guardar=self._cargar_cuadricula)
        dialogo.open()
        
    def abrir_modal_nueva_categoria(self):
        ModalNuevaCategoria().open()
        
    def _actualizar_kpis(self, *args):
        """Mantiene al día las tres tarjetas de resumen cuando cambian los presupuestos o los gastos."""
        self.tarjeta_total.actualizar_valor(f"$ {estado.presupuesto_total:,.2f}")
        self.tarjeta_gastado.actualizar_valor(f"$ {estado.total_gastado:,.2f}")
        self.tarjeta_disp.actualizar_valor(f"$ {estado.presupuesto_total - estado.total_gastado:,.2f}")
        pct = int((estado.total_gastado / estado.presupuesto_total) * 100) if estado.presupuesto_total > 0 else 0
        self.tarjeta_gastado.badge.etiqueta.text = f"{pct}% utilizado"
        
    def refrescar_grid(self, *args):
        self._cargar_cuadricula()
        
    def refrescar_chips(self, *args):
        self._cargar_chips()
        
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
