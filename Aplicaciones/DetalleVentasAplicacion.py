from Aplicaciones import ProductosAplicacion
from Entidades import DetalleVentas
from Repositorios import DetalleVentasRepositorio
from Utilidades import Errores


class DetalleVentasAplicacion:
    repositorio: DetalleVentasRepositorio.DetalleVentasRepositorio = None
    productos: ProductosAplicacion.ProductosAplicacion = None

    def __init__(self):
        self.repositorio = DetalleVentasRepositorio.DetalleVentasRepositorio()
        self.productos = ProductosAplicacion.ProductosAplicacion()

    def Consultar(self, product_sale_id: int) -> list:
        return self.repositorio.Consultar(product_sale_id)

    def BuscarPorId(self, id: int) -> DetalleVentas.DetalleVentas | None:
        return self.repositorio.BuscarPorId(id)

    def Insertar(self, entidad: DetalleVentas.DetalleVentas) -> DetalleVentas.DetalleVentas:
        self.ValidarStock(entidad)
        return self.repositorio.Insertar(entidad)

    def Actualizar(self, entidad: DetalleVentas.DetalleVentas) -> DetalleVentas.DetalleVentas:
        return self.repositorio.Actualizar(entidad)

    def Eliminar(self, id: int) -> None:
        self.repositorio.Eliminar(id)

    def ValidarStock(self, entidad: DetalleVentas.DetalleVentas) -> None:
        producto = self.productos.BuscarPorId(entidad.GetProductId())
        if producto and entidad.GetQuantity() > producto.GetStockQuantity():
            raise Errores.ErrorValidacion(
                f"Stock insuficiente: solo hay {producto.GetStockQuantity()} unidad(es).")
