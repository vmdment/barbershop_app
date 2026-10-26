from Entidades import ServiciosBarbero
from Utilidades import Conexion


class ServiciosBarberoRepositorio:

    def Consultar(self, barber_id: int) -> list:
        filas: list = Conexion.conexion.call("proc_select_barber_services", (barber_id,))
        return [self.__Construir(fila) for fila in filas]

    def BuscarPorId(self, id: int) -> ServiciosBarbero.ServiciosBarbero | None:
        filas: list = Conexion.conexion.call("proc_select_barber_service_by_id", (id,))
        if not filas:
            return None
        return self.__Construir(filas[0])

    def Insertar(self, entidad: ServiciosBarbero.ServiciosBarbero) -> ServiciosBarbero.ServiciosBarbero:
        filas: list = Conexion.conexion.call(
            "proc_insert_barber_service",
            (
                entidad.GetBarberId(),
                entidad.GetServiceId(),
                entidad.GetCustomPrice(),
                entidad.GetCustomDurationMinutes(),
            ),
        )
        entidad.SetId(int(filas[0]["id"]))
        return entidad

    def Actualizar(self, entidad: ServiciosBarbero.ServiciosBarbero) -> ServiciosBarbero.ServiciosBarbero:
        Conexion.conexion.call(
            "proc_update_barber_service",
            (
                entidad.GetId(),
                entidad.GetBarberId(),
                entidad.GetServiceId(),
                entidad.GetCustomPrice(),
                entidad.GetCustomDurationMinutes(),
            ),
        )
        return entidad

    def Eliminar(self, id: int) -> None:
        Conexion.conexion.call("proc_delete_barber_service", (id,))

    def __Construir(self, fila: dict) -> ServiciosBarbero.ServiciosBarbero:
        entidad: ServiciosBarbero.ServiciosBarbero = ServiciosBarbero.ServiciosBarbero()
        entidad.SetId(fila.get("id"))
        entidad.SetBarberId(fila.get("barber_id"))
        entidad.SetServiceId(fila.get("service_id"))
        entidad.SetServiceName(fila.get("service_name"))
        entidad.SetCustomPrice(fila.get("custom_price"))
        entidad.SetCustomDurationMinutes(fila.get("custom_duration_minutes"))
        entidad.SetFinalPrice(fila.get("final_price"))
        entidad.SetFinalDuration(fila.get("final_duration"))
        return entidad
