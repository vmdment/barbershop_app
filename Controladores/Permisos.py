"""Inicio de sesión y permisos por rol de la API REST.

El cliente inicia sesión con POST /api/auth/login y recibe un token firmado. En cada petición lo envía en
la cabecera:

    Authorization: Bearer <token>

El token solo guarda el ID del usuario; el rol se vuelve a leer de la base en cada petición, así que un
cambio de rol o la eliminación del usuario se aplican de inmediato.

Roles (por el nombre de la tabla `role`, sin distinguir mayúsculas):

    Administrador          -> ADMIN    todos los permisos
    Barbero                -> BARBERO  gestiona sus citas y vende productos
    Cliente (o Usuario)    -> CLIENTE  solicita y cancela sus citas, elige barbero

Un usuario con otro rol (ej. "Asistente") no puede iniciar sesión.
"""
import secrets
from dataclasses import dataclass

import flask
import itsdangerous

from Aplicaciones import BarberosAplicacion, UsuariosAplicacion
from Utilidades import Configuracion

ADMIN = "Administrador"
BARBERO = "Barbero"
CLIENTE = "Cliente"

TODOS = (ADMIN, BARBERO, CLIENTE)
SOLO_ADMIN = (ADMIN,)

# Nombre del rol en la base (en minúsculas) -> rol de la API
NOMBRES_ROL = {
    "administrador": ADMIN,
    "admin": ADMIN,
    "barbero": BARBERO,
    "cliente": CLIENTE,
    "usuario": CLIENTE,
}


class NoAutenticado(Exception):
    """Falta el token, es inválido o venció (HTTP 401)."""


class Prohibido(Exception):
    """El usuario inició sesión pero su rol no permite la operación (HTTP 403)."""


@dataclass
class Sesion:
    usuario_id: int
    rol: str                  # ADMIN, BARBERO o CLIENTE
    nombre: str
    email: str
    barbero_id: int | None    # solo para el rol BARBERO

    def EsAdmin(self) -> bool:
        return self.rol == ADMIN

    def Json(self) -> dict:
        return {"id": self.usuario_id, "full_name": self.nombre, "email": self.email,
                "rol": self.rol, "barber_id": self.barbero_id}


def RolDe(nombre_rol: str | None) -> str | None:
    return NOMBRES_ROL.get((nombre_rol or "").strip().lower())


# ------------------------------------------------------------------
# Token
# ------------------------------------------------------------------

_clave_temporal = secrets.token_hex(32)


def _Serializador() -> itsdangerous.URLSafeTimedSerializer:
    clave = Configuracion.Configuracion.Valor("CLAVE_SECRETA") or _clave_temporal
    return itsdangerous.URLSafeTimedSerializer(clave, salt="sesion-barbershop")


def DuracionSegundos() -> int:
    horas = Configuracion.Configuracion.Valor("SESION_HORAS", "8")
    try:
        return max(1, int(float(horas) * 3600))
    except ValueError:
        return 8 * 3600


def CrearToken(usuario_id: int) -> str:
    return _Serializador().dumps({"id": usuario_id})


def _LeerToken() -> int:
    cabecera = flask.request.headers.get("Authorization", "")
    tipo, _, token = cabecera.partition(" ")
    if tipo.lower() != "bearer" or not token.strip():
        raise NoAutenticado("Debe iniciar sesión (cabecera 'Authorization: Bearer <token>').")
    try:
        datos = _Serializador().loads(token.strip(), max_age=DuracionSegundos())
    except itsdangerous.SignatureExpired:
        raise NoAutenticado("La sesión venció. Inicie sesión de nuevo.") from None
    except itsdangerous.BadData:
        raise NoAutenticado("Token de sesión inválido.") from None
    if not isinstance(datos, dict) or not isinstance(datos.get("id"), int):
        raise NoAutenticado("Token de sesión inválido.")
    return datos["id"]


# ------------------------------------------------------------------
# Sesión de la petición
# ------------------------------------------------------------------

_usuarios = UsuariosAplicacion.UsuariosAplicacion()
_barberos = BarberosAplicacion.BarberosAplicacion()


def CrearSesion(usuario) -> Sesion:
    """Arma la sesión de un usuario de la base. Lanza Prohibido si su rol no tiene acceso."""
    rol = RolDe(usuario.GetRoleName())
    if rol is None:
        raise Prohibido(f"El rol '{usuario.GetRoleName()}' no tiene acceso a la aplicación.")
    barbero_id = None
    if rol == BARBERO:
        barbero = _barberos.BuscarPorUsuario(usuario.GetId())
        if barbero is None:
            raise Prohibido("El usuario tiene rol Barbero pero no está registrado como barbero.")
        if not barbero.GetIsActive():
            raise Prohibido("El barbero está inactivo.")
        barbero_id = barbero.GetId()
    return Sesion(usuario.GetId(), rol, usuario.GetFullName(), usuario.GetEmail(), barbero_id)


def Autorizar(roles: tuple | None) -> None:
    """Valida el token y el rol de la petición actual. roles=None: ruta pública."""
    flask.g.sesion = None
    if roles is None:
        return
    usuario = _usuarios.BuscarPorId(_LeerToken())
    if usuario is None:
        raise NoAutenticado("El usuario de la sesión ya no existe.")
    sesion = CrearSesion(usuario)
    if sesion.rol not in roles:
        raise Prohibido(f"El rol {sesion.rol} no tiene permiso para esta operación.")
    flask.g.sesion = sesion


def SesionActual() -> Sesion:
    sesion = flask.g.get("sesion")
    if sesion is None:
        raise NoAutenticado("Debe iniciar sesión.")
    return sesion
