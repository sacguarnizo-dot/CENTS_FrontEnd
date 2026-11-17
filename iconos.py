"""
CENTS - Utilidades de iconos

La fuente por defecto de Kivy (Roboto) no incluye simbolos como flechas, "＋", "☀" o "▼",
y se ven como un cuadrito vacio. Estas funciones insertan iconos de Material Design
(fuente "Icons" de KivyMD) dentro del texto mediante markup, para usarlos junto a una
palabra en un Button/Label (hay que activar markup=True en el widget).

    con_icono("Ver consejos", "eye-outline", derecha=True)
    icono("arrow-right")
    glifo("email-outline")            # solo el caracter, para Label(font_name="Icons")

Si el nombre del icono no existe devuelve texto vacio (nunca un cuadrito roto).
"""
from kivymd.icon_definitions import md_icons


def glifo(nombre):
    """Caracter crudo del icono (usar con font_name="Icons")."""
    return md_icons.get(nombre, "")


def icono(nombre):
    """Icono como fragmento de markup, para mezclarlo con texto normal."""
    g = md_icons.get(nombre, "")
    return f"[font=Icons]{g}[/font]" if g else ""


def con_icono(texto, nombre, derecha=False, separacion="  "):
    """Texto con un icono a la izquierda (por defecto) o a la derecha."""
    ic = icono(nombre)
    if not ic:
        return texto
    if not texto:
        return ic
    return f"{texto}{separacion}{ic}" if derecha else f"{ic}{separacion}{texto}"
