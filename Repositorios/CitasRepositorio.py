from Entidades import Citas
from Utilidades import Conexion


class CitasRepositorio:

    def Consultar(self) -> list:
        filas: list = Conexion.conexion.call("proc_select_appointments")
        return [self.__Construir(fila) for fila in filas]

    def ConsultarPorCliente(self, customer_id: int) -> list:
        filas: list = Conexion.conexion.call("proc_select_appointments_by_customer", (customer_id,))
        return [self.__Construir(fila) for fila in filas]

    def ConsultarPorBarbero(self, barber_id: int) -> list:
        filas: list = Conexion.conexion.call("proc_select_appointments_by_barber", (barber_id,))
        return [self.__Construir(fila) for fila in filas]

    def BuscarPorId(self, id: int) -> Citas.Citas | None:
        filas: list = Conexion.conexion.call("proc_select_appointment_by_id", (id,))
        if not filas:
            return None
        return self.__Construir(filas[0])

    def Insertar(self, entidad: Citas.Citas) -> Citas.Citas:
        filas: list = Conexion.conexion.call(
            "proc_insert_appointment",
            (
                entidad.GetCustomerId(),
                entidad.GetBarberId(),
                entidad.GetBarbershopId(),
                entidad.GetAppointmentDate(),
                entidad.GetStartTime(),
                entidad.GetEndTime(),
                entidad.GetLocationType(),
                entidad.GetHomeAddress(),
            ),
        )
        entidad.SetId(int(filas[0]["id"]))
        return entidad

    def Actualizar(self, entidad: Citas.Citas) -> Citas.Citas:
        Conexion.conexion.call(
            "proc_update_appointment",
            (
                entidad.GetId(),
                entidad.GetCustomerId(),
                entidad.GetBarberId(),
                entidad.GetBarbershopId(),
                entidad.GetAppointmentDate(),
                entidad.GetStartTime(),
                entidad.GetEndTime(),
                entidad.GetLocationType(),
                entidad.GetHomeAddress(),
            ),
        )
        return entidad

    def Eliminar(self, id: int) -> None:
        Conexion.conexion.call("proc_delete_appointment", (id,))

    def CambiarEstado(self, id: int, estado: str) -> None:
        Conexion.conexion.call("proc_update_appointment_status", (id, estado))

    def __Construir(self, fila: dict) -> Citas.Citas:
        entidad: Citas.Citas = Citas.Citas()
        entidad.SetId(fila.get("id"))
        entidad.SetCustomerId(fila.get("customer_id"))
        entidad.SetCustomerName(fila.get("customer_name"))
        entidad.SetBarberId(fila.get("barber_id"))
        entidad.SetBarberName(fila.get("barber_name"))
        entidad.SetBarbershopId(fila.get("barbershop_id"))
        entidad.SetAppointmentDate(fila.get("appointment_date"))
        entidad.SetStartTime(fila.get("start_time"))
        entidad.SetEndTime(fila.get("end_time"))
        entidad.SetLocationType(fila.get("location_type"))
        entidad.SetHomeAddress(fila.get("home_address"))
        entidad.SetStatus(fila.get("status"))
        entidad.SetTotalAmount(fila.get("total_amount"))
        return entidad
