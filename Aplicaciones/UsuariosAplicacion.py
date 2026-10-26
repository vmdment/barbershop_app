from Entidades import Usuarios
from Repositorios import UsuariosRepositorio
from Utilidades import Errores


class UsuariosAplicacion:
    repositorio: UsuariosRepositorio.UsuariosRepositorio = None

    def __init__(self):
        self.repositorio = UsuariosRepositorio.UsuariosRepositorio()

    def Consultar(self) -> list:
        return self.repositorio.Consultar()

    def BuscarPorId(self, id: int) -> Usuarios.Usuarios | None:
        return self.repositorio.BuscarPorId(id)

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
