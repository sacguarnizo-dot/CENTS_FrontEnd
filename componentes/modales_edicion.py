"""
CENTS - Ventanas de edición y de nueva categoría
- ModalEditarGasto
- ModalEditarIngreso
- ModalEditarInversionFija
- ModalEditarInversionVariable
- ModalNuevaCategoria

Reutilizan el diseño de ModalNuevoGasto / ModalNuevoIngreso (tarjeta redondeada, encabezado,
etiquetas en mayúscula, campos, píldoras de opciones y botones Cancelar / Guardar). Todas
parten de ModalFormulario, que valida los datos y se los entrega ya limpios a quien guarda.
"""
import os
import sys
_dir_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _dir_raiz not in sys.path:
    sys.path.insert(0, _dir_raiz)

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Line
from tema import tema
from estado_app import estado, METODOS_GASTO, METODOS_INGRESO, CATEGORIAS_INGRESO
from utilidades import parsear_fecha, formatear_fecha, fecha_a_campo, a_numero
from componentes.tarjetas import EntradaTexto, BotonPrimario, BotonPildora


def _unicos(*listas):
    """Une listas sin repetir y respetando el orden."""
    vistos = []
    for lista in listas:
        for x in lista:
            if x and x not in vistos:
                vistos.append(x)
    return vistos


