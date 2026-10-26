from Entidades import Servicios
from Utilidades import Conexion


class ServiciosRepositorio:

    def Consultar(self) -> list:
        filas: list = Conexion.conexion.call("proc_select_services")
        return [self.__Construir(fila) for fila in filas]

    def BuscarPorId(self, id: int) -> Servicios.Servicios | None:
        filas: list = Conexion.conexion.call("proc_select_service_by_id", (id,))
        if not filas:
            return None
        return self.__Construir(filas[0])

    def Insertar(self, entidad: Servicios.Servicios) -> Servicios.Servicios:
        filas: list = Conexion.conexion.call(
            "proc_insert_service",
            (
                entidad.GetName(),
                entidad.GetDescription(),
                entidad.GetBasePrice(),
                entidad.GetDurationMinutes(),
                entidad.GetBufferMinutes(),
            ),
        )
        entidad.SetId(int(filas[0]["id"]))
        return entidad

    def Actualizar(self, entidad: Servicios.Servicios) -> Servicios.Servicios:
        Conexion.conexion.call(
            "proc_update_service",
            (
                entidad.GetId(),
                entidad.GetName(),
                entidad.GetDescription(),
                entidad.GetBasePrice(),
                entidad.GetDurationMinutes(),
                entidad.GetBufferMinutes(),
            ),
        )
        return entidad

    def Eliminar(self, id: int) -> None:
        Conexion.conexion.call("proc_delete_service", (id,))

    def __Construir(self, fila: dict) -> Servicios.Servicios:
        entidad: Servicios.Servicios = Servicios.Servicios()
        entidad.SetId(fila.get("id"))
        entidad.SetName(fila.get("name"))
        entidad.SetDescription(fila.get("description"))
        entidad.SetBasePrice(fila.get("base_price"))
        entidad.SetDurationMinutes(fila.get("duration_minutes"))
        entidad.SetBufferMinutes(fila.get("buffer_minutes"))
        return entidad
