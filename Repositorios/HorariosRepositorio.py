from Entidades import Horarios
from Utilidades import Conexion


class HorariosRepositorio:

    def Consultar(self, barber_id: int) -> list:
        filas: list = Conexion.conexion.call("proc_select_barber_schedule", (barber_id,))
        return [self.__Construir(fila) for fila in filas]

    def BuscarPorId(self, id: int) -> Horarios.Horarios | None:
        filas: list = Conexion.conexion.call("proc_select_barber_schedule_by_id", (id,))
        if not filas:
            return None
        return self.__Construir(filas[0])

    def Insertar(self, entidad: Horarios.Horarios) -> Horarios.Horarios:
        filas: list = Conexion.conexion.call(
            "proc_insert_barber_schedule",
            (
                entidad.GetBarberId(),
                entidad.GetDayOfWeek(),
                entidad.GetStartTime(),
                entidad.GetEndTime(),
                entidad.GetLunchStartTime(),
                entidad.GetLunchEndTime(),
            ),
        )
        entidad.SetId(int(filas[0]["id"]))
        return entidad

    def Actualizar(self, entidad: Horarios.Horarios) -> Horarios.Horarios:
        Conexion.conexion.call(
            "proc_update_barber_schedule",
            (
                entidad.GetId(),
                entidad.GetBarberId(),
                entidad.GetDayOfWeek(),
                entidad.GetStartTime(),
                entidad.GetEndTime(),
                entidad.GetLunchStartTime(),
                entidad.GetLunchEndTime(),
            ),
        )
        return entidad

    def Eliminar(self, id: int) -> None:
        Conexion.conexion.call("proc_delete_barber_schedule", (id,))

    def __Construir(self, fila: dict) -> Horarios.Horarios:
        entidad: Horarios.Horarios = Horarios.Horarios()
        entidad.SetId(fila.get("id"))
        entidad.SetBarberId(fila.get("barber_id"))
        entidad.SetDayOfWeek(fila.get("day_of_week"))
        entidad.SetStartTime(fila.get("start_time"))
        entidad.SetEndTime(fila.get("end_time"))
        entidad.SetLunchStartTime(fila.get("lunch_start_time"))
        entidad.SetLunchEndTime(fila.get("lunch_end_time"))
        return entidad