class ModalFormulario(ModalView):
    """
    Formulario genérico. `campos` es una lista de diccionarios:
        clave      nombre con el que llega el dato a al_guardar
        etiqueta   texto en mayúsculas sobre el campo
        tipo       "texto" | "numero" | "entero" | "fecha" | "opciones"
        valor      valor inicial (texto) o la opción seleccionada
        opciones   lista de opciones (solo tipo "opciones")
        hint       texto de ayuda del campo
        nombre     nombre amigable para los mensajes de error
        minimo     valor mínimo permitido en números (por defecto 0.01)
        opcional   True si puede quedar vacío (devuelve `vacio`)
        mitad      True para poner dos campos seguidos en la misma fila
    Al guardar válido llama a al_guardar(dict) y se cierra.
    """
    def __init__(self, titulo, subtitulo, campos, texto_guardar="Guardar cambios", al_guardar=None, alto=640, **kwargs):
        alto = min(alto, max(420, Window.height - 40))
        super().__init__(
            size_hint=(None, None),
            size=(520, alto),
            auto_dismiss=True,
            background_color=[0, 0, 0, 0.55],
            **kwargs
        )
        self._campos = campos
        self._al_guardar_cb = al_guardar
        self._inputs = {}
        self._valores = {}
        self._pildoras = {}
        self._construir_ui(titulo, subtitulo, texto_guardar)
        self.bind(on_open=self._al_abrir)

    # ------------------------------------------------------------------ interfaz
    def _construir_ui(self, titulo, subtitulo, texto_guardar):
        contenedor = BoxLayout(orientation="vertical", padding=[28, 24, 28, 24], spacing=14)
        with contenedor.canvas.before:
            Color(*tema.fondo_tarjeta)
            RoundedRectangle(pos=contenedor.pos, size=contenedor.size, radius=[16])
        contenedor.bind(pos=lambda w, *a: self._redibujar_tarjeta(w), size=lambda w, *a: self._redibujar_tarjeta(w))

        encabezado = BoxLayout(orientation="vertical", size_hint_y=None, height=50, spacing=4)
        lbl_t = Label(text=f"[b]{titulo}[/b]", markup=True, font_size="20sp", color=tema.texto_principal, halign="left")
        lbl_t.bind(size=lbl_t.setter("text_size"))
        lbl_sub = Label(text=subtitulo, font_size="13sp", color=tema.texto_secundario, halign="left")
        lbl_sub.bind(size=lbl_sub.setter("text_size"))
        encabezado.add_widget(lbl_t)
        encabezado.add_widget(lbl_sub)
        contenedor.add_widget(encabezado)

        desplazable = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        formulario = BoxLayout(orientation="vertical", spacing=12, size_hint_y=None)
        formulario.bind(minimum_height=formulario.setter("height"))

        i = 0
        while i < len(self._campos):
            c = self._campos[i]
            if c.get("mitad") and i + 1 < len(self._campos) and self._campos[i + 1].get("mitad"):
                fila = BoxLayout(orientation="horizontal", spacing=12, size_hint_y=None, height=66)
                fila.add_widget(self._columna(c))
                fila.add_widget(self._columna(self._campos[i + 1]))
                formulario.add_widget(fila)
                i += 2
            else:
                formulario.add_widget(self._crear_etiqueta(c["etiqueta"]))
                formulario.add_widget(self._crear_opciones(c) if c.get("tipo") == "opciones" else self._crear_entrada(c))
                i += 1

        desplazable.add_widget(formulario)
        contenedor.add_widget(desplazable)

        self.lbl_error = Label(text="", font_size="12sp", color=tema.peligro, size_hint_y=None, height=18, halign="left")
        self.lbl_error.bind(size=self.lbl_error.setter("text_size"))
        contenedor.add_widget(self.lbl_error)

        fila_btn = BoxLayout(orientation="horizontal", spacing=12, size_hint_y=None, height=44)
        btn_cancelar = Button(text="Cancelar", font_size="14sp", bold=True, background_color=[0, 0, 0, 0], color=tema.texto_secundario)
        with btn_cancelar.canvas.before:
            Color(*tema.borde)
            Line(rounded_rectangle=(btn_cancelar.x, btn_cancelar.y, btn_cancelar.width, btn_cancelar.height, 8), width=1)
        btn_cancelar.bind(pos=lambda w, *a: self._redibujar_btn_contorno(w), size=lambda w, *a: self._redibujar_btn_contorno(w))
        btn_cancelar.bind(on_release=lambda *a: self.dismiss())
        fila_btn.add_widget(btn_cancelar)

        btn_guardar = BotonPrimario(text=texto_guardar)
        btn_guardar.bind(on_release=lambda *a: self._guardar())
        fila_btn.add_widget(btn_guardar)
        contenedor.add_widget(fila_btn)
        self.add_widget(contenedor)

    def _crear_etiqueta(self, texto):
        lbl = Label(text=texto, font_size="11sp", bold=True, color=tema.texto_atenuado, size_hint_y=None, height=20, halign="left")
        lbl.bind(size=lbl.setter("text_size"))
        return lbl

    def _columna(self, c):
        col = BoxLayout(orientation="vertical", spacing=4)
        col.add_widget(self._crear_etiqueta(c["etiqueta"]))
        col.add_widget(self._crear_entrada(c))
        return col

    def _crear_entrada(self, c):
        w = EntradaTexto(text=str(c.get("valor", "")), hint_text=c.get("hint", ""))
        self._inputs[c["clave"]] = w
        return w

    def _crear_opciones(self, c):
        clave = c["clave"]
        opciones = list(c["opciones"])
        valor = c.get("valor")
        if valor and valor not in opciones:
            opciones.append(valor)
        self._valores[clave] = valor if valor in opciones else (opciones[0] if opciones else None)
        por_fila = 4 if max(len(o) for o in opciones) <= 11 else 3
        filas = [opciones[i:i + por_fila] for i in range(0, len(opciones), por_fila)]
        bloque = BoxLayout(orientation="vertical", spacing=6, size_hint_y=None, height=len(filas) * 36 + (len(filas) - 1) * 6)
        pildoras = []
        for ops in filas:
            fila = BoxLayout(orientation="horizontal", spacing=6, size_hint_y=None, height=36)
            for op in ops:
                b = BotonPildora(texto=op, activo=(op == self._valores[clave]))
                b.font_size = "11sp"
                b.bind(on_release=lambda w, cl=clave, o=op: self._elegir(cl, o))
                pildoras.append((b, op))
                fila.add_widget(b)
            for _ in range(por_fila - len(ops)):
                fila.add_widget(Widget())
            bloque.add_widget(fila)
        self._pildoras[clave] = pildoras
        return bloque

    def _elegir(self, clave, opcion):
        self._valores[clave] = opcion
        for b, o in self._pildoras[clave]:
            b.activo = (o == opcion)

    def _redibujar_tarjeta(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.fondo_tarjeta)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[16])

    def _redibujar_btn_contorno(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*tema.borde)
            Line(rounded_rectangle=(w.x, w.y, w.width, w.height, 8), width=1)

    def _al_abrir(self, *args):
        primero = next(iter(self._inputs.values()), None)
        if primero is not None:
            Clock.schedule_once(lambda dt: setattr(primero, "focus", True), 0.1)

    # ---------------------------------------------------------------- validación
    def _error(self, mensaje, widget=None):
        self.lbl_error.text = mensaje
        if widget is not None:
            widget.focus = True

    def validar(self, datos):
        """Gancho para validaciones extra. Devuelve un mensaje de error o None."""
        return None

    def _guardar(self):
        self.lbl_error.text = ""
        datos = {}
        for c in self._campos:
            clave = c["clave"]
            tipo = c.get("tipo", "texto")
            nombre = c.get("nombre", c["etiqueta"].capitalize())
            if tipo == "opciones":
                datos[clave] = self._valores.get(clave)
                continue
            w = self._inputs[clave]
            txt = w.text.strip()
            if not txt:
                if c.get("opcional"):
                    datos[clave] = c.get("vacio", "")
                    continue
                return self._error(f"Completa el campo «{nombre}».", w)
            if tipo in ("numero", "entero"):
                try:
                    valor = a_numero(txt)
                except ValueError:
                    return self._error(f"«{nombre}» debe ser un número.", w)
                minimo = c.get("minimo", 0.01)
                if valor < minimo:
                    msg = f"«{nombre}» debe ser mayor que 0." if minimo > 0 else f"«{nombre}» no puede ser negativo."
                    return self._error(msg, w)
                if tipo == "entero":
                    if valor != int(valor):
                        return self._error(f"«{nombre}» debe ser un número entero.", w)
                    valor = int(valor)
                datos[clave] = valor
            elif tipo == "fecha":
                d = parsear_fecha(txt)
                if d is None:
                    return self._error("La fecha no es válida. Usa el formato dd/mm/aaaa.", w)
                datos[clave] = formatear_fecha(d)
            else:
                datos[clave] = txt
        extra = self.validar(datos)
        if extra:
            return self._error(extra, next(iter(self._inputs.values()), None))
        if self._al_guardar_cb:
            self._al_guardar_cb(datos)
        self.dismiss()


