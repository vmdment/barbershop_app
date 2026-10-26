from Entidades import Proveedores
from Utilidades import Conexion


class ProveedoresRepositorio:

    def Consultar(self) -> list:
        filas: list = Conexion.conexion.call("proc_select_suppliers")
        return [self.__Construir(fila) for fila in filas]

    def BuscarPorId(self, id: int) -> Proveedores.Proveedores | None:
        filas: list = Conexion.conexion.call("proc_select_supplier_by_id", (id,))
        if not filas:
            return None
        return self.__Construir(filas[0])

    def Insertar(self, entidad: Proveedores.Proveedores) -> Proveedores.Proveedores:
        filas: list = Conexion.conexion.call(
            "proc_insert_supplier",
            (
                entidad.GetCompanyName(),
                entidad.GetContactName(),
                entidad.GetPhone(),
                entidad.GetEmail(),
                entidad.GetAddress(),
            ),
        )
        entidad.SetId(int(filas[0]["id"]))
        return entidad

    def Actualizar(self, entidad: Proveedores.Proveedores) -> Proveedores.Proveedores:
        Conexion.conexion.call(
            "proc_update_supplier",
            (
                entidad.GetId(),
                entidad.GetCompanyName(),
                entidad.GetContactName(),
                entidad.GetPhone(),
                entidad.GetEmail(),
                entidad.GetAddress(),
            ),
        )
        return entidad

    def Eliminar(self, id: int) -> None:
        Conexion.conexion.call("proc_delete_supplier", (id,))

    def __Construir(self, fila: dict) -> Proveedores.Proveedores:
        entidad: Proveedores.Proveedores = Proveedores.Proveedores()
        entidad.SetId(fila.get("id"))
        entidad.SetCompanyName(fila.get("company_name"))
        entidad.SetContactName(fila.get("contact_name"))
        entidad.SetPhone(fila.get("phone"))
        entidad.SetEmail(fila.get("email"))
        entidad.SetAddress(fila.get("address"))
        return entidad
