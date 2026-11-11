"""
CENTS - Pantalla de Inversiones
Tablas de Renta Fija y Renta Variable con tasas, plazos, cantidades, comisiones y costos.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Line
from tema import tema
from estado_app import estado
from componentes.tarjetas import TarjetaBase, EntradaTexto, EntradaEstilizada

class VistaInversiones(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(do_scroll_x=False, **kwargs)
        self.filtro_busqueda = ""
        self._construir_ui()
        
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
        
        self.in_buscar = EntradaTexto(text="", hint_text="⌕ Buscar inversión o descripción...", size_hint_x=0.35)
        self.in_buscar.bind(text=self._al_buscar)
        barra_filtros.add_widget(self.in_buscar)
        
        self.botones_filtros = [
            self._crear_boton_filtro("▣ Este mes"),
            self._crear_boton_filtro("Entidad ⌄"),
            self._crear_boton_filtro("Monto ⌄")
        ]
        for bf in self.botones_filtros:
            barra_filtros.add_widget(bf)
        
        self.btn_limpiar = Button(text="Limpiar filtros", font_size="12sp", color=tema.texto_atenuado, background_color=[0, 0, 0, 0], size_hint=(None, 1), width=95)
        self.btn_limpiar.bind(on_release=lambda *a: self._limpiar_filtros())
        barra_filtros.add_widget(self.btn_limpiar)
        
        self.btn_exportar = Button(text="↓ Exportar historial", font_size="13sp", bold=True, color=tema.texto_principal, background_color=[0, 0, 0, 0], size_hint=(None, 1), width=145)
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
        
        self.lbl_conteo_rf = Label(text="15 movimientos", font_size="12sp", color=tema.texto_atenuado, size_hint=(None, 1), width=100, halign="right")
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
        
        self.caja_filas_fija = BoxLayout(orientation="vertical", spacing=2, size_hint_y=None)
        self.caja_filas_fija.bind(minimum_height=self.caja_filas_fija.setter('height'))
        self._cargar_filas_fija()
        self.tarjeta_fija.add_widget(self.caja_filas_fija)
        
        fila_pag_f = BoxLayout(orientation="horizontal", size_hint_y=None, height=32, padding=[8, 6, 8, 0])
        self.lbl_p_f = Label(text="Mostrando 1 - 5 de 15 movimientos", font_size="12sp", color=tema.texto_atenuado, halign="left")
        self.lbl_p_f.bind(size=self.lbl_p_f.setter('text_size'))
        fila_pag_f.add_widget(self.lbl_p_f)
        
        caja_pg_f = BoxLayout(orientation="horizontal", spacing=6, size_hint=(None, 1))
        caja_pg_f.bind(minimum_width=caja_pg_f.setter('width'))
        self.botones_pg_f = []
        for p in ["1", "2", "3", "→"]:
            pb = Button(text=p, font_size="12sp", bold=True, size_hint=(None, None), size=(26, 26), background_color=[0, 0, 0, 0])
            self._estilizar_boton_pag(pb, activo=(p == "1"))
            self.botones_pg_f.append((pb, p))
            caja_pg_f.add_widget(pb)
        fila_pag_f.add_widget(caja_pg_f)
        self.tarjeta_fija.add_widget(fila_pag_f)
        
        contenedor.add_widget(self.tarjeta_fija)
        
        # 3. Tabla 2: Renta Variable
        self.tarjeta_var = TarjetaBase(orientation="vertical", padding=[20, 16, 20, 16], spacing=12, size_hint_y=None)
        self.tarjeta_var.bind(minimum_height=self.tarjeta_var.setter('height'))
        
        fila_rv = BoxLayout(orientation="horizontal", size_hint_y=None, height=28)
        self.lbl_rv = Label(text="[b]Todas las transacciones de Renta Variable[/b]", markup=True, font_size="15sp", color=tema.texto_principal, halign="left")
        self.lbl_rv.bind(size=self.lbl_rv.setter('text_size'))
        fila_rv.add_widget(self.lbl_rv)
        
        self.lbl_conteo_rv = Label(text="15 movimientos", font_size="12sp", color=tema.texto_atenuado, size_hint=(None, 1), width=100, halign="right")
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
        
        self.caja_filas_var = BoxLayout(orientation="vertical", spacing=2, size_hint_y=None)
        self.caja_filas_var.bind(minimum_height=self.caja_filas_var.setter('height'))
        self._cargar_filas_var()
        self.tarjeta_var.add_widget(self.caja_filas_var)
        
        fila_pag_v = BoxLayout(orientation="horizontal", size_hint_y=None, height=32, padding=[8, 6, 8, 0])
        self.lbl_p_v = Label(text="Mostrando 1 - 5 de 15 movimientos", font_size="12sp", color=tema.texto_atenuado, halign="left")
        self.lbl_p_v.bind(size=self.lbl_p_v.setter('text_size'))
        fila_pag_v.add_widget(self.lbl_p_v)
        
        caja_pg_v = BoxLayout(orientation="horizontal", spacing=6, size_hint=(None, 1))
        caja_pg_v.bind(minimum_width=caja_pg_v.setter('width'))
        self.botones_pg_v = []
        for p in ["1", "2", "3", "→"]:
            pb = Button(text=p, font_size="12sp", bold=True, size_hint=(None, None), size=(26, 26), background_color=[0, 0, 0, 0])
            self._estilizar_boton_pag(pb, activo=(p == "1"))
            self.botones_pg_v.append((pb, p))
            caja_pg_v.add_widget(pb)
        fila_pag_v.add_widget(caja_pg_v)
        self.tarjeta_var.add_widget(fila_pag_v)
        
        contenedor.add_widget(self.tarjeta_var)
        self.add_widget(contenedor)
        
    def _crear_celda_enc(self, texto, size_hint_x=0.2, alineacion="left"):
        lbl = Label(text=texto, font_size="11sp", bold=True, color=tema.texto_atenuado, size_hint_x=size_hint_x, halign=alineacion)
        lbl.bind(size=lbl.setter('text_size'))
        tema.bind(texto_atenuado=lambda *a, l=lbl: setattr(l, 'color', tema.texto_atenuado))
        return lbl
        
    def _crear_boton_filtro(self, texto):
        b = Button(text=texto, font_size="12sp", color=tema.texto_secundario, background_color=[0, 0, 0, 0], size_hint=(None, 1), width=105)
        with b.canvas.before:
            Color(*tema.borde)
            Line(rounded_rectangle=(b.x, b.y, b.width, b.height, 8), width=1)
        b.bind(pos=lambda w, *a: self._redibujar_btn_contorno(w), size=lambda w, *a: self._redibujar_btn_contorno(w))
        return b
        
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
                
    def _cargar_filas_fija(self):
        self.caja_filas_fija.clear_widgets()
        for item in estado.inversiones_renta_fija:
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
            
            btn_editar = Button(text="✎", font_size="13sp", color=tema.primario, background_color=[0, 0, 0, 0], size_hint_x=0.06)
            fila.add_widget(btn_editar)
            
            self.caja_filas_fija.add_widget(fila)
            
    def _cargar_filas_var(self):
        self.caja_filas_var.clear_widgets()
        for item in estado.inversiones_renta_variable:
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
            
            btn_editar = Button(text="✎", font_size="13sp", color=tema.primario, background_color=[0, 0, 0, 0], size_hint_x=0.05)
            fila.add_widget(btn_editar)
            
            self.caja_filas_var.add_widget(fila)
            
    def _redibujar_linea_fila(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.borde_claro)
            Line(points=[w.x, w.y, w.x + w.width, w.y], width=1)
            
    def _al_buscar(self, instance, value):
        self.filtro_busqueda = value.strip()
        self._cargar_filas_fija()
        self._cargar_filas_var()
        
    def _limpiar_filtros(self):
        self.in_buscar.text = ""
        self.filtro_busqueda = ""
        self._cargar_filas_fija()
        self._cargar_filas_var()
        
    def actualizar_tema(self, *args):
        self.in_buscar._al_cambiar_tema()
        for bf in self.botones_filtros:
            self._redibujar_btn_contorno(bf)
            bf.color = tema.texto_secundario
        self.btn_limpiar.color = tema.texto_atenuado
        self._redibujar_btn_contorno(self.btn_exportar)
        self.btn_exportar.color = tema.texto_principal
        self.lbl_rf.color = tema.texto_principal
        self.lbl_conteo_rf.color = tema.texto_atenuado
        self._redibujar_enc(self.enc_f)
        for c in self.celdas_enc_f:
            c.color = tema.texto_atenuado
        self.lbl_p_f.color = tema.texto_atenuado
        for pb, p in self.botones_pg_f:
            self._estilizar_boton_pag(pb, activo=(p == "1"))
        self.lbl_rv.color = tema.texto_principal
        self.lbl_conteo_rv.color = tema.texto_atenuado
        self._redibujar_enc(self.enc_v)
        for c in self.celdas_enc_v:
            c.color = tema.texto_atenuado
        self.lbl_p_v.color = tema.texto_atenuado
        for pb, p in self.botones_pg_v:
            self._estilizar_boton_pag(pb, activo=(p == "1"))
        self._cargar_filas_fija()
        self._cargar_filas_var()
