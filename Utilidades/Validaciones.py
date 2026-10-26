"""Lectura de datos por consola con validación.

Todas las funciones repiten la pregunta hasta recibir un valor válido.
- Escribir 'cancelar' aborta la operación (lanza Cancelado).
- Si hay un valor actual (al actualizar), Enter lo conserva.
- En campos opcionales, Enter deja el campo vacío y '-' borra el valor actual.
"""
import getpass
import hashlib
import os
import re
from datetime import date, datetime, time
from decimal import Decimal, InvalidOperation

PALABRA_CANCELAR = "cancelar"
BORRAR = "-"

_RE_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_RE_TELEFONO = re.compile(r"^[0-9+() -]{7,20}$")


class Cancelado(Exception):
    """El usuario canceló la operación o no se puede continuar."""


def formatear(valor) -> str:
    if valor is None:
        return "-"
    if isinstance(valor, bool):
        return "Sí" if valor else "No"
    if isinstance(valor, datetime):
        return valor.strftime("%Y-%m-%d %H:%M")
    if isinstance(valor, time):
        return valor.strftime("%H:%M")
    if isinstance(valor, Decimal):
        return f"{valor:.2f}"
    return str(valor)


def _pedir(etiqueta: str, convertir, obligatorio: bool = True, actual=None, mostrar=None):
    tiene_actual = actual is not None
    if tiene_actual:
        sufijo = f" [{mostrar if mostrar is not None else formatear(actual)}]"
    else:
        sufijo = "" if obligatorio else " (opcional)"
    while True:
        texto = input(f"  {etiqueta}{sufijo}: ").strip()
        if texto.lower() == PALABRA_CANCELAR:
            raise Cancelado("Operación cancelada.")
        if texto == "":
            if tiene_actual:
                return actual
            if not obligatorio:
                return None
            print("    [!] Este campo es obligatorio.")
            continue
        if texto == BORRAR and not obligatorio:
            return None
        try:
            return convertir(texto)
        except ValueError as e:
            print(f"    [!] {e}")


def pedir_texto(etiqueta, obligatorio=True, largo=0, actual=None) -> str | None:
    def convertir(texto):
        if largo and len(texto) > largo:
            raise ValueError(f"Máximo {largo} caracteres (escribió {len(texto)}).")
        return texto
    return _pedir(etiqueta, convertir, obligatorio, actual)


def pedir_entero(etiqueta, obligatorio=True, minimo=None, maximo=None, actual=None) -> int | None:
    def convertir(texto):
        try:
            numero = int(texto)
        except ValueError:
            raise ValueError("Debe ingresar un número entero.") from None
        _validar_rango(numero, minimo, maximo)
        return numero
    return _pedir(etiqueta, convertir, obligatorio, actual)


def pedir_decimal(etiqueta, obligatorio=True, minimo=None, maximo=None, actual=None) -> Decimal | None:
    def convertir(texto):
        try:
            numero = Decimal(texto.replace(",", "."))
        except InvalidOperation:
            raise ValueError("Debe ingresar un número (ej. 15000 o 12.50).") from None
        if not numero.is_finite():
            raise ValueError("Debe ingresar un número válido.")
        if numero != numero.quantize(Decimal("0.01")):
            raise ValueError("Use como máximo 2 decimales.")
        _validar_rango(numero, minimo, maximo)
        return numero.quantize(Decimal("0.01"))
    return _pedir(etiqueta, convertir, obligatorio, actual)


def _validar_rango(numero, minimo, maximo):
    if minimo is not None and numero < minimo:
        raise ValueError(f"El valor mínimo es {minimo}.")
    if maximo is not None and numero > maximo:
        raise ValueError(f"El valor máximo es {maximo}.")


def _convertir_fecha(texto) -> date:
    for formato in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(texto, formato).date()
        except ValueError:
            pass
    raise ValueError("Fecha inválida. Use AAAA-MM-DD o DD/MM/AAAA (ej. 2026-12-31).")


