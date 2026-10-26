from Entidades import Barberias
from Utilidades import Conexion


class BarberiasRepositorio:

    def Consultar(self) -> list:
        filas: list = Conexion.conexion.call("proc_select_barbershops")
        return [self.__Construir(fila) for fila in filas]

    def BuscarPorId(self, id: int) -> Barberias.Barberias | None:
        filas: list = Conexion.conexion.call("proc_select_barbershop_by_id", (id,))
        if not filas:
            return None
        return self.__Construir(filas[0])

    def Insertar(self, entidad: Barberias.Barberias) -> Barberias.Barberias:
        filas: list = Conexion.conexion.call(
            "proc_insert_barbershop",
            (
                entidad.GetManagerId(),
                entidad.GetName(),
                entidad.GetAddress(),
                entidad.GetCity(),
                entidad.GetPhone(),
            ),
        )
        entidad.SetId(int(filas[0]["id"]))
        return entidad

    def Actualizar(self, entidad: Barberias.Barberias) -> Barberias.Barberias:
        Conexion.conexion.call(
            "proc_update_barbershop",
            (
                entidad.GetId(),
                entidad.GetManagerId(),
                entidad.GetName(),
                entidad.GetAddress(),
                entidad.GetCity(),
                entidad.GetPhone(),
            ),
        )
        return entidad

    def Eliminar(self, id: int) -> None:
        Conexion.conexion.call("proc_delete_barbershop", (id,))

    def __Construir(self, fila: dict) -> Barberias.Barberias:
        entidad: Barberias.Barberias = Barberias.Barberias()
        entidad.SetId(fila.get("id"))
        entidad.SetManagerId(fila.get("manager_id"))
        entidad.SetManagerName(fila.get("manager_name"))
        entidad.SetName(fila.get("name"))
        entidad.SetAddress(fila.get("address"))
        entidad.SetCity(fila.get("city"))
        entidad.SetPhone(fila.get("phone"))
        return entidad
