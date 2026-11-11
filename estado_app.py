"""
CENTS - Estado Global y Almacén de Datos
Gestiona las transacciones, usuario, presupuestos, inversiones y temas.
"""

from kivy.event import EventDispatcher
from kivy.properties import StringProperty, DictProperty, ListProperty, NumericProperty

class EstadoAplicacion(EventDispatcher):
    nombre_tema = StringProperty("claro")
    pantalla_actual = StringProperty("inicio")
    
    usuario_actual = DictProperty({
        "nombre": "Usuario1",
        "primer_nombre": "Steven",
        "apellido": "Guarnizo",
        "correo": "usuario@gmail.com",
        "telefono": "+593 99 000 0000",
        "id": "FIN 2026 00128",
        "tipo_cuenta": "Personal",
        "fecha_registro": "15 de octubre de 2026",
        "moneda": "USD ($)",
        "idioma": "Español (ES)",
        "iniciales": "SG"
    })
    
    # Resumen financiero
    presupuesto_total = NumericProperty(2000.00)
    total_gastado = NumericProperty(1245.80)
    total_ingresado = NumericProperty(1245.80)
    gasto_promedio_diario = NumericProperty(41.53)
    ingreso_promedio_diario = NumericProperty(46.53)
    ingreso_mes_actual = NumericProperty(1415.00)
    
    # Colecciones de datos
    gastos = ListProperty([
        {"id": 1, "fecha": "01 Nov 2026", "descripcion": "Supermercado semanal", "categoria": "Alimentación", "metodo": "Tarjeta", "monto": 86.50},
        {"id": 2, "fecha": "31 Oct 2026", "descripcion": "Taxi al trabajo", "categoria": "Transporte", "metodo": "Efectivo", "monto": 12.00},
        {"id": 3, "fecha": "30 Oct 2026", "descripcion": "Internet hogar", "categoria": "Servicios", "metodo": "Transferencia", "monto": 35.00},
        {"id": 4, "fecha": "29 Oct 2026", "descripcion": "Cena con amigos", "categoria": "Entretenimiento", "metodo": "Tarjeta", "monto": 28.50},
        {"id": 5, "fecha": "28 Oct 2026", "descripcion": "Compra farmacia", "categoria": "Salud", "metodo": "Efectivo", "monto": 16.80},
        {"id": 6, "fecha": "27 Oct 2026", "descripcion": "Pago de arriendo", "categoria": "Vivienda", "metodo": "Transferencia", "monto": 350.00},
        {"id": 7, "fecha": "26 Oct 2026", "descripcion": "Combustible", "categoria": "Transporte", "metodo": "Tarjeta", "monto": 40.00},
        {"id": 8, "fecha": "25 Oct 2026", "descripcion": "Café y desayuno", "categoria": "Alimentación", "metodo": "Efectivo", "monto": 8.75},
        {"id": 9, "fecha": "24 Oct 2026", "descripcion": "Suscripción música", "categoria": "Entretenimiento", "metodo": "Tarjeta", "monto": 5.99},
        {"id": 10, "fecha": "23 Oct 2026", "descripcion": "Productos de limpieza", "categoria": "Vivienda", "metodo": "Tarjeta", "monto": 22.40},
    ])
    
    ingresos = ListProperty([
        {"id": 1, "fecha": "01 Nov 2026", "descripcion": "Freelance salario", "categoria": "Salario", "metodo": "Transferencia", "monto": 1005.00},
        {"id": 2, "fecha": "31 Oct 2026", "descripcion": "Trabajo de diseño web", "categoria": "Freelance", "metodo": "Depósito", "monto": 42.00},
        {"id": 3, "fecha": "30 Oct 2026", "descripcion": "Dinero de ahorros", "categoria": "Intereses", "metodo": "Efectivo", "monto": 33.00},
        {"id": 4, "fecha": "27 Oct 2026", "descripcion": "Regalo de cumpleaños", "categoria": "Bonos", "metodo": "Efectivo", "monto": 28.00},
        {"id": 5, "fecha": "26 Oct 2026", "descripcion": "Pago por asesoria", "categoria": "Salario", "metodo": "Transferencia", "monto": 30.00},
        {"id": 6, "fecha": "25 Oct 2026", "descripcion": "Trabajo de la semana", "categoria": "Salario", "metodo": "Transferencia", "monto": 250.00},
        {"id": 7, "fecha": "24 Oct 2026", "descripcion": "Cobro de una deuda", "categoria": "Intereses", "metodo": "Efectivo", "monto": 27.00},
    ])
    
    presupuestos = ListProperty([
        {"id": 1, "categoria": "Alimentación", "gastado": 180.00, "limite": 250.00, "porcentaje": 72, "estado": "Dentro del presupuesto", "color": [0.086, 0.686, 0.38, 1]},
        {"id": 2, "categoria": "Transporte", "gastado": 90.00, "limite": 120.00, "porcentaje": 75, "estado": "Dentro del presupuesto", "color": [0.086, 0.686, 0.38, 1]},
        {"id": 3, "categoria": "Vivienda", "gastado": 450.00, "limite": 500.00, "porcentaje": 90, "estado": "Cerca del límite", "color": [0.96, 0.62, 0.04, 1]},
        {"id": 4, "categoria": "Salud", "gastado": 65.00, "limite": 100.00, "porcentaje": 65, "estado": "Dentro del presupuesto", "color": [0.086, 0.686, 0.38, 1]},
        {"id": 5, "categoria": "Entretenimiento", "gastado": 115.00, "limite": 100.00, "porcentaje": 115, "estado": "¡Presupuesto excedido!", "color": [0.937, 0.267, 0.267, 1]},
        {"id": 6, "categoria": "Servicios", "gastado": 145.00, "limite": 200.00, "porcentaje": 73, "estado": "Dentro del presupuesto", "color": [0.086, 0.686, 0.38, 1]},
    ])
    
    inversiones_renta_fija = ListProperty([
        {"id": 1, "fecha": "01 Nov 2026", "descripcion": "Poliza de Acumulación", "entidad": "PRODUBANCO", "tasa": "7%", "dias": "365", "monto": 2000.00},
        {"id": 2, "fecha": "31 Oct 2026", "descripcion": "Poliza de Acumulación", "entidad": "BANCO GUAYAQUIL", "tasa": "7%", "dias": "365", "monto": 500.00},
        {"id": 3, "fecha": "30 Oct 2026", "descripcion": "Certificado de Tesoreria", "entidad": "BCE", "tasa": "2,56%", "dias": "90", "monto": 2500.00},
        {"id": 4, "fecha": "29 Oct 2026", "descripcion": "Bonos del Estado", "entidad": "Ministerio de Finanzas", "tasa": "11,11%", "dias": "1460", "monto": 1000.00},
        {"id": 5, "fecha": "28 Oct 2026", "descripcion": "Certificado de Tesoreria", "entidad": "BCE", "tasa": "2,56%", "dias": "90", "monto": 2500.00},
    ])
    
    inversiones_renta_variable = ListProperty([
        {"id": 1, "fecha": "01 Nov 2026", "accion": "FONDO DE INVERSIÓN COTIZADO ETF", "broker": "MERCAPITAL", "costo": 1.06, "cantidad": 300, "monto": 318.00, "comision": 70.00, "costo_total": 340.00},
        {"id": 2, "fecha": "31 Oct 2026", "accion": "VERIZON", "broker": "XTB", "costo": 45.24, "cantidad": 3, "monto": 135.72, "comision": 70.00, "costo_total": 226.00},
        {"id": 3, "fecha": "30 Oct 2026", "accion": "CORPORACION FAVORITA C.A", "broker": "MERCAPITAL", "costo": 2.07, "cantidad": 100, "monto": 270.00, "comision": 0.00, "costo_total": 81.90},
        {"id": 4, "fecha": "29 Oct 2026", "accion": "BANCO DEL AUSTRO", "broker": "MERCAPITAL", "costo": 0.52, "cantidad": 300, "monto": 156.00, "comision": 70.00, "costo_total": 388.00},
        {"id": 5, "fecha": "28 Oct 2026", "accion": "BlackBerry", "broker": "XTB", "costo": 8.19, "cantidad": 10, "monto": 81.90, "comision": 0.00, "costo_total": 135.72},
    ])
    
    categorias = ListProperty(["Alimentación", "Transporte", "Vivienda", "Salud", "Ocio", "Servicios", "Entretenimiento"])
    
    def agregar_gasto(self, descripcion, monto, categoria="Alimentación", metodo="Tarjeta", fecha="01/11/2026"):
        nuevo = {
            "id": len(self.gastos) + 1,
            "fecha": fecha,
            "descripcion": descripcion,
            "categoria": categoria,
            "metodo": metodo,
            "monto": float(monto)
        }
        self.gastos.insert(0, nuevo)
        self.total_gastado += float(monto)
        self._recalcular_presupuesto(categoria, float(monto))
        
    def agregar_ingreso(self, descripcion, monto, categoria="Salario", metodo="Transferencia", fecha="03/11/2026"):
        nuevo = {
            "id": len(self.ingresos) + 1,
            "fecha": fecha,
            "descripcion": descripcion,
            "categoria": categoria,
            "metodo": metodo,
            "monto": float(monto)
        }
        self.ingresos.insert(0, nuevo)
        self.total_ingresado += float(monto)
        self.ingreso_mes_actual += float(monto)

    def agregar_presupuesto(self, nombre, limite, categoria):
        nuevo_p = {
            "id": len(self.presupuestos) + 1,
            "categoria": categoria if categoria else nombre,
            "gastado": 0.0,
            "limite": float(limite),
            "porcentaje": 0,
            "estado": "Dentro del presupuesto",
            "color": [0.086, 0.686, 0.38, 1]
        }
        self.presupuestos.append(nuevo_p)
        self.presupuesto_total += float(limite)

    def _recalcular_presupuesto(self, categoria, monto):
        actualizados = []
        for p in self.presupuestos:
            if p["categoria"].lower() == categoria.lower():
                copia = dict(p)
                copia["gastado"] += monto
                pct = int((copia["gastado"] / copia["limite"]) * 100) if copia["limite"] > 0 else 0
                copia["porcentaje"] = pct
                if pct > 100:
                    copia["estado"] = "¡Presupuesto excedido!"
                    copia["color"] = [0.937, 0.267, 0.267, 1]
                elif pct >= 85:
                    copia["estado"] = "Cerca del límite"
                    copia["color"] = [0.96, 0.62, 0.04, 1]
                else:
                    copia["estado"] = "Dentro del presupuesto"
                    copia["color"] = [0.086, 0.686, 0.38, 1]
                actualizados.append(copia)
            else:
                actualizados.append(p)
        self.presupuestos = actualizados

    def actualizar_perfil(self, nombre, correo, telefono):
        u = dict(self.usuario_actual)
        u["nombre"] = nombre
        u["correo"] = correo
        u["telefono"] = telefono
        self.usuario_actual = u

    def cambiar_tema(self, modo_str):
        if modo_str.lower() in ["oscuro", "dark", "☾ oscuro"]:
            self.nombre_tema = "oscuro"
        else:
            self.nombre_tema = "claro"

# Instancia singleton global
estado = EstadoAplicacion()
