from Entidades import DetalleVentas
from Utilidades import Conexion


class DetalleVentasRepositorio:

    def Consultar(self, product_sale_id: int) -> list:
        filas: list = Conexion.conexion.call("proc_select_product_sale_details", (product_sale_id,))
        return [self.__Construir(fila) for fila in filas]

    def BuscarPorId(self, id: int) -> DetalleVentas.DetalleVentas | None:
        filas: list = Conexion.conexion.call("proc_select_product_sale_detail_by_id", (id,))
        if not filas:
            return None
        return self.__Construir(filas[0])

    def Insertar(self, entidad: DetalleVentas.DetalleVentas) -> DetalleVentas.DetalleVentas:
        filas: list = Conexion.conexion.call(
            "proc_insert_product_sale_detail",
            (
                entidad.GetProductSaleId(),
                entidad.GetProductId(),
                entidad.GetQuantity(),
                entidad.GetUnitPrice(),
            ),
        )
        entidad.SetId(int(filas[0]["id"]))
        return entidad

    def Actualizar(self, entidad: DetalleVentas.DetalleVentas) -> DetalleVentas.DetalleVentas:
        Conexion.conexion.call(
            "proc_update_product_sale_detail",
            (
                entidad.GetId(),
                entidad.GetQuantity(),
                entidad.GetUnitPrice(),
            ),
        )
        return entidad

    def Eliminar(self, id: int) -> None:
        Conexion.conexion.call("proc_delete_product_sale_detail", (id,))

    def __Construir(self, fila: dict) -> DetalleVentas.DetalleVentas:
        entidad: DetalleVentas.DetalleVentas = DetalleVentas.DetalleVentas()
        entidad.SetId(fila.get("id"))
        entidad.SetProductSaleId(fila.get("product_sale_id"))
        entidad.SetProductId(fila.get("product_id"))
        entidad.SetProductName(fila.get("product_name"))
        entidad.SetQuantity(fila.get("quantity"))
        entidad.SetUnitPrice(fila.get("unit_price"))
        entidad.SetSubtotal(fila.get("subtotal"))
        return entidad
