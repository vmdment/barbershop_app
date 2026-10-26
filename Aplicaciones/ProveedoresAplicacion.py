from Entidades import Proveedores
from Repositorios import ProveedoresRepositorio
from Utilidades import Errores


class ProveedoresAplicacion:
    repositorio: ProveedoresRepositorio.ProveedoresRepositorio = None

    def __init__(self):
        self.repositorio = ProveedoresRepositorio.ProveedoresRepositorio()

    def Consultar(self) -> list:
        return self.repositorio.Consultar()

    def BuscarPorId(self, id: int) -> Proveedores.Proveedores | None:
        return self.repositorio.BuscarPorId(id)

    def Insertar(self, entidad: Proveedores.Proveedores) -> Proveedores.Proveedores:
        self.Validar(entidad)
        return self.repositorio.Insertar(entidad)

    def Actualizar(self, entidad: Proveedores.Proveedores) -> Proveedores.Proveedores:
        self.Validar(entidad)
        return self.repositorio.Actualizar(entidad)

    def Eliminar(self, id: int) -> None:
        self.repositorio.Eliminar(id)

    def Validar(self, entidad: Proveedores.Proveedores) -> None:
        if entidad.GetCompanyName() is None or str(entidad.GetCompanyName()).strip() == "":
            raise Errores.ErrorValidacion("El nombre de la empresa es obligatorio.")