def _convertir_hora(texto) -> time:
    for formato in ("%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(texto, formato).time()
        except ValueError:
            pass
    raise ValueError("Hora inválida. Use formato 24 h HH:MM (ej. 14:30).")


def _convertir_fecha_hora(texto) -> datetime:
    partes = texto.split()
    if len(partes) != 2:
        raise ValueError("Use el formato AAAA-MM-DD HH:MM (ej. 2026-12-31 14:30).")
    return datetime.combine(_convertir_fecha(partes[0]), _convertir_hora(partes[1]))


def pedir_fecha(etiqueta, obligatorio=True, actual=None) -> date | None:
    return _pedir(etiqueta + " (AAAA-MM-DD)", _convertir_fecha, obligatorio, actual)


def pedir_hora(etiqueta, obligatorio=True, actual=None) -> time | None:
    return _pedir(etiqueta + " (HH:MM)", _convertir_hora, obligatorio, actual)


def pedir_fecha_hora(etiqueta, obligatorio=True, actual=None) -> datetime | None:
    return _pedir(etiqueta + " (AAAA-MM-DD HH:MM)", _convertir_fecha_hora, obligatorio, actual)


def pedir_email(etiqueta, obligatorio=True, actual=None) -> str | None:
    def convertir(texto):
        if len(texto) > 100 or not _RE_EMAIL.match(texto):
            raise ValueError("Correo inválido (ej. nombre@dominio.com).")
        return texto.lower()
    return _pedir(etiqueta, convertir, obligatorio, actual)


def pedir_telefono(etiqueta, obligatorio=True, actual=None) -> str | None:
    def convertir(texto):
        if not _RE_TELEFONO.match(texto) or sum(c.isdigit() for c in texto) < 7:
            raise ValueError("Teléfono inválido: entre 7 y 20 caracteres, solo dígitos, espacios, + - ( ).")
        return texto
    return _pedir(etiqueta, convertir, obligatorio, actual)


def pedir_si_no(etiqueta, actual=None) -> int:
    def convertir(texto):
        if texto.lower() in ("s", "si", "sí", "1"):
            return 1
        if texto.lower() in ("n", "no", "0"):
            return 0
        raise ValueError("Responda s (sí) o n (no).")
    if actual is not None:
        return int(_pedir(etiqueta + " (s/n)", convertir, True, int(bool(actual)), "Sí" if actual else "No"))
    return _pedir(etiqueta + " (s/n)", convertir, True)


def confirmar(pregunta: str) -> bool:
    try:
        return pedir_si_no(pregunta) == 1
    except Cancelado:
        return False


def pedir_opcion(etiqueta, opciones: dict, obligatorio=True, actual=None):
    """opciones: {valor_bd: texto_visible}. Se elige por número."""
    claves = list(opciones)
    for i, clave in enumerate(claves, start=1):
        print(f"    {i}. {opciones[clave]}")

    def convertir(texto):
        if texto.isdigit() and 1 <= int(texto) <= len(claves):
            return claves[int(texto) - 1]
        raise ValueError(f"Elija un número entre 1 y {len(claves)}.")
    return _pedir(etiqueta, convertir, obligatorio, actual, opciones.get(actual))


def pedir_id(etiqueta, ids_validos=None, obligatorio=True, actual=None) -> int | None:
    def convertir(texto):
        if not texto.isdigit() or int(texto) <= 0:
            raise ValueError("El ID debe ser un número entero positivo.")
        if ids_validos is not None and int(texto) not in ids_validos:
            raise ValueError("Ese ID no está en la lista.")
        return int(texto)
    return _pedir(etiqueta, convertir, obligatorio, actual)


def pedir_password(nueva_opcional=False) -> str | None:
    """Pide la contraseña dos veces y devuelve su hash.
    Con nueva_opcional=True, Enter devuelve None (conservar la actual)."""
    while True:
        texto = getpass.getpass("  Contraseña" + (" nueva (Enter = conservar)" if nueva_opcional else "") + ": ")
        if texto.strip().lower() == PALABRA_CANCELAR:
            raise Cancelado("Operación cancelada.")
        if texto == "" and nueva_opcional:
            return None
        if len(texto) < 6:
            print("    [!] La contraseña debe tener al menos 6 caracteres.")
            continue
        if getpass.getpass("  Repita la contraseña: ") != texto:
            print("    [!] Las contraseñas no coinciden.")
            continue
        return hashear_password(texto)


def hashear_password(texto: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", texto.encode("utf-8"), salt, 100_000)
    return f"pbkdf2_sha256${salt.hex()}${digest.hex()}"
