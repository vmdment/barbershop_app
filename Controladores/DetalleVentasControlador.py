from Aplicaciones import DetalleVentasAplicacion, VentasAplicacion
from Controladores import Permisos
from Controladores.ControladorBase import ControladorBase, LeerEnteroQuery, NoEncontrado, Respuesta
from Entidades import DetalleVentas
from Controladores.Permisos import ADMIN, BARBERO, Prohibido

VENDEDORES = (ADMIN, BARBERO)
_ventas = VentasAplicacion.VentasAplicacion()


class DetalleVentasControlador(ControladorBase):
    """Productos de una venta. El barbero solo ve y modifica el detalle de sus propias ventas."""

    def __init__(self):
        super().__init__("detalle-ventas", DetalleVentas.DetalleVentas,
                         DetalleVentasAplicacion.DetalleVentasAplicacion(), filtro="product_sale_id",
                         leer=VENDEDORES, escribir=VENDEDORES)

    def ValidarVenta(self, product_sale_id) -> None:
        sesion = Permisos.SesionActual()
        if sesion.EsAdmin():
            return
        venta = _ventas.BuscarPorId(product_sale_id) if product_sale_id else None
        if venta is None:
            raise NoEncontrado(f"No existe la venta con ID {product_sale_id}.")
        if venta.GetSellerUserId() != sesion.usuario_id:
            raise Prohibido("Solo puede ver o modificar el detalle de sus propias ventas.")

    def Autorizar(self, detalle, accion: str) -> None:
        self.ValidarVenta(detalle.GetProductSaleId())

    def Consultar(self):
        product_sale_id = LeerEnteroQuery("product_sale_id")
        self.ValidarVenta(product_sale_id)
        return Respuesta(self.ListaJson(self.aplicacion.Consultar(product_sale_id)))


controlador = DetalleVentasControlador()
blueprint = controlador.blueprint
