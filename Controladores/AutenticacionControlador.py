"""Inicio de sesión y perfil del usuario.

    POST   /api/auth/login        {"email", "password"}                      -> token + sesión (pública)
    POST   /api/auth/registro     {"full_name", "email", "phone", "password"} -> crea una cuenta de Cliente (pública)
    GET    /api/auth/perfil       perfil completo de la sesión (datos, rol, barbería, si tiene foto)
    PUT    /api/auth/perfil       {"full_name"?, "phone"?, "password_actual"?, "password_nueva"?}
    PUT    /api/auth/perfil/foto  {"imagen": "data:image/png;base64,..."}  (JPG, PNG o WEBP de hasta 2 MB)
    DELETE /api/auth/perfil/foto  quita la foto

    POST   /api/auth/salir        registra el cierre de sesión (el cliente luego borra el token)

La foto de cualquier usuario se ve en GET /api/usuarios/<id>/foto (con sesión iniciada).
Cada inicio de sesión, intento fallido, cuenta nueva y salida queda en el registro de accesos
(Controladores/AccesosControlador.py).
El token se envía en las demás rutas como `Authorization: Bearer <token>`. Cerrar sesión es borrar el
token en el cliente (no se guarda en el servidor).
"""
import base64
import binascii

from Aplicaciones import BarberiasAplicacion, BarberosAplicacion, RolesAplicacion, UsuariosAplicacion
from Controladores import AccesosControlador, Permisos
from Controladores.ControladorBase import ControladorBase, ErrorPeticion, LeerJson, Respuesta, ValorJson
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
ESQUEMA_PERFIL = {
    "type": "object",
    "properties": {
        **ESQUEMA_SESION["properties"],
        "phone": {"type": "string"}, "created_at": {"type": "string", "format": "date-time"},
        "tiene_foto": {"type": "boolean"},
        "barberia": {"type": "string", "nullable": True, "description": "Barbero: su barbería"},
        "barberias": {"type": "array", "items": {"type": "string"}, "description": "Administrador: las que maneja"},
    },
}

