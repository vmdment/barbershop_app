from Aplicaciones import DetalleVentasAplicacion, VentasAplicacion
from Controladores import Permisos, VentasControlador
from Controladores.ControladorBase import ControladorBase, LeerEnteroQuery, NoEncontrado, Respuesta
from Entidades import DetalleVentas
from Controladores.Permisos import ADMIN, BARBERO, Prohibido

VENDEDORES = (ADMIN, BARBERO)
_ventas = VentasAplicacion.VentasAplicacion()


class DetalleVentasControlador(ControladorBase):
    """Productos de una venta. El barbero solo ve y modifica el detalle de sus propias ventas y no cambia
    el precio: se cobra el precio de venta del producto."""

    def __init__(self):
        super().__init__("detalle-ventas", DetalleVentas.DetalleVentas,
                         DetalleVentasAplicacion.DetalleVentasAplicacion(), filtro="product_sale_id",
                         leer=VENDEDORES, escribir=VENDEDORES)

    def ValidarVenta(self, product_sale_id) -> None:
        venta = _ventas.BuscarPorId(product_sale_id) if product_sale_id else None
        if venta is None:
            raise NoEncontrado(f"No existe la venta con ID {product_sale_id}.")
        VentasControlador.controlador.Autorizar(venta, "ver")

    def PrepararDatos(self, datos: dict, nuevo: bool) -> None:
        if Permisos.SesionActual().rol == BARBERO and datos.get("unit_price") not in (None, ""):
            raise Prohibido("El barbero no puede cambiar el precio: se cobra el precio de venta del producto.")

    def Autorizar(self, detalle, accion: str) -> None:
        self.ValidarVenta(detalle.GetProductSaleId())

    def Consultar(self):
        product_sale_id = LeerEnteroQuery("product_sale_id")
        self.ValidarVenta(product_sale_id)
        return Respuesta(self.ListaJson(self.aplicacion.Consultar(product_sale_id)))


controlador = DetalleVentasControlador()
blueprint = controlador.blueprint
