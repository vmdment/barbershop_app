from Aplicaciones import VentasAplicacion
from Controladores import Permisos
from Controladores.ControladorBase import ControladorBase
from Entidades import Ventas
from Controladores.Permisos import ADMIN, BARBERO, Prohibido

VENDEDORES = (ADMIN, BARBERO)


class VentasControlador(ControladorBase):
    """El barbero registra sus ventas (él queda como vendedor), elige el cliente y solo ve las suyas.
    Eliminar una venta queda para el administrador, que ve las suyas y las de los barberos de sus barberías."""

    def __init__(self):
        super().__init__("ventas", Ventas.Ventas, VentasAplicacion.VentasAplicacion(),
                         leer=VENDEDORES, escribir=VENDEDORES, eliminar=(ADMIN,))

    def PrepararDatos(self, datos: dict, nuevo: bool) -> None:
        sesion = Permisos.SesionActual()
        if sesion.rol == BARBERO:
            datos["seller_user_id"] = sesion.usuario_id

    def EnAlcance(self, venta, alcance: Permisos.Alcance) -> bool:
        vendedor = venta.GetSellerUserId()
        return vendedor == Permisos.SesionActual().usuario_id or vendedor in alcance.usuarios_barberos

    def Autorizar(self, venta, accion: str) -> None:
        sesion = Permisos.SesionActual()
        if sesion.EsAdmin():
            super().Autorizar(venta, accion)
        elif venta.GetSellerUserId() != sesion.usuario_id:
            raise Prohibido("Solo puede ver o modificar sus propias ventas.")

    def FiltrarLista(self, ventas: list) -> list:
        sesion = Permisos.SesionActual()
        if sesion.EsAdmin():
            return super().FiltrarLista(ventas)
        return [v for v in ventas if v.GetSellerUserId() == sesion.usuario_id]


controlador = VentasControlador()
blueprint = controlador.blueprint