# ====================================================================== edición
class ModalEditarGasto(ModalFormulario):
    def __init__(self, registro, al_guardar=None, **kwargs):
        campos = [
            {"clave": "monto", "etiqueta": "MONTO ($)", "tipo": "numero", "valor": f"{registro['monto']:.2f}", "hint": "0.00", "nombre": "Monto"},
            {"clave": "descripcion", "etiqueta": "DESCRIPCIÓN / CONCEPTO", "tipo": "texto", "valor": registro["descripcion"], "nombre": "Descripción"},
            {"clave": "categoria", "etiqueta": "CATEGORÍA", "tipo": "opciones", "valor": registro["categoria"], "opciones": _unicos(estado.categorias)},
            {"clave": "metodo", "etiqueta": "MÉTODO DE PAGO", "tipo": "opciones", "valor": registro["metodo"], "opciones": _unicos(METODOS_GASTO)},
            {"clave": "fecha", "etiqueta": "FECHA", "tipo": "fecha", "valor": fecha_a_campo(registro["fecha"]), "hint": "dd/mm/aaaa", "nombre": "Fecha"},
        ]
        super().__init__("Editar gasto", "Modifica los datos y guarda los cambios.", campos, al_guardar=self._aplicar, alto=640, **kwargs)
        self._registro = registro
        self._despues = al_guardar

    def _aplicar(self, datos):
        estado.editar_gasto(self._registro["id"], **datos)
        if self._despues:
            self._despues()


class ModalEditarIngreso(ModalFormulario):
    def __init__(self, registro, al_guardar=None, **kwargs):
        campos = [
            {"clave": "monto", "etiqueta": "MONTO ($)", "tipo": "numero", "valor": f"{registro['monto']:.2f}", "hint": "0.00", "nombre": "Monto"},
            {"clave": "descripcion", "etiqueta": "DESCRIPCIÓN", "tipo": "texto", "valor": registro["descripcion"], "nombre": "Descripción"},
            {"clave": "categoria", "etiqueta": "CATEGORÍA", "tipo": "opciones", "valor": registro["categoria"], "opciones": _unicos(CATEGORIAS_INGRESO)},
            {"clave": "metodo", "etiqueta": "MÉTODO DE COBRO", "tipo": "opciones", "valor": registro["metodo"], "opciones": _unicos(METODOS_INGRESO)},
            {"clave": "fecha", "etiqueta": "FECHA", "tipo": "fecha", "valor": fecha_a_campo(registro["fecha"]), "hint": "dd/mm/aaaa", "nombre": "Fecha"},
        ]
        super().__init__("Editar ingreso", "Modifica los datos y guarda los cambios.", campos, al_guardar=self._aplicar, alto=620, **kwargs)
        self._registro = registro
        self._despues = al_guardar

    def _aplicar(self, datos):
        estado.editar_ingreso(self._registro["id"], **datos)
        if self._despues:
            self._despues()


