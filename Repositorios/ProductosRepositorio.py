from Entidades import Productos
from Utilidades import Conexion


class ProductosRepositorio:

    def Consultar(self) -> list:
        filas: list = Conexion.conexion.call("proc_select_all_products")
        return [self.__Construir(fila) for fila in filas]

    def ConsultarDisponibles(self) -> list:
        filas: list = Conexion.conexion.call("proc_select_products")
        return [self.__Construir(fila) for fila in filas]

    def ConsultarStockBajo(self) -> list:
        filas: list = Conexion.conexion.call("proc_select_low_stock_products")
        return [self.__Construir(fila) for fila in filas]

    def BuscarPorId(self, id: int) -> Productos.Productos | None:
        filas: list = Conexion.conexion.call("proc_select_product_by_id", (id,))
        if not filas:
            return None
        return self.__Construir(filas[0])

    def Insertar(self, entidad: Productos.Productos) -> Productos.Productos:
        filas: list = Conexion.conexion.call(
            "proc_insert_product",
            (
                entidad.GetBarbershopId(),
                entidad.GetBarberId(),
                entidad.GetName(),
                entidad.GetDescription(),
                entidad.GetSellingPrice(),
                entidad.GetStockQuantity(),
                entidad.GetMinStockLevel(),
            ),
        )
        entidad.SetId(int(filas[0]["id"]))
        return entidad

    def Actualizar(self, entidad: Productos.Productos) -> Productos.Productos:
        Conexion.conexion.call(
            "proc_update_product",
            (
                entidad.GetId(),
                entidad.GetBarbershopId(),
                entidad.GetBarberId(),
                entidad.GetName(),
                entidad.GetDescription(),
                entidad.GetSellingPrice(),
                entidad.GetStockQuantity(),
                entidad.GetMinStockLevel(),
            ),
        )
        return entidad

    def Eliminar(self, id: int) -> None:
        Conexion.conexion.call("proc_delete_product", (id,))

    def __Construir(self, fila: dict) -> Productos.Productos:
        entidad: Productos.Productos = Productos.Productos()
        entidad.SetId(fila.get("id"))
        entidad.SetBarbershopId(fila.get("barbershop_id"))
        entidad.SetBarbershopName(fila.get("barbershop_name"))
        entidad.SetBarberId(fila.get("barber_id"))
        entidad.SetBarberName(fila.get("barber_name"))
        entidad.SetName(fila.get("name"))
        entidad.SetDescription(fila.get("description"))
        entidad.SetSellingPrice(fila.get("selling_price"))
        entidad.SetStockQuantity(fila.get("stock_quantity"))
        entidad.SetMinStockLevel(fila.get("min_stock_level"))
        return entidad
