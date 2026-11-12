from Entidades import Usuarios
from Repositorios import UsuariosRepositorio
from Utilidades import Errores


FOTO_MAX_BYTES = 2 * 1024 * 1024


def TipoImagen(content: bytes) -> str | None:
    """Tipo de imagen según sus primeros bytes."""
    if content.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        return "image/webp"
    return None


class UsuariosAplicacion:
    repositorio: UsuariosRepositorio.UsuariosRepositorio = None

    def __init__(self):
        self.repositorio = UsuariosRepositorio.UsuariosRepositorio()

    def Consultar(self) -> list:
        return self.repositorio.Consultar()

    def BuscarPorId(self, id: int) -> Usuarios.Usuarios | None:
        return self.repositorio.BuscarPorId(id)

    def BuscarPorEmail(self, email: str) -> Usuarios.Usuarios | None:
        return self.repositorio.BuscarPorEmail(email)

    def BuscarFoto(self, user_id: int) -> dict | None:
        return self.repositorio.BuscarFoto(user_id)

    def GuardarFoto(self, user_id: int, content: bytes) -> None:
        """Valida que sea una imagen JPG, PNG o WEBP (por su contenido, no por el nombre) de hasta 2 MB."""
        if not content:
            raise Errores.ErrorValidacion("La foto está vacía.")
        if len(content) > FOTO_MAX_BYTES:
            raise Errores.ErrorValidacion("La foto no puede pesar más de 2 MB.")
        tipo = TipoImagen(content)
        if tipo is None:
            raise Errores.ErrorValidacion("La foto debe ser una imagen JPG, PNG o WEBP.")
        self.repositorio.GuardarFoto(user_id, tipo, content)

    def EliminarFoto(self, user_id: int) -> None:
        self.repositorio.EliminarFoto(user_id)

    def Insertar(self, entidad: Usuarios.Usuarios) -> Usuarios.Usuarios:
        self.Validar(entidad)
        return self.repositorio.Insertar(entidad)

    def Actualizar(self, entidad: Usuarios.Usuarios) -> Usuarios.Usuarios:
        self.Validar(entidad)
        return self.repositorio.Actualizar(entidad)

    def Eliminar(self, id: int) -> None:
        self.repositorio.Eliminar(id)

    def Validar(self, entidad: Usuarios.Usuarios) -> None:
        if entidad.GetFullName() is None or str(entidad.GetFullName()).strip() == "":
            raise Errores.ErrorValidacion("El nombre completo es obligatorio.")
