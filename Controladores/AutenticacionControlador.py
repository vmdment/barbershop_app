"""Inicio de sesión.

    POST /api/auth/login      {"email", "password"}                      -> token + datos de la sesión (pública)
    POST /api/auth/registro   {"full_name", "email", "phone", "password"} -> crea una cuenta de Cliente (pública)
    GET  /api/auth/perfil     datos de la sesión actual (requiere token)

El token se envía en las demás rutas como `Authorization: Bearer <token>`. Cerrar sesión es borrar el
token en el cliente (no se guarda en el servidor).
"""
from Aplicaciones import RolesAplicacion, UsuariosAplicacion
from Controladores import Permisos
from Controladores.ControladorBase import ControladorBase, ErrorPeticion, LeerJson, Respuesta
from Entidades import Usuarios
from Utilidades import Validaciones

ESQUEMA_SESION = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"}, "full_name": {"type": "string"}, "email": {"type": "string"},
        "rol": {"type": "string", "enum": list(Permisos.TODOS)},
        "barber_id": {"type": "integer", "nullable": True, "description": "Solo para el rol Barbero"},
    },
}
ESQUEMA_LOGIN = {
    "type": "object",
    "properties": {"token": {"type": "string"}, "expira_en_segundos": {"type": "integer"},
                   "usuario": ESQUEMA_SESION},
}

_roles = RolesAplicacion.RolesAplicacion()


class AutenticacionControlador(ControladorBase):
    ocultos = ("password_hash",)

    def __init__(self):
        super().__init__("auth", Usuarios.Usuarios, UsuariosAplicacion.UsuariosAplicacion(), crud=False)
        self.RegistrarRuta("/login", "login", self.Login, "POST", "Iniciar sesión",
                           cuerpo={"type": "object", "required": ["email", "password"],
                                   "properties": {"email": {"type": "string", "example": "admin@barberia.com"},
                                                  "password": {"type": "string", "format": "password"}}},
                           respuesta=ESQUEMA_LOGIN, roles=None)
        self.RegistrarRuta("/registro", "registro", self.Registro, "POST",
                           "Crear una cuenta de cliente e iniciar sesión",
                           cuerpo={"type": "object", "required": ["full_name", "email", "phone", "password"],
                                   "properties": {"full_name": {"type": "string"}, "email": {"type": "string"},
                                                  "phone": {"type": "string"},
                                                  "password": {"type": "string", "format": "password",
                                                               "minLength": 6}}},
                           respuesta=ESQUEMA_LOGIN, roles=None)
        self.RegistrarRuta("/perfil", "perfil", self.Perfil, "GET", "Datos de la sesión actual",
                           respuesta=ESQUEMA_SESION, roles=Permisos.TODOS)

    @staticmethod
    def RespuestaSesion(sesion: Permisos.Sesion, codigo: int = 200):
        return Respuesta({"token": Permisos.CrearToken(sesion.usuario_id),
                          "expira_en_segundos": Permisos.DuracionSegundos(),
                          "usuario": sesion.Json()}, codigo)

    def Login(self):
        datos = LeerJson()
        email, password = datos.get("email"), datos.get("password")
        if not isinstance(email, str) or not isinstance(password, str) or not email.strip() or not password:
            raise ErrorPeticion("Envíe 'email' y 'password'.")
        usuario = self.aplicacion.BuscarPorEmail(email.strip())
        if usuario is None or not Validaciones.verificar_password(password, usuario.GetPasswordHash()):
            raise Permisos.NoAutenticado("Correo o contraseña incorrectos.")
        return self.RespuestaSesion(Permisos.CrearSesion(usuario))

    def Registro(self):
        """Cualquiera puede crear su cuenta, siempre con el rol Cliente.
        Los administradores y barberos los crea un administrador en /api/usuarios."""
        datos = LeerJson()
        password = datos.get("password")
        if not isinstance(password, str) or len(password) < 6:
            raise ErrorPeticion("La contraseña debe tener al menos 6 caracteres.")
        rol = next((r for r in _roles.Consultar() if Permisos.RolDe(r.GetName()) == Permisos.CLIENTE), None)
        if rol is None:
            raise ErrorPeticion("No existe el rol Cliente en la base. Ejecute bd.sql.")
        usuario = Usuarios.Usuarios()
        self.AplicarDatos(usuario, {campo: datos.get(campo) for campo in ("full_name", "email", "phone")})
        usuario.SetRoleId(rol.GetId())
        usuario.SetPasswordHash(Validaciones.hashear_password(password))
        usuario = self.aplicacion.Insertar(usuario)
        return self.RespuestaSesion(Permisos.CrearSesion(self.aplicacion.BuscarPorId(usuario.GetId())), 201)

    def Perfil(self):
        return Respuesta(Permisos.SesionActual().Json())


controlador = AutenticacionControlador()
blueprint = controlador.blueprint
