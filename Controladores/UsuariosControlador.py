from Aplicaciones import UsuariosAplicacion
from Controladores import Permisos
from Controladores.ControladorBase import ControladorBase, ErrorPeticion, Respuesta
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
