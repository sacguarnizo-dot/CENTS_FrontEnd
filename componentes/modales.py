"""
CENTS - Ventanas Modales y Cuadros de Diálogo
- ModalNuevoGasto
- ModalNuevoIngreso
- ModalConsejos (Consejos Financieros)
- ModalNuevoPresupuesto
"""

import os
import sys
_dir_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _dir_raiz not in sys.path:
    sys.path.insert(0, _dir_raiz)

from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Line
from tema import tema
from estado_app import estado
from componentes.tarjetas import EntradaTexto, EntradaEstilizada, BotonPrimario

class ModalNuevoGasto(ModalView):
    def __init__(self, al_guardar=None, **kwargs):
        super().__init__(
            size_hint=(None, None),
            size=(520, 640),
            auto_dismiss=True,
            background_color=[0, 0, 0, 0.55],
            **kwargs
        )
        self.al_guardar = al_guardar
        self.categoria_seleccionada = "Alimentación"
        self.metodo_seleccionado = "Tarjeta"
        self._construir_ui()
        
    def _construir_ui(self):
        contenedor = BoxLayout(orientation="vertical", padding=[28, 24, 28, 24], spacing=14)
        with contenedor.canvas.before:
            Color(*tema.fondo_tarjeta)
            RoundedRectangle(pos=contenedor.pos, size=contenedor.size, radius=[16])
        contenedor.bind(pos=lambda w, *a: self._redibujar_tarjeta(w), size=lambda w, *a: self._redibujar_tarjeta(w))
        
        # Encabezado
        encabezado = BoxLayout(orientation="vertical", size_hint_y=None, height=50, spacing=4)
        lbl_t = Label(text="[b]Nuevo gasto[/b]", markup=True, font_size="20sp", color=tema.texto_principal, halign="left")
        lbl_t.bind(size=lbl_t.setter('text_size'))
        lbl_sub = Label(text="Completa los datos para registrar tu movimiento.", font_size="13sp", color=tema.texto_secundario, halign="left")
        lbl_sub.bind(size=lbl_sub.setter('text_size'))
        encabezado.add_widget(lbl_t)
        encabezado.add_widget(lbl_sub)
        contenedor.add_widget(encabezado)
        
        # Formulario
        desplazable = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        formulario = BoxLayout(orientation="vertical", spacing=12, size_hint_y=None)
        formulario.bind(minimum_height=formulario.setter('height'))
        
        # MONTO
        formulario.add_widget(self._crear_etiqueta("MONTO ($)"))
        self.in_monto = EntradaTexto(hint_text="0.00")
        formulario.add_widget(self.in_monto)
        
        # DESCRIPCIÓN
        formulario.add_widget(self._crear_etiqueta("DESCRIPCIÓN / CONCEPTO"))
        self.in_desc = EntradaTexto(hint_text="Ej. Compra de supermercado")
        formulario.add_widget(self.in_desc)
        
        # CATEGORÍA
        formulario.add_widget(self._crear_etiqueta("CATEGORÍA"))
        caja_cat = BoxLayout(orientation="horizontal", spacing=6, size_hint_y=None, height=36)
        self.botones_cat = []
        for cat in ["Alimentación", "Transporte", "Servicios", "Vivienda", "Salud"]:
            b = Button(text=cat, font_size="11sp", background_color=[0, 0, 0, 0], bold=True)
            self._estilizar_pildora(b, activo=(cat == self.categoria_seleccionada))
            b.bind(on_release=lambda btn, c=cat: self._seleccionar_cat(c))
            self.botones_cat.append((b, cat))
            caja_cat.add_widget(b)
        formulario.add_widget(caja_cat)
        
        # MÉTODO DE PAGO
        formulario.add_widget(self._crear_etiqueta("MÉTODO DE PAGO"))
        caja_pago = BoxLayout(orientation="horizontal", spacing=8, size_hint_y=None, height=36)
        self.botones_pago = []
        for m in ["Efectivo", "Tarjeta", "Transferencia"]:
            b = Button(text=m, font_size="12sp", background_color=[0, 0, 0, 0], bold=True)
            self._estilizar_pildora(b, activo=(m == self.metodo_seleccionado))
            b.bind(on_release=lambda btn, met=m: self._seleccionar_metodo(met))
            self.botones_pago.append((b, m))
            caja_pago.add_widget(b)
        formulario.add_widget(caja_pago)
        
        # FECHA
        formulario.add_widget(self._crear_etiqueta("FECHA"))
        self.in_fecha = EntradaTexto(text="01/11/2026")
        formulario.add_widget(self.in_fecha)
        
        # NOTAS (OPCIONAL)
        formulario.add_widget(self._crear_etiqueta("NOTAS (OPCIONAL)"))
        self.in_notas = EntradaTexto(hint_text="Añade algún detalle sobre este gasto...")
        formulario.add_widget(self.in_notas)
        
        # Adjuntar comprobante
        btn_adjuntar = Button(
            text="＋ Adjuntar comprobante  (PNG, JPG o PDF)",
            font_size="12sp",
            color=tema.primario,
            background_color=[0, 0, 0, 0],
            size_hint_y=None,
            height=36
        )
        with btn_adjuntar.canvas.before:
            Color(*tema.fondo_sutil)
            RoundedRectangle(pos=btn_adjuntar.pos, size=btn_adjuntar.size, radius=[8])
            Color(*tema.borde)
            Line(rounded_rectangle=(btn_adjuntar.x, btn_adjuntar.y, btn_adjuntar.width, btn_adjuntar.height, 8), width=1)
        btn_adjuntar.bind(pos=lambda w, *a: self._redibujar_adjunto(w), size=lambda w, *a: self._redibujar_adjunto(w))
        formulario.add_widget(btn_adjuntar)
        
        desplazable.add_widget(formulario)
        contenedor.add_widget(desplazable)
        
        # Botones de Acción
        fila_btn = BoxLayout(orientation="horizontal", spacing=12, size_hint_y=None, height=44)
        
        btn_cancelar = Button(text="Cancelar", font_size="14sp", bold=True, background_color=[0, 0, 0, 0], color=tema.texto_secundario)
        with btn_cancelar.canvas.before:
            Color(*tema.borde)
            Line(rounded_rectangle=(btn_cancelar.x, btn_cancelar.y, btn_cancelar.width, btn_cancelar.height, 8), width=1)
        btn_cancelar.bind(pos=lambda w, *a: self._redibujar_btn_contorno(w), size=lambda w, *a: self._redibujar_btn_contorno(w))
        btn_cancelar.bind(on_release=lambda *a: self.dismiss())
        fila_btn.add_widget(btn_cancelar)
        
        btn_guardar = BotonPrimario(text="Guardar gasto")
        btn_guardar.bind(on_release=lambda *a: self._guardar())
        fila_btn.add_widget(btn_guardar)
        
        contenedor.add_widget(fila_btn)
        self.add_widget(contenedor)
        
    def _crear_etiqueta(self, texto):
        lbl = Label(text=texto, font_size="11sp", bold=True, color=tema.texto_atenuado, size_hint_y=None, height=20, halign="left")
        lbl.bind(size=lbl.setter('text_size'))
        return lbl
        
    def _estilizar_pildora(self, btn, activo):
        btn.canvas.before.clear()
        with btn.canvas.before:
            if activo:
                Color(*tema.primario)
                RoundedRectangle(pos=btn.pos, size=btn.size, radius=[8])
                btn.color = [1, 1, 1, 1]
            else:
                Color(*tema.fondo_sutil)
                RoundedRectangle(pos=btn.pos, size=btn.size, radius=[8])
                Color(*tema.borde)
                Line(rounded_rectangle=(btn.x, btn.y, btn.width, btn.height, 8), width=1)
                btn.color = tema.texto_secundario
                
    def _seleccionar_cat(self, cat):
        self.categoria_seleccionada = cat
        for b, c in self.botones_cat:
            self._estilizar_pildora(b, activo=(c == cat))
            
    def _seleccionar_metodo(self, met):
        self.metodo_seleccionado = met
        for b, m in self.botones_pago:
            self._estilizar_pildora(b, activo=(m == met))
            
    def _redibujar_tarjeta(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.fondo_tarjeta)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[16])
            
    def _redibujar_adjunto(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.fondo_sutil)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[8])
            Color(*tema.borde)
            Line(rounded_rectangle=(w.x, w.y, w.width, w.height, 8), width=1)
            
    def _redibujar_btn_contorno(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.borde)
            Line(rounded_rectangle=(w.x, w.y, w.width, w.height, 8), width=1)
            
    def _guardar(self):
        desc = self.in_desc.text.strip() or "Nuevo gasto"
        monto = 0.0
        try:
            monto = float(self.in_monto.text.replace("$", "").strip())
        except ValueError:
            monto = 15.00
            
        estado.agregar_gasto(
            descripcion=desc,
            monto=monto,
            categoria=self.categoria_seleccionada,
            metodo=self.metodo_seleccionado,
            fecha=self.in_fecha.text.strip() or "01/11/2026"
        )
        if self.al_guardar:
            self.al_guardar()
        self.dismiss()

