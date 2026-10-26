from Entidades import Ventas
from Utilidades import Conexion


class VentasRepositorio:

    def Consultar(self) -> list:
        filas: list = Conexion.conexion.call("proc_select_product_sales")
        return [self.__Construir(fila) for fila in filas]

    def BuscarPorId(self, id: int) -> Ventas.Ventas | None:
        filas: list = Conexion.conexion.call("proc_select_product_sale_by_id", (id,))
        if not filas:
            return None
        return self.__Construir(filas[0])

    def Insertar(self, entidad: Ventas.Ventas) -> Ventas.Ventas:
        filas: list = Conexion.conexion.call(
            "proc_insert_product_sale",
            (
                entidad.GetCustomerId(),
                entidad.GetSellerUserId(),
                entidad.GetPaymentMethod(),
            ),
        )
        entidad.SetId(int(filas[0]["id"]))
        return entidad

    def Actualizar(self, entidad: Ventas.Ventas) -> Ventas.Ventas:
        Conexion.conexion.call(
            "proc_update_product_sale",
            (
                entidad.GetId(),
                entidad.GetCustomerId(),
                entidad.GetSellerUserId(),
                entidad.GetPaymentMethod(),
            ),
        )
        return entidad

    def Eliminar(self, id: int) -> None:
        Conexion.conexion.call("proc_delete_product_sale", (id,))

    def __Construir(self, fila: dict) -> Ventas.Ventas:
        entidad: Ventas.Ventas = Ventas.Ventas()
        entidad.SetId(fila.get("id"))
        entidad.SetCustomerId(fila.get("customer_id"))
        entidad.SetCustomerName(fila.get("customer_name"))
        entidad.SetSellerUserId(fila.get("seller_user_id"))
        entidad.SetSellerName(fila.get("seller_name"))
        entidad.SetSaleDatetime(fila.get("sale_datetime"))
        entidad.SetTotalAmount(fila.get("total_amount"))
        entidad.SetPaymentMethod(fila.get("payment_method"))
        return entidad