_roles = RolesAplicacion.RolesAplicacion()
_barberias = BarberiasAplicacion.BarberiasAplicacion()
_barberos = BarberosAplicacion.BarberosAplicacion()


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
        self.RegistrarRuta("/salir", "salir", self.Salir, "POST", "Cerrar sesión (queda en el registro de accesos)",
                           respuesta="texto", roles=Permisos.TODOS)
        self.RegistrarRuta("/perfil", "perfil", self.Perfil, "GET", "Perfil de la sesión actual",
                           respuesta=ESQUEMA_PERFIL, roles=Permisos.TODOS)
        self.RegistrarRuta("/perfil", "editar_perfil", self.EditarPerfil, "PUT",
                           "Editar nombre y teléfono, o cambiar la contraseña (con la actual)",
                           cuerpo={"type": "object", "properties": {
                               "full_name": {"type": "string"}, "phone": {"type": "string"},
                               "password_actual": {"type": "string", "format": "password"},
                               "password_nueva": {"type": "string", "format": "password", "minLength": 6}}},
                           respuesta=ESQUEMA_PERFIL, roles=Permisos.TODOS)
        self.RegistrarRuta("/perfil/foto", "subir_foto", self.SubirFoto, "PUT",
                           "Subir o cambiar la foto de perfil (JPG, PNG o WEBP, hasta 2 MB)",
                           cuerpo={"type": "object", "required": ["imagen"], "properties": {
                               "imagen": {"type": "string", "description": "data URL o base64 de la imagen"}}},
                           respuesta=ESQUEMA_PERFIL, roles=Permisos.TODOS)
        self.RegistrarRuta("/perfil/foto", "quitar_foto", self.QuitarFoto, "DELETE", "Quitar la foto de perfil",
                           respuesta=ESQUEMA_PERFIL, roles=Permisos.TODOS)

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
            AccesosControlador.Registrar(usuario.GetId() if usuario else None, email, "Failed")
            raise Permisos.NoAutenticado("Correo o contraseña incorrectos.")
        try:
            sesion = Permisos.CrearSesion(usuario)
        except Permisos.Prohibido:
            AccesosControlador.Registrar(usuario.GetId(), email, "Failed")   # rol sin acceso o barbero inactivo
            raise
        AccesosControlador.Registrar(usuario.GetId(), usuario.GetEmail(), "Login")
        return self.RespuestaSesion(sesion)

    def Salir(self):
        sesion = Permisos.SesionActual()
        AccesosControlador.Registrar(sesion.usuario_id, sesion.email, "Logout")
        return Respuesta("Sesión cerrada.")

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
        AccesosControlador.Registrar(usuario.GetId(), usuario.GetEmail(), "Register")
        return self.RespuestaSesion(Permisos.CrearSesion(self.aplicacion.BuscarPorId(usuario.GetId())), 201)

    # --- Perfil ---

    def DatosPerfil(self) -> dict:
        sesion = Permisos.SesionActual()
        usuario = self.aplicacion.BuscarPorId(sesion.usuario_id)
        perfil = {**sesion.Json(), "full_name": usuario.GetFullName(), "phone": usuario.GetPhone(),
                  "created_at": ValorJson(usuario.GetCreatedAt()),
                  "tiene_foto": self.aplicacion.BuscarFoto(sesion.usuario_id) is not None}
        if sesion.rol == Permisos.BARBERO:
            barbero = _barberos.BuscarPorId(sesion.barbero_id)
            perfil.update({"barberia": barbero.GetBarbershopName(),
                           "provides_home_service": barbero.GetProvidesHomeService(),
                           "provides_shop_service": barbero.GetProvidesShopService()})
        if sesion.EsAdmin():
            perfil["barberias"] = [b.GetName() for b in _barberias.Consultar() if b.GetManagerId() == sesion.usuario_id]
        return perfil

    def Perfil(self):
        return Respuesta(self.DatosPerfil())

    def EditarPerfil(self):
        """Cada usuario cambia su nombre y teléfono. El correo y el rol solo los cambia un administrador.
        Para cambiar la contraseña hay que enviar la actual."""
        datos = LeerJson()
        sesion = Permisos.SesionActual()
        usuario = self.aplicacion.BuscarPorId(sesion.usuario_id)
        self.AplicarDatos(usuario, {c: datos[c] for c in ("full_name", "phone") if c in datos})

        nueva = datos.get("password_nueva")
        if nueva not in (None, ""):
            if not isinstance(nueva, str) or len(nueva) < 6:
                raise ErrorPeticion("La contraseña nueva debe tener al menos 6 caracteres.")
            actual = datos.get("password_actual")
            guardado = self.aplicacion.BuscarPorEmail(usuario.GetEmail())
            if not isinstance(actual, str) or not Validaciones.verificar_password(actual, guardado.GetPasswordHash()):
                raise ErrorPeticion("La contraseña actual no es correcta.")
            usuario.SetPasswordHash(Validaciones.hashear_password(nueva))
        else:
            usuario.SetPasswordHash(None)   # se conserva la actual
        self.aplicacion.Actualizar(usuario)
        return Respuesta(self.DatosPerfil())

    def SubirFoto(self):
        imagen = LeerJson().get("imagen")
        if not isinstance(imagen, str) or not imagen.strip():
            raise ErrorPeticion("Envíe la foto en 'imagen' (data URL o base64).")
        if imagen.startswith("data:"):
            imagen = imagen.partition(",")[2]
        try:
            contenido = base64.b64decode(imagen, validate=True)
        except (binascii.Error, ValueError):
            raise ErrorPeticion("La foto no está en base64 válido.") from None
        self.aplicacion.GuardarFoto(Permisos.SesionActual().usuario_id, contenido)
        return Respuesta(self.DatosPerfil())

    def QuitarFoto(self):
        self.aplicacion.EliminarFoto(Permisos.SesionActual().usuario_id)
        return Respuesta(self.DatosPerfil())


controlador = AutenticacionControlador()
blueprint = controlador.blueprint
