from Entidades import Productos
from Repositorios import ProductosRepositorio
from Utilidades import Errores


class ProductosAplicacion:
    repositorio: ProductosRepositorio.ProductosRepositorio = None

    def __init__(self):
        self.repositorio = ProductosRepositorio.ProductosRepositorio()

    def Consultar(self) -> list:
        return self.repositorio.Consultar()

    def ConsultarDisponibles(self) -> list:
        return self.repositorio.ConsultarDisponibles()

    def ConsultarStockBajo(self) -> list:
        return self.repositorio.ConsultarStockBajo()

    def BuscarPorId(self, id: int) -> Productos.Productos | None:
        return self.repositorio.BuscarPorId(id)

    def Insertar(self, entidad: Productos.Productos) -> Productos.Productos:
        self.Validar(entidad)
        return self.repositorio.Insertar(entidad)

    def Actualizar(self, entidad: Productos.Productos) -> Productos.Productos:
        self.Validar(entidad)
        return self.repositorio.Actualizar(entidad)

    def Eliminar(self, id: int) -> None:
        self.repositorio.Eliminar(id)

    def Validar(self, entidad: Productos.Productos) -> None:
        if entidad.GetName() is None or str(entidad.GetName()).strip() == "":
            raise Errores.ErrorValidacion("El nombre del producto es obligatorio.")
        if entidad.GetBarbershopId() is None and entidad.GetBarberId() is None:
            raise Errores.ErrorValidacion("El producto debe pertenecer a una barbería o a un barbero.")
