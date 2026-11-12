import flask

from Aplicaciones import UsuariosAplicacion
from Controladores import Permisos
from Controladores.ControladorBase import ControladorBase, ErrorPeticion, NoEncontrado, Respuesta
from Entidades import Usuarios
from Utilidades import Validaciones


class UsuariosControlador(ControladorBase):
    """Solo el administrador maneja usuarios. GET /api/usuarios/clientes le da al barbero (y al
    administrador) la lista de clientes, solo con nombre y correo, para asociarlos a una venta."""
    # El hash de la contraseña nunca sale en las respuestas
    ocultos = ("password_hash",)
    # Campo extra que aparece en el Swagger: solo se envía, nunca se devuelve
    extrasEsquema = {"password": {"type": "string", "format": "password", "writeOnly": True, "minLength": 6,
                                  "description": "Obligatorio al registrar; al actualizar, omítalo para "
                                                 "conservar la contraseña actual."}}

    def __init__(self):
        super().__init__("usuarios", Usuarios.Usuarios, UsuariosAplicacion.UsuariosAplicacion())
        self.RegistrarRuta("/clientes", "clientes", self.ConsultarClientes, "GET",
                           "Clientes (id, nombre y correo) para elegir en una venta",
                           respuesta={"type": "array", "items": {"type": "object", "properties": {
                               "id": {"type": "integer"}, "full_name": {"type": "string"},
                               "email": {"type": "string"}}}},
                           roles=(Permisos.ADMIN, Permisos.BARBERO))
        self.RegistrarRuta("/<int:id>/foto", "foto", self.Foto, "GET",
                           "Foto de perfil del usuario (imagen; 404 si no tiene)",
                           respuesta={"type": "string", "format": "binary"}, roles=Permisos.TODOS)

    def Foto(self, id: int):
        """Cualquier usuario con sesión ve las fotos (ej. el cliente ve la del barbero que elige)."""
        foto = self.aplicacion.BuscarFoto(id)
        if foto is None:
            raise NoEncontrado("El usuario no tiene foto de perfil.")
        respuesta = flask.Response(foto["content"], mimetype=foto["content_type"])
        respuesta.headers["Cache-Control"] = "private, no-cache"
        return respuesta

    def ConsultarClientes(self):
        return Respuesta([{"id": u.GetId(), "full_name": u.GetFullName(), "email": u.GetEmail()}
                          for u in self.aplicacion.Consultar() if Permisos.RolDe(u.GetRoleName()) == Permisos.CLIENTE])

    def PrepararDatos(self, datos: dict, nuevo: bool) -> None:
        """Se recibe "password" en texto plano y se guarda su hash (igual que la consola).
        Al actualizar, si no se envía "password" se conserva la contraseña actual."""
        datos.pop("password_hash", None)
        password = datos.pop("password", None)
        if password is None:
            if nuevo:
                raise ErrorPeticion("El campo 'password' es obligatorio.")
            return
        if not isinstance(password, str) or len(password) < 6:
            raise ErrorPeticion("La contraseña debe tener al menos 6 caracteres.")
        datos["password_hash"] = Validaciones.hashear_password(password)


controlador = UsuariosControlador()
blueprint = controlador.blueprint
