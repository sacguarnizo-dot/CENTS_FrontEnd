"""
CENTS - Utilidades de fechas y números (sin dependencias de Kivy)

Los datos guardan la fecha como "01 Nov 2026", pero los formularios la escriben como
"01/11/2026". Estas funciones entienden ambos formatos para poder ordenar por fecha,
filtrar por mes y editar registros sin importar cómo se guardaron.
"""
import re
from datetime import date

MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
         "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
MESES_ABREV = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

_MES_A_NUM = {}
for _i, _nombre in enumerate(MESES, start=1):
    _MES_A_NUM[_nombre.lower()] = _i
    _MES_A_NUM[_nombre[:3].lower()] = _i
_MES_A_NUM["sept"] = 9
_MES_A_NUM["set"] = 9
for _i, _ing in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], start=1):
    _MES_A_NUM.setdefault(_ing, _i)


def parsear_fecha(texto):
    """Devuelve un date a partir de '01 Nov 2026', '01/11/2026', '1-11-2026' o '2026-11-01'; None si no es válida."""
    if not texto:
        return None
    t = str(texto).strip()
    try:
        m = re.match(r"^(\d{1,2})\s+([A-Za-zÁÉÍÓÚáéíóúñÑ]+)\.?\s+(\d{4})$", t)
        if m:
            mes = _MES_A_NUM.get(m.group(2).lower())
            return date(int(m.group(3)), mes, int(m.group(1))) if mes else None
        m = re.match(r"^(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})$", t)
        if m:
            return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", t)
        if m:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None
    return None


def formatear_fecha(d):
    """date -> '01 Nov 2026' (el formato que usan las tablas)."""
    return f"{d.day:02d} {MESES_ABREV[d.month - 1]} {d.year}"


def fecha_a_campo(texto):
    """Texto de fecha -> 'dd/mm/aaaa' para mostrarlo en un campo de edición."""
    d = parsear_fecha(texto)
    return f"{d.day:02d}/{d.month:02d}/{d.year}" if d else str(texto or "")


def fecha_orden(texto):
    """Clave para ordenar de más reciente a más antigua (fechas inválidas al final)."""
    return parsear_fecha(texto) or date.min


def mes_de(texto):
    """'01 Nov 2026' -> (2026, 11); None si la fecha no es válida."""
    d = parsear_fecha(texto)
    return (d.year, d.month) if d else None


def mes_actual():
    hoy = date.today()
    return (hoy.year, hoy.month)


def _mes_anterior(clave):
    y, m = clave
    return (y - 1, 12) if m == 1 else (y, m - 1)


def en_mes_actual(texto):
    return mes_de(texto) == mes_actual()


def nombre_mes(clave):
    """(2026, 10) -> 'Octubre 2026'."""
    return f"{MESES[clave[1] - 1]} {clave[0]}"


def etiqueta_mes_menu(clave):
    """Nombre del mes con una marca para el mes actual y el pasado."""
    actual = mes_actual()
    if clave == actual:
        return f"{nombre_mes(clave)}  ·  este mes"
    if clave == _mes_anterior(actual):
        return f"{nombre_mes(clave)}  ·  mes pasado"
    return nombre_mes(clave)


def meses_disponibles(textos_fecha):
    """Meses que hay en los datos más el mes actual, del más reciente al más antiguo."""
    claves = {mes_actual()}
    for t in textos_fecha:
        c = mes_de(t)
        if c:
            claves.add(c)
    return sorted(claves, reverse=True)


def a_numero(texto):
    """'$1,250.50' / '12,5' / '15' -> float. Lanza ValueError si no es un número."""
    s = str(texto).replace("$", "").replace(" ", "").strip()
    if not s:
        raise ValueError("vacío")
    if "," in s and "." in s:
        s = s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".")
    return float(s)
