# CENTS - Frontend en Python 3.10, Kivy 2.3.1 y KivyMD 1.2.0

Aplicación de finanzas personales diseñada a partir de los prototipos del PDF. Todo el código y los archivos están organizados y nombrados en **español**, utilizando **Python 3.10.5**, **Kivy 2.3.1** y **KivyMD 1.2.0**.

---

## 📌 Versiones Instaladas y Configuradas

- **Python**: `3.10.5`
- **Kivy**: `2.3.1`
- **KivyMD**: `1.2.0`
- **Pillow**: `10.4.0`

Instalación de requerimientos:
```bash
pip install -r requerimientos.txt
```

---

## 🚀 Cómo Ejecutar la Aplicación

### Opción 1 (Recomendada en Windows):
Haz doble clic sobre el archivo ejecutable:
- **`ejecutar.bat`** (o `run.bat`)

### Opción 2 (PowerShell):
```powershell
.\ejecutar.ps1
```

### Opción 3 (Directo con Python 3.10):
```bash
python principal.py
```

---

## 📁 Estructura de Archivos Ordenada en Español

```
CENTS_FrontEnd/
│
├── principal.py                        # Archivo principal de inicio de la aplicación
├── main.py                             # Archivo de compatibilidad (ejecuta principal.py)
├── estado_app.py                       # Estado reactivo global, datos y usuario
├── tema.py                             # Colores, estilos y conmutador Modo Claro / Oscuro
├── requerimientos.txt                  # Dependencias del proyecto en español
├── requirements.txt                    # Dependencias en formato estándar
├── ejecutar.bat                        # Acceso directo para ejecutar en Windows
├── ejecutar.ps1                        # Script para ejecutar en PowerShell
├── README.md                           # Documentación completa del proyecto
│
├── componentes/                        # Componentes gráficos reutilizables
│   ├── __init__.py
│   ├── tarjetas.py                     # Tarjetas KPI, tarjetas de categorías y botones
│   ├── graficos.py                     # Gráfico de Donut y Gráfico de Barras de 6 meses en Canvas
│   ├── modales.py                      # Ventanas emergentes (Nuevo Gasto, Nuevo Ingreso, Consejos, Presupuesto)
│   ├── barra_lateral.py                # Menú lateral fijo con logotipo y "Consejo del día"
│   └── barra_superior.py               # Encabezado superior dinámico, fecha y cápsula de perfil
│
└── pantallas/                          # Pantallas y vistas de la aplicación
    ├── __init__.py
    ├── pantallas_autenticacion.py      # Login ("Bienvenido de nuevo"), Registro y Recuperar Contraseña
    ├── pantalla_inicio.py              # Pantalla principal (Dashboard) con métricas, gráficos y movimientos
    ├── pantalla_ingresos.py            # Pantalla de Ingresos con filtros y tabla de transacciones
    ├── pantalla_gastos.py              # Pantalla de Gastos con buscador y tabla completa de transacciones
    ├── pantalla_presupuestos.py        # Pantalla de Presupuestos, límites por categoría y nuevo presupuesto
    ├── pantalla_inversiones.py         # Pantalla de Inversiones (Renta Fija y Renta Variable)
    ├── pantalla_perfil.py              # Mi Perfil, Editar Perfil y Cambiar Contraseña
    ├── pantalla_configuracion.py       # Configuración, moneda, idioma y cambio de apariencia en vivo
    └── portal_principal.py             # Contenedor que integra la barra lateral y cambia entre vistas
```

---

## 🖥️ Pantallas del PDF Reproducidas al 100%

1. **Autenticación**:
   - **`PantallaLogin`**: *"Bienvenido de nuevo"*, banner azul con círculos financieros, formulario de acceso y enlaces.
   - **`PantallaRegistro`**: *"Crear una cuenta"*, nombre, correo, contraseñas y checkbox de términos.
   - **`PantallaRecuperarContrasena`**: *"Recuperar contraseña"*, icono ✉ y envío de enlace.

2. **Dashboard e Inicio**:
   - **`VistaInicio`**: 4 tarjetas métricas (Total gastado, Restante, Promedio diario, Mayor categoría), gráfico de Donut interactivo, gráfico de barras mensuales (Jun a Nov) y tabla de últimos movimientos.

3. **Ingresos y Gastos**:
   - **`VistaIngresos`**: Métricas de ingresos, filtros por mes/categoría/método, y tabla completa.
   - **`VistaGastos`**: Historial completo con botón para exportar, filtros y opción de edición ✎.

4. **Presupuestos e Inversiones**:
   - **`VistaPresupuestos`**: Tarjetas de límites por categoría con barra de progreso y badges (*Dentro del presupuesto*, *Cerca del límite*, *¡Presupuesto excedido!*).
   - **`VistaInversiones`**: Tablas completas de Renta Fija (Pólizas, Certificados BCE, Bonos) y Renta Variable (ETF, Verizon, Favorita, etc.).

5. **Perfil, Seguridad y Configuración**:
   - **`VistaMiPerfil`**: Visualización de datos, ID de cuenta y botones de gestión.
   - **`VistaEditarPerfil`**: Formulario de edición con avatar `SG`.
   - **`VistaCambiarContrasena`**: Formulario seguro con validación de contraseña.
   - **`VistaConfiguracion`**: Subpestañas, selector de monedas (`USD`, `EUR`, `MXN`), selector de idiomas y conmutador de **Modo Claro / Oscuro** en vivo.

6. **Modales Interactivos**:
   - `ModalNuevoGasto`: Registro de concepto, categoría, método de pago y monto.
   - `ModalNuevoIngreso`: Registro de ingresos y método de cobro.
   - `ModalNuevoPresupuesto`: Asignación de montos límite por categoría.
   - `ModalConsejos`: Consejo del día y recomendaciones de ahorro financiero.
