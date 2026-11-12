"""Registro de accesos al sistema (tabla access_log).

    GET /api/accesos?limite=200   Administrador: accesos de él, de los barberos de sus barberías, de los
                                  clientes y los intentos con correos que no existen.
    GET /api/accesos/mios         Cualquier usuario: sus últimos 20 accesos (incluye intentos fallidos
                                  con su correo).

Los eventos se registran en AutenticacionControlador: Login, Failed (contraseña incorrecta o acceso
negado), Register (cuenta nueva) y Logout (cerrar sesión).
"""
import flask

from Aplicaciones import AccesosAplicacion
from Controladores import Permisos
from Controladores.ControladorBase import ControladorBase, Respuesta
from Entidades import Accesos

EVENTOS = {"Login": "Inicio de sesión", "Failed": "Intento fallido", "Register": "Cuenta creada", "Logout": "Cierre de sesión"}


def Registrar(user_id, email, evento) -> None:
    """Guarda un acceso de la petición actual. Si falla, solo se anota en el log: nunca impide entrar."""
    try:
        AccesosAplicacion.AccesosAplicacion().Registrar(
            user_id, email, evento, flask.request.remote_addr, flask.request.headers.get("User-Agent"))
    except Exception:
        flask.current_app.logger.exception("No se pudo registrar el acceso")


class AccesosControlador(ControladorBase):

    def __init__(self):
        super().__init__("accesos", Accesos.Accesos, AccesosAplicacion.AccesosAplicacion(), crud=False)
        self.RegistrarRuta("", "consultar", self.Consultar, "GET", "Registro de accesos (más recientes primero)",
                           parametros=[], lista=True, roles=(Permisos.ADMIN,))
        self.RegistrarRuta("/mios", "mios", self.ConsultarMios, "GET", "Mis últimos accesos",
                           lista=True, roles=Permisos.TODOS)

    def EnAlcance(self, acceso, alcance: Permisos.Alcance) -> bool:
        if acceso.GetUserId() is None:          # correo que no existe o usuario ya eliminado
            return True
        if acceso.GetUserId() == Permisos.SesionActual().usuario_id:
            return True
        return (acceso.GetUserId() in alcance.usuarios_barberos
                or Permisos.RolDe(acceso.GetRoleName()) == Permisos.CLIENTE)

    def Consultar(self):
        limite = flask.request.args.get("limite", "200")
        limite = int(limite) if limite.isdigit() else 200
        return Respuesta(self.ListaJson(self.FiltrarLista(self.aplicacion.Consultar(None, limite))))

    def ConsultarMios(self):
        return Respuesta(self.ListaJson(self.aplicacion.Consultar(Permisos.SesionActual().usuario_id, 20)))


controlador = AccesosControlador()
blueprint = controlador.blueprint