class ModalNuevoIngreso(ModalView):
    def __init__(self, al_guardar=None, **kwargs):
        super().__init__(
            size_hint=(None, None),
            size=(520, 620),
            auto_dismiss=True,
            background_color=[0, 0, 0, 0.55],
            **kwargs
        )
        self.al_guardar = al_guardar
        self.categoria_seleccionada = "Salario"
        self.metodo_seleccionado = "Transferencia"
        self._construir_ui()
        
    def _construir_ui(self):
        contenedor = BoxLayout(orientation="vertical", padding=[28, 24, 28, 24], spacing=14)
        with contenedor.canvas.before:
            Color(*tema.fondo_tarjeta)
            RoundedRectangle(pos=contenedor.pos, size=contenedor.size, radius=[16])
        contenedor.bind(pos=lambda w, *a: self._redibujar_tarjeta(w), size=lambda w, *a: self._redibujar_tarjeta(w))
        
        encabezado = BoxLayout(orientation="vertical", size_hint_y=None, height=50, spacing=4)
        lbl_t = Label(text="[b]Nuevo ingreso[/b]", markup=True, font_size="20sp", color=tema.texto_principal, halign="left")
        lbl_t.bind(size=lbl_t.setter('text_size'))
        lbl_sub = Label(text="Completa los datos para registrar tu nuevo ingreso.", font_size="13sp", color=tema.texto_secundario, halign="left")
        lbl_sub.bind(size=lbl_sub.setter('text_size'))
        encabezado.add_widget(lbl_t)
        encabezado.add_widget(lbl_sub)
        contenedor.add_widget(encabezado)
        
        desplazable = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        formulario = BoxLayout(orientation="vertical", spacing=12, size_hint_y=None)
        formulario.bind(minimum_height=formulario.setter('height'))
        
        formulario.add_widget(self._crear_etiqueta("MONTO ($)"))
        self.in_monto = EntradaTexto(hint_text="0.00")
        formulario.add_widget(self.in_monto)
        
        formulario.add_widget(self._crear_etiqueta("DESCRIPCIÓN"))
        self.in_desc = EntradaTexto(hint_text="Ej. Pago mensual, Trabajo extra...")
        formulario.add_widget(self.in_desc)
        
        formulario.add_widget(self._crear_etiqueta("CATEGORÍA"))
        caja_cat = BoxLayout(orientation="horizontal", spacing=6, size_hint_y=None, height=36)
        self.botones_cat = []
        for cat in ["Salario", "Freelance", "Intereses", "Bonos"]:
            b = Button(text=cat, font_size="11sp", background_color=[0, 0, 0, 0], bold=True)
            self._estilizar_pildora(b, activo=(cat == self.categoria_seleccionada))
            b.bind(on_release=lambda btn, c=cat: self._seleccionar_cat(c))
            self.botones_cat.append((b, cat))
            caja_cat.add_widget(b)
        formulario.add_widget(caja_cat)
        
        formulario.add_widget(self._crear_etiqueta("MÉTODO DE COBRO"))
        caja_pago = BoxLayout(orientation="horizontal", spacing=8, size_hint_y=None, height=36)
        self.botones_pago = []
        for m in ["Efectivo", "Transferencia", "Depósito"]:
            b = Button(text=m, font_size="12sp", background_color=[0, 0, 0, 0], bold=True)
            self._estilizar_pildora(b, activo=(m == self.metodo_seleccionado))
            b.bind(on_release=lambda btn, met=m: self._seleccionar_metodo(met))
            self.botones_pago.append((b, m))
            caja_pago.add_widget(b)
        formulario.add_widget(caja_pago)
        
        formulario.add_widget(self._crear_etiqueta("FECHA"))
        self.in_fecha = EntradaTexto(text="03/11/2026")
        formulario.add_widget(self.in_fecha)
        
        formulario.add_widget(self._crear_etiqueta("NOTAS (OPCIONAL)"))
        self.in_notas = EntradaTexto(hint_text="Añade algún detalle sobre este ingreso...")
        formulario.add_widget(self.in_notas)
        
        btn_adj = Button(text="+ Adjuntar comprobante (Opcional)  PNG, JPG o PDF", font_size="12sp", color=tema.primario, background_color=[0, 0, 0, 0], size_hint_y=None, height=36)
        with btn_adj.canvas.before:
            Color(*tema.fondo_sutil)
            RoundedRectangle(pos=btn_adj.pos, size=btn_adj.size, radius=[8])
            Color(*tema.borde)
            Line(rounded_rectangle=(btn_adj.x, btn_adj.y, btn_adj.width, btn_adj.height, 8), width=1)
        btn_adj.bind(pos=lambda w, *a: self._redibujar_adjunto(w), size=lambda w, *a: self._redibujar_adjunto(w))
        formulario.add_widget(btn_adj)
        
        desplazable.add_widget(formulario)
        contenedor.add_widget(desplazable)
        
        fila_btn = BoxLayout(orientation="horizontal", spacing=12, size_hint_y=None, height=44)
        
        btn_cancelar = Button(text="Cancelar", font_size="14sp", bold=True, background_color=[0, 0, 0, 0], color=tema.texto_secundario)
        with btn_cancelar.canvas.before:
            Color(*tema.borde)
            Line(rounded_rectangle=(btn_cancelar.x, btn_cancelar.y, btn_cancelar.width, btn_cancelar.height, 8), width=1)
        btn_cancelar.bind(pos=lambda w, *a: self._redibujar_btn_contorno(w), size=lambda w, *a: self._redibujar_btn_contorno(w))
        btn_cancelar.bind(on_release=lambda *a: self.dismiss())
        fila_btn.add_widget(btn_cancelar)
        
        btn_guardar = BotonPrimario(text="Guardar ingreso")
        btn_guardar.bind(on_release=lambda *a: self._guardar())
        fila_btn.add_widget(btn_guardar)
        
        contenedor.add_widget(fila_btn)
        self.add_widget(contenedor)
        
    def _crear_etiqueta(self, texto):
        lbl = Label(text=texto, font_size="11sp", bold=True, color=tema.texto_atenuado, size_hint_y=None, height=20, halign="left")
        lbl.bind(size=lbl.setter('text_size'))
        return lbl
        
    def _estilizar_pildora(self, btn, activo):
        btn.canvas.before.clear()
        with btn.canvas.before:
            if activo:
                Color(*tema.primario)
                RoundedRectangle(pos=btn.pos, size=btn.size, radius=[8])
                btn.color = [1, 1, 1, 1]
            else:
                Color(*tema.fondo_sutil)
                RoundedRectangle(pos=btn.pos, size=btn.size, radius=[8])
                Color(*tema.borde)
                Line(rounded_rectangle=(btn.x, btn.y, btn.width, btn.height, 8), width=1)
                btn.color = tema.texto_secundario
                
    def _seleccionar_cat(self, cat):
        self.categoria_seleccionada = cat
        for b, c in self.botones_cat:
            self._estilizar_pildora(b, activo=(c == cat))
            
    def _seleccionar_metodo(self, met):
        self.metodo_seleccionado = met
        for b, m in self.botones_pago:
            self._estilizar_pildora(b, activo=(m == met))
            
    def _redibujar_tarjeta(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.fondo_tarjeta)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[16])
            
    def _redibujar_adjunto(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.fondo_sutil)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[8])
            Color(*tema.borde)
            Line(rounded_rectangle=(w.x, w.y, w.width, w.height, 8), width=1)
            
    def _redibujar_btn_contorno(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.borde)
            Line(rounded_rectangle=(w.x, w.y, w.width, w.height, 8), width=1)
            
    def _guardar(self):
        desc = self.in_desc.text.strip() or "Nuevo ingreso"
        monto = 0.0
        try:
            monto = float(self.in_monto.text.replace("$", "").strip())
        except ValueError:
            monto = 100.0
            
        estado.agregar_ingreso(
            descripcion=desc,
            monto=monto,
            categoria=self.categoria_seleccionada,
            metodo=self.metodo_seleccionado,
            fecha=self.in_fecha.text.strip() or "03/11/2026"
        )
        if self.al_guardar:
            self.al_guardar()
        self.dismiss()

