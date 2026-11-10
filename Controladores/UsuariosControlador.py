from Aplicaciones import UsuariosAplicacion
from Controladores.ControladorBase import ControladorBase, ErrorPeticion
from Entidades import Usuarios
from Utilidades import Validaciones


class UsuariosControlador(ControladorBase):
    # El hash de la contraseña nunca sale en las respuestas
    ocultos = ("password_hash",)
    # Campo extra que aparece en el Swagger: solo se envía, nunca se devuelve
    extrasEsquema = {"password": {"type": "string", "format": "password", "writeOnly": True, "minLength": 6,
                                  "description": "Obligatorio al registrar; al actualizar, omítalo para "
                                                 "conservar la contraseña actual."}}

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


controlador = UsuariosControlador("usuarios", Usuarios.Usuarios, UsuariosAplicacion.UsuariosAplicacion())
blueprint = controlador.blueprint
