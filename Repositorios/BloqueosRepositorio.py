from Entidades import Bloqueos
from Utilidades import Conexion


class BloqueosRepositorio:

    def Consultar(self, barber_id: int) -> list:
        filas: list = Conexion.conexion.call("proc_select_schedule_blocks", (barber_id,))
        return [self.__Construir(fila) for fila in filas]

    def BuscarPorId(self, id: int) -> Bloqueos.Bloqueos | None:
        filas: list = Conexion.conexion.call("proc_select_schedule_block_by_id", (id,))
        if not filas:
            return None
        return self.__Construir(filas[0])

    def Insertar(self, entidad: Bloqueos.Bloqueos) -> Bloqueos.Bloqueos:
        filas: list = Conexion.conexion.call(
            "proc_insert_schedule_block",
            (
                entidad.GetBarberId(),
                entidad.GetStartDatetime(),
                entidad.GetEndDatetime(),
                entidad.GetReason(),
            ),
        )
        entidad.SetId(int(filas[0]["id"]))
        return entidad

    def Actualizar(self, entidad: Bloqueos.Bloqueos) -> Bloqueos.Bloqueos:
        Conexion.conexion.call(
            "proc_update_schedule_block",
            (
                entidad.GetId(),
                entidad.GetBarberId(),
                entidad.GetStartDatetime(),
                entidad.GetEndDatetime(),
                entidad.GetReason(),
            ),
        )
        return entidad

    def Eliminar(self, id: int) -> None:
        Conexion.conexion.call("proc_delete_schedule_block", (id,))

    def __Construir(self, fila: dict) -> Bloqueos.Bloqueos:
        entidad: Bloqueos.Bloqueos = Bloqueos.Bloqueos()
        entidad.SetId(fila.get("id"))
        entidad.SetBarberId(fila.get("barber_id"))
        entidad.SetStartDatetime(fila.get("start_datetime"))
        entidad.SetEndDatetime(fila.get("end_datetime"))
        entidad.SetReason(fila.get("reason"))
        return entidad
