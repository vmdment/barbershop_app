from Entidades import Barberos
from Utilidades import Conexion


class BarberosRepositorio:

    def Consultar(self) -> list:
        filas: list = Conexion.conexion.call("proc_select_barbers")
        return [self.__Construir(fila) for fila in filas]

    def BuscarPorId(self, id: int) -> Barberos.Barberos | None:
        filas: list = Conexion.conexion.call("proc_select_barber_by_id", (id,))
        if not filas:
            return None
        return self.__Construir(filas[0])

    def Insertar(self, entidad: Barberos.Barberos) -> Barberos.Barberos:
        filas: list = Conexion.conexion.call(
            "proc_insert_barber",
            (
                entidad.GetUserId(),
                entidad.GetBarbershopId(),
                entidad.GetProvidesHomeService(),
                entidad.GetProvidesShopService(),
                entidad.GetCommissionRate(),
            ),
        )
        entidad.SetId(int(filas[0]["id"]))
        return entidad

    def Actualizar(self, entidad: Barberos.Barberos) -> Barberos.Barberos:
        Conexion.conexion.call(
            "proc_update_barber",
            (
                entidad.GetId(),
                entidad.GetUserId(),
                entidad.GetBarbershopId(),
                entidad.GetProvidesHomeService(),
                entidad.GetProvidesShopService(),
                entidad.GetCommissionRate(),
                entidad.GetIsActive(),
            ),
        )
        return entidad

    def Eliminar(self, id: int) -> None:
        Conexion.conexion.call("proc_delete_barber", (id,))

    def __Construir(self, fila: dict) -> Barberos.Barberos:
        entidad: Barberos.Barberos = Barberos.Barberos()
        entidad.SetId(fila.get("id"))
        entidad.SetUserId(fila.get("user_id"))
        entidad.SetBarberName(fila.get("barber_name"))
        entidad.SetBarbershopId(fila.get("barbershop_id"))
        entidad.SetBarbershopName(fila.get("barbershop_name"))
        entidad.SetProvidesHomeService(fila.get("provides_home_service"))
        entidad.SetProvidesShopService(fila.get("provides_shop_service"))
        entidad.SetCommissionRate(fila.get("commission_rate"))
        entidad.SetIsActive(fila.get("is_active"))
        return entidad
