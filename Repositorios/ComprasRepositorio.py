from Entidades import Compras
from Utilidades import Conexion


class ComprasRepositorio:

    def Consultar(self) -> list:
        filas: list = Conexion.conexion.call("proc_select_supplier_purchases")
        return [self.__Construir(fila) for fila in filas]

    def BuscarPorId(self, id: int) -> Compras.Compras | None:
        filas: list = Conexion.conexion.call("proc_select_supplier_purchase_by_id", (id,))
        if not filas:
            return None
        return self.__Construir(filas[0])

    def Insertar(self, entidad: Compras.Compras) -> Compras.Compras:
        filas: list = Conexion.conexion.call(
            "proc_insert_supplier_purchase",
            (
                entidad.GetSupplierId(),
                entidad.GetBarberId(),
                entidad.GetBarbershopId(),
                entidad.GetToolsDescription(),
                entidad.GetTotalPaid(),
            ),
        )
        entidad.SetId(int(filas[0]["id"]))
        return entidad

    def Actualizar(self, entidad: Compras.Compras) -> Compras.Compras:
        Conexion.conexion.call(
            "proc_update_supplier_purchase",
            (
                entidad.GetId(),
                entidad.GetSupplierId(),
                entidad.GetBarberId(),
                entidad.GetBarbershopId(),
                entidad.GetToolsDescription(),
                entidad.GetTotalPaid(),
            ),
        )
        return entidad

    def Eliminar(self, id: int) -> None:
        Conexion.conexion.call("proc_delete_supplier_purchase", (id,))

    def __Construir(self, fila: dict) -> Compras.Compras:
        entidad: Compras.Compras = Compras.Compras()
        entidad.SetId(fila.get("id"))
        entidad.SetSupplierId(fila.get("supplier_id"))
        entidad.SetCompanyName(fila.get("company_name"))
        entidad.SetBarberId(fila.get("barber_id"))
        entidad.SetBarberName(fila.get("barber_name"))
        entidad.SetBarbershopId(fila.get("barbershop_id"))
        entidad.SetBarbershopName(fila.get("barbershop_name"))
        entidad.SetPurchaseDatetime(fila.get("purchase_datetime"))
        entidad.SetToolsDescription(fila.get("tools_description"))
        entidad.SetTotalPaid(fila.get("total_paid"))
        return entidad