class ModalEditarInversionFija(ModalFormulario):
    def __init__(self, registro, al_guardar=None, **kwargs):
        campos = [
            {"clave": "descripcion", "etiqueta": "DESCRIPCIÓN", "tipo": "texto", "valor": registro["descripcion"], "nombre": "Descripción"},
            {"clave": "entidad", "etiqueta": "ENTIDAD", "tipo": "texto", "valor": registro["entidad"], "nombre": "Entidad"},
            {"clave": "tasa", "etiqueta": "TASA (%)", "tipo": "texto", "valor": registro["tasa"], "hint": "Ej. 7%", "nombre": "Tasa", "mitad": True},
            {"clave": "dias", "etiqueta": "PLAZO (DÍAS)", "tipo": "entero", "valor": str(registro["dias"]), "hint": "365", "nombre": "Plazo", "minimo": 1, "mitad": True},
            {"clave": "monto", "etiqueta": "MONTO ($)", "tipo": "numero", "valor": f"{registro['monto']:.2f}", "hint": "0.00", "nombre": "Monto", "mitad": True},
            {"clave": "fecha", "etiqueta": "FECHA", "tipo": "fecha", "valor": fecha_a_campo(registro["fecha"]), "hint": "dd/mm/aaaa", "nombre": "Fecha", "mitad": True},
        ]
        super().__init__("Editar inversión", "Modifica los datos de tu renta fija y guarda los cambios.", campos, al_guardar=self._aplicar, alto=560, **kwargs)
        self._registro = registro
        self._despues = al_guardar

    def _aplicar(self, datos):
        datos["dias"] = str(datos["dias"])
        if not datos["tasa"].endswith("%"):
            datos["tasa"] += "%"
        estado.editar_inversion_fija(self._registro["id"], **datos)
        if self._despues:
            self._despues()


class ModalEditarInversionVariable(ModalFormulario):
    def __init__(self, registro, al_guardar=None, **kwargs):
        campos = [
            {"clave": "accion", "etiqueta": "ACCIÓN / ACTIVO", "tipo": "texto", "valor": registro["accion"], "nombre": "Acción"},
            {"clave": "broker", "etiqueta": "BROKER", "tipo": "texto", "valor": registro["broker"], "nombre": "Broker"},
            {"clave": "costo", "etiqueta": "COSTO UNITARIO ($)", "tipo": "numero", "valor": f"{registro['costo']:.2f}", "hint": "0.00", "nombre": "Costo unitario", "mitad": True},
            {"clave": "cantidad", "etiqueta": "CANTIDAD", "tipo": "entero", "valor": str(registro["cantidad"]), "hint": "1", "nombre": "Cantidad", "minimo": 1, "mitad": True},
            {"clave": "monto", "etiqueta": "MONTO ($)", "tipo": "numero", "valor": f"{registro['monto']:.2f}", "hint": "0.00", "nombre": "Monto", "mitad": True},
            {"clave": "comision", "etiqueta": "COMISIÓN ($)", "tipo": "numero", "valor": f"{registro['comision']:.2f}", "hint": "0.00", "nombre": "Comisión", "minimo": 0, "mitad": True},
            {"clave": "costo_total", "etiqueta": "COSTO TOTAL ($)", "tipo": "numero", "valor": f"{registro['costo_total']:.2f}", "hint": "0.00", "nombre": "Costo total", "minimo": 0, "mitad": True},
            {"clave": "fecha", "etiqueta": "FECHA", "tipo": "fecha", "valor": fecha_a_campo(registro["fecha"]), "hint": "dd/mm/aaaa", "nombre": "Fecha", "mitad": True},
        ]
        super().__init__("Editar inversión", "Modifica los datos de tu renta variable y guarda los cambios.", campos, al_guardar=self._aplicar, alto=640, **kwargs)
        self._registro = registro
        self._despues = al_guardar

    def _aplicar(self, datos):
        estado.editar_inversion_variable(self._registro["id"], **datos)
        if self._despues:
            self._despues()


# ================================================================ nueva categoría
class ModalNuevaCategoria(ModalFormulario):
    def __init__(self, al_guardar=None, **kwargs):
        campos = [
            {"clave": "nombre", "etiqueta": "NOMBRE DE LA CATEGORÍA", "tipo": "texto", "hint": "Ej. Mascotas", "nombre": "Nombre"},
            {"clave": "limite", "etiqueta": "LÍMITE MENSUAL ($)  ·  OPCIONAL", "tipo": "numero", "opcional": True, "vacio": 0.0, "hint": "Ej. 120.00 (crea también su presupuesto)", "nombre": "Límite mensual"},
        ]
        super().__init__("Nueva categoría", "Organiza tus gastos con una categoría propia.", campos, texto_guardar="Guardar categoría", al_guardar=self._aplicar, alto=380, **kwargs)
        self._despues = al_guardar

    def validar(self, datos):
        if estado.existe_categoria(datos["nombre"]):
            return "Ya existe una categoría con ese nombre."
        return None

    def _aplicar(self, datos):
        estado.agregar_categoria(datos["nombre"], datos.get("limite") or 0.0)
        if self._despues:
            self._despues()