class ModalNuevoPresupuesto(ModalView):
    def __init__(self, al_guardar=None, **kwargs):
        super().__init__(
            size_hint=(None, None),
            size=(520, 620),
            auto_dismiss=True,
            background_color=[0, 0, 0, 0.55],
            **kwargs
        )
        self.al_guardar = al_guardar
        self.categoria_seleccionada = "Alimentación"
        self._construir_ui()
        
    def _construir_ui(self):
        contenedor = BoxLayout(orientation="vertical", padding=[28, 24, 28, 24], spacing=14)
        with contenedor.canvas.before:
            Color(*tema.fondo_tarjeta)
            RoundedRectangle(pos=contenedor.pos, size=contenedor.size, radius=[16])
        contenedor.bind(pos=lambda w, *a: self._redibujar_tarjeta(w), size=lambda w, *a: self._redibujar_tarjeta(w))
        
        encabezado = BoxLayout(orientation="vertical", size_hint_y=None, height=50, spacing=4)
        lbl_t = Label(text="[b]Nuevo presupuesto[/b]", markup=True, font_size="20sp", color=tema.texto_principal, halign="left")
        lbl_t.bind(size=lbl_t.setter('text_size'))
        lbl_sub = Label(text="Crea un límite de gasto para organizar mejor tu dinero.", font_size="13sp", color=tema.texto_secundario, halign="left")
        lbl_sub.bind(size=lbl_sub.setter('text_size'))
        encabezado.add_widget(lbl_t)
        encabezado.add_widget(lbl_sub)
        contenedor.add_widget(encabezado)
        
        desplazable = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        formulario = BoxLayout(orientation="vertical", spacing=12, size_hint_y=None)
        formulario.bind(minimum_height=formulario.setter('height'))
        
        formulario.add_widget(self._crear_etiqueta("NOMBRE DEL PRESUPUESTO"))
        self.in_nombre = EntradaTexto(hint_text="Ej. Presupuesto de alimentación")
        formulario.add_widget(self.in_nombre)
        
        formulario.add_widget(self._crear_etiqueta("CATEGORÍA"))
        caja_cat = BoxLayout(orientation="horizontal", spacing=6, size_hint_y=None, height=36)
        self.botones_cat = []
        for cat in ["Alimentación", "Transporte", "Vivienda", "Salud", "Ocio"]:
            b = Button(text=cat, font_size="11sp", background_color=[0, 0, 0, 0], bold=True)
            self._estilizar_pildora(b, activo=(cat == self.categoria_seleccionada))
            b.bind(on_release=lambda btn, c=cat: self._seleccionar_cat(c))
            self.botones_cat.append((b, cat))
            caja_cat.add_widget(b)
        formulario.add_widget(caja_cat)
        
        fila_campos = BoxLayout(orientation="horizontal", spacing=12, size_hint_y=None, height=64)
        col_per = BoxLayout(orientation="vertical", spacing=4)
        col_per.add_widget(self._crear_etiqueta("PERÍODO"))
        self.in_periodo = EntradaTexto(text="Mensual")
        col_per.add_widget(self.in_periodo)
        fila_campos.add_widget(col_per)
        
        col_lim = BoxLayout(orientation="vertical", spacing=4)
        col_lim.add_widget(self._crear_etiqueta("MONTO LÍMITE ($)"))
        self.in_limite = EntradaTexto(hint_text="250.00")
        col_lim.add_widget(self.in_limite)
        fila_campos.add_widget(col_lim)
        formulario.add_widget(fila_campos)
        
        formulario.add_widget(self._crear_etiqueta("MES DE INICIO"))
        self.in_mes = EntradaTexto(text="Noviembre 2026")
        formulario.add_widget(self.in_mes)
        
        formulario.add_widget(self._crear_etiqueta("DESCRIPCIÓN (OPCIONAL)"))
        self.in_desc = EntradaTexto(hint_text="Agrega una nota sobre el objetivo de este presupuesto...")
        formulario.add_widget(self.in_desc)
        
        caja_aviso = BoxLayout(orientation="horizontal", padding=[14, 10, 14, 10], spacing=10, size_hint_y=None, height=54)
        with caja_aviso.canvas.before:
            Color(*tema.fondo_resaltado)
            RoundedRectangle(pos=caja_aviso.pos, size=caja_aviso.size, radius=[8])
            Color(*tema.borde)
            Line(rounded_rectangle=(caja_aviso.x, caja_aviso.y, caja_aviso.width, caja_aviso.height, 8), width=1)
        caja_aviso.bind(pos=lambda w, *a: self._redibujar_aviso(w), size=lambda w, *a: self._redibujar_aviso(w))
        
        lbl_info = Label(
            text="[b]i  Ten en cuenta[/b]\nEl límite se comparará con tus gastos durante el período seleccionado.",
            markup=True,
            font_size="11sp",
            color=tema.primario,
            halign="left"
        )
        lbl_info.bind(size=lbl_info.setter('text_size'))
        caja_aviso.add_widget(lbl_info)
        formulario.add_widget(caja_aviso)
        
        desplazable.add_widget(formulario)
        contenedor.add_widget(desplazable)
        
        fila_btn = BoxLayout(orientation="horizontal", spacing=12, size_hint_y=None, height=44)
        
        btn_cancelar = Button(text="Cancelar", font_size="14sp", bold=True, background_color=[0, 0, 0, 0], color=tema.texto_secundario)
        with btn_cancelar.canvas.before:
            Color(*tema.borde)
            Line(rounded_rectangle=(btn_cancelar.x, btn_cancelar.y, btn_cancelar.width, btn_cancelar.height, 8), width=1)
        btn_cancelar.bind(pos=lambda w, *a: self._redibujar_btn_contorno(w), size=lambda w, *a: self._redibujar_btn_contorno(w))
        btn_cancelar.bind(on_release=lambda *a: self.dismiss())
        fila_btn.add_widget(btn_cancelar)
        
        btn_guardar = BotonPrimario(text="Crear presupuesto")
        btn_guardar.bind(on_release=lambda *a: self._guardar())
        fila_btn.add_widget(btn_guardar)
        
        contenedor.add_widget(fila_btn)
        self.add_widget(contenedor)
        
    def _crear_etiqueta(self, texto):
        lbl = Label(text=texto, font_size="11sp", bold=True, color=tema.texto_atenuado, size_hint_y=None, height=20, halign="left")
        lbl.bind(size=lbl.setter('text_size'))
        return lbl
        
    def _estilizar_pildora(self, btn, activo):
        btn.canvas.before.clear()
        with btn.canvas.before:
            if activo:
                Color(*tema.primario)
                RoundedRectangle(pos=btn.pos, size=btn.size, radius=[8])
                btn.color = [1, 1, 1, 1]
            else:
                Color(*tema.fondo_sutil)
                RoundedRectangle(pos=btn.pos, size=btn.size, radius=[8])
                Color(*tema.borde)
                Line(rounded_rectangle=(btn.x, btn.y, btn.width, btn.height, 8), width=1)
                btn.color = tema.texto_secundario
                
    def _seleccionar_cat(self, cat):
        self.categoria_seleccionada = cat
        for b, c in self.botones_cat:
            self._estilizar_pildora(b, activo=(c == cat))
            
    def _redibujar_tarjeta(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.fondo_tarjeta)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[16])
            
    def _redibujar_aviso(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.fondo_resaltado)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[8])
            Color(*tema.borde)
            Line(rounded_rectangle=(w.x, w.y, w.width, w.height, 8), width=1)
            
    def _redibujar_btn_contorno(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.borde)
            Line(rounded_rectangle=(w.x, w.y, w.width, w.height, 8), width=1)
            
    def _guardar(self):
        nombre = self.in_nombre.text.strip() or "Presupuesto"
        lim = 200.0
        try:
            lim = float(self.in_limite.text.replace("$", "").strip())
        except ValueError:
            lim = 200.0
        estado.agregar_presupuesto(nombre=nombre, limite=lim, categoria=self.categoria_seleccionada)
        if self.al_guardar:
            self.al_guardar()
        self.dismiss()

