from Entidades import Ventas
from Repositorios import VentasRepositorio


class VentasAplicacion:
    repositorio: VentasRepositorio.VentasRepositorio = None

    def __init__(self):
        self.repositorio = VentasRepositorio.VentasRepositorio()

    def Consultar(self) -> list:
        return self.repositorio.Consultar()

    def BuscarPorId(self, id: int) -> Ventas.Ventas | None:
        return self.repositorio.BuscarPorId(id)

    def Insertar(self, entidad: Ventas.Ventas) -> Ventas.Ventas:
        return self.repositorio.Insertar(entidad)

    def Actualizar(self, entidad: Ventas.Ventas) -> Ventas.Ventas:
        return self.repositorio.Actualizar(entidad)

    def Eliminar(self, id: int) -> None:
        self.repositorio.Eliminar(id)
