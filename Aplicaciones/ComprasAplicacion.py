from Entidades import Compras
from Repositorios import ComprasRepositorio
from Utilidades import Errores


class ComprasAplicacion:
    repositorio: ComprasRepositorio.ComprasRepositorio = None

    def __init__(self):
        self.repositorio = ComprasRepositorio.ComprasRepositorio()

    def Consultar(self) -> list:
        return self.repositorio.Consultar()

    def BuscarPorId(self, id: int) -> Compras.Compras | None:
        return self.repositorio.BuscarPorId(id)

    def Insertar(self, entidad: Compras.Compras) -> Compras.Compras:
        self.Validar(entidad)
        return self.repositorio.Insertar(entidad)

    def Actualizar(self, entidad: Compras.Compras) -> Compras.Compras:
        self.Validar(entidad)
        return self.repositorio.Actualizar(entidad)

    def Eliminar(self, id: int) -> None:
        self.repositorio.Eliminar(id)

    def Validar(self, entidad: Compras.Compras) -> None:
        if entidad.GetToolsDescription() is None or str(entidad.GetToolsDescription()).strip() == "":
            raise Errores.ErrorValidacion("La descripción de lo comprado es obligatoria.")
        if entidad.GetBarberId() is None and entidad.GetBarbershopId() is None:
            raise Errores.ErrorValidacion("La compra debe asignarse a un barbero o a una barbería.")
