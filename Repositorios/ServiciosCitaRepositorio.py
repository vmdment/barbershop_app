from Entidades import ServiciosCita
from Utilidades import Conexion


class ServiciosCitaRepositorio:

    def Consultar(self, appointment_id: int) -> list:
        filas: list = Conexion.conexion.call("proc_select_appointment_details", (appointment_id,))
        return [self.__Construir(fila) for fila in filas]

    def BuscarPorId(self, id: int) -> ServiciosCita.ServiciosCita | None:
        filas: list = Conexion.conexion.call("proc_select_appointment_detail_by_id", (id,))
        if not filas:
            return None
        return self.__Construir(filas[0])

    def Insertar(self, entidad: ServiciosCita.ServiciosCita) -> ServiciosCita.ServiciosCita:
        filas: list = Conexion.conexion.call(
            "proc_insert_appointment_detail",
            (
                entidad.GetAppointmentId(),
                entidad.GetServiceId(),
                entidad.GetAppliedPrice(),
                entidad.GetAppliedDurationMinutes(),
            ),
        )
        entidad.SetId(int(filas[0]["id"]))
        return entidad

    def Actualizar(self, entidad: ServiciosCita.ServiciosCita) -> ServiciosCita.ServiciosCita:
        Conexion.conexion.call(
            "proc_update_appointment_detail",
            (
                entidad.GetId(),
                entidad.GetAppliedPrice(),
                entidad.GetAppliedDurationMinutes(),
            ),
        )
        return entidad

    def Eliminar(self, id: int) -> None:
        Conexion.conexion.call("proc_delete_appointment_detail", (id,))

    def __Construir(self, fila: dict) -> ServiciosCita.ServiciosCita:
        entidad: ServiciosCita.ServiciosCita = ServiciosCita.ServiciosCita()
        entidad.SetId(fila.get("id"))
        entidad.SetAppointmentId(fila.get("appointment_id"))
        entidad.SetServiceId(fila.get("service_id"))
        entidad.SetServiceName(fila.get("service_name"))
        entidad.SetAppliedPrice(fila.get("applied_price"))
        entidad.SetAppliedDurationMinutes(fila.get("applied_duration_minutes"))
        return entidad