class ModalConsejos(ModalView):
    """Ventana modal de Consejos Financieros y recomendaciones prácticas."""
    def __init__(self, **kwargs):
        super().__init__(
            size_hint=(None, None),
            size=(540, 520),
            auto_dismiss=True,
            background_color=[0, 0, 0, 0.55],
            **kwargs
        )
        self._construir_ui()
        
    def _construir_ui(self):
        tarjeta = BoxLayout(orientation="vertical", padding=[28, 24, 28, 24], spacing=16)
        with tarjeta.canvas.before:
            Color(*tema.fondo_tarjeta)
            RoundedRectangle(pos=tarjeta.pos, size=tarjeta.size, radius=[16])
        tarjeta.bind(pos=lambda w, *a: self._redibujar_tarjeta(w), size=lambda w, *a: self._redibujar_tarjeta(w))
        
        encabezado = BoxLayout(orientation="vertical", size_hint_y=None, height=50, spacing=4)
        lbl_t = Label(text="[b]Consejos Financieros[/b]", markup=True, font_size="20sp", color=tema.texto_principal, halign="left")
        lbl_t.bind(size=lbl_t.setter('text_size'))
        lbl_sub = Label(text="Recomendaciones prácticas para cuidar tu dinero en el día a día.", font_size="13sp", color=tema.texto_secundario, halign="left")
        lbl_sub.bind(size=lbl_sub.setter('text_size'))
        encabezado.add_widget(lbl_t)
        encabezado.add_widget(lbl_sub)
        tarjeta.add_widget(encabezado)
        
        caja_consejo = BoxLayout(orientation="vertical", padding=[16, 14, 16, 14], spacing=6, size_hint_y=None, height=105)
        with caja_consejo.canvas.before:
            Color(*tema.fondo_resaltado)
            RoundedRectangle(pos=caja_consejo.pos, size=caja_consejo.size, radius=[10])
            Color(*tema.borde)
            Line(rounded_rectangle=(caja_consejo.x, caja_consejo.y, caja_consejo.width, caja_consejo.height, 10), width=1)
        caja_consejo.bind(pos=lambda w, *a: self._redibujar_caja_consejo(w), size=lambda w, *a: self._redibujar_caja_consejo(w))
        
        lbl_dia_t = Label(text="[b]CONSEJO DEL DÍA[/b]", markup=True, font_size="11sp", color=tema.primario, size_hint_y=None, height=18, halign="left")
        lbl_dia_t.bind(size=lbl_dia_t.setter('text_size'))
        caja_consejo.add_widget(lbl_dia_t)
        
        lbl_dia_cuerpo = Label(
            text="Revisa tus gastos cada semana para mantener tu presupuesto.\nPequeñas revisiones periódicas evitan sorpresas a fin de mes.",
            font_size="12sp",
            color=tema.texto_principal,
            halign="left",
            valign="top"
        )
        lbl_dia_cuerpo.bind(size=lbl_dia_cuerpo.setter('text_size'))
        caja_consejo.add_widget(lbl_dia_cuerpo)
        tarjeta.add_widget(caja_consejo)
        
        lbl_mas = Label(text="MÁS RECOMENDACIONES", font_size="11sp", bold=True, color=tema.texto_atenuado, size_hint_y=None, height=20, halign="left")
        lbl_mas.bind(size=lbl_mas.setter('text_size'))
        tarjeta.add_widget(lbl_mas)
        
        lista_rec = [
            ("Automatiza tu ahorro", "Aparta un monto fijo apenas recibas tus ingresos.", "$"),
            ("Controla los gastos hormiga", "Identifica pequeños consumos diarios que suman al final del mes.", "$"),
            ("Crea un fondo de emergencia", "Procura destinar un pequeño porcentaje para imprevistos.", "$")
        ]
        
        caja_rec = BoxLayout(orientation="vertical", spacing=10, size_hint_y=None)
        caja_rec.bind(minimum_height=caja_rec.setter('height'))
        
        for titulo, desc, icono in lista_rec:
            fila = BoxLayout(orientation="horizontal", spacing=12, size_hint_y=None, height=44)
            
            caja_icono = Widget(size_hint=(None, None), size=(32, 32), pos_hint={"center_y": 0.5})
            with caja_icono.canvas:
                Color(*tema.fondo_sutil)
                RoundedRectangle(pos=caja_icono.pos, size=caja_icono.size, radius=[8])
            lbl_icono = Label(text=f"[b]{icono}[/b]", markup=True, font_size="14sp", color=tema.primario, size_hint=(None, None), size=(32, 32), pos_hint={"center_y": 0.5})
            
            from kivy.uix.floatlayout import FloatLayout
            fl = FloatLayout(size_hint=(None, None), size=(32, 32), pos_hint={"center_y": 0.5})
            fl.add_widget(caja_icono)
            fl.add_widget(lbl_icono)
            fila.add_widget(fl)
            
            col_txt = BoxLayout(orientation="vertical", spacing=2)
            lbl_rt = Label(text=f"[b]{titulo}[/b]", markup=True, font_size="13sp", color=tema.texto_principal, halign="left")
            lbl_rt.bind(size=lbl_rt.setter('text_size'))
            lbl_rd = Label(text=desc, font_size="11sp", color=tema.texto_secundario, halign="left")
            lbl_rd.bind(size=lbl_rd.setter('text_size'))
            col_txt.add_widget(lbl_rt)
            col_txt.add_widget(lbl_rd)
            fila.add_widget(col_txt)
            caja_rec.add_widget(fila)
            
        tarjeta.add_widget(caja_rec)
        tarjeta.add_widget(Widget())
        
        btn_entendido = BotonPrimario(text="Entendido", size_hint_y=None, height=44)
        btn_entendido.bind(on_release=lambda *a: self.dismiss())
        tarjeta.add_widget(btn_entendido)
        
        self.add_widget(tarjeta)
        
    def _redibujar_tarjeta(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.fondo_tarjeta)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[16])
            
    def _redibujar_caja_consejo(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.fondo_resaltado)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[10])
            Color(*tema.borde)
            Line(rounded_rectangle=(w.x, w.y, w.width, w.height, 10), width=1)
