from Entidades import Roles
from Repositorios import RolesRepositorio
from Utilidades import Errores


class RolesAplicacion:
    repositorio: RolesRepositorio.RolesRepositorio = None

    def __init__(self):
        self.repositorio = RolesRepositorio.RolesRepositorio()

    def Consultar(self) -> list:
        return self.repositorio.Consultar()

    def BuscarPorId(self, id: int) -> Roles.Roles | None:
        return self.repositorio.BuscarPorId(id)

    def Insertar(self, entidad: Roles.Roles) -> Roles.Roles:
        self.Validar(entidad)
        return self.repositorio.Insertar(entidad)

    def Actualizar(self, entidad: Roles.Roles) -> Roles.Roles:
        self.Validar(entidad)
        return self.repositorio.Actualizar(entidad)

    def Eliminar(self, id: int) -> None:
        self.repositorio.Eliminar(id)

    def Validar(self, entidad: Roles.Roles) -> None:
        if entidad.GetName() is None or str(entidad.GetName()).strip() == "":
            raise Errores.ErrorValidacion("El nombre del rol es obligatorio.")
