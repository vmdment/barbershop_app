from Entidades import Accesos
from Utilidades import Conexion


class AccesosRepositorio:

    def Consultar(self, user_id: int | None = None, limite: int = 200) -> list:
        filas: list = Conexion.conexion.call("proc_select_access_log", (user_id, limite))
        return [self.__Construir(fila) for fila in filas]

    def Registrar(self, user_id: int | None, email: str, evento: str, ip: str | None, agente: str | None) -> None:
        Conexion.conexion.call("proc_insert_access_log", (user_id, email, evento, ip, agente))

    def __Construir(self, fila: dict) -> Accesos.Accesos:
        entidad: Accesos.Accesos = Accesos.Accesos()
        entidad.SetId(fila.get("id"))
        entidad.SetUserId(fila.get("user_id"))
        entidad.SetFullName(fila.get("full_name"))
        entidad.SetRoleName(fila.get("role_name"))
        entidad.SetEmail(fila.get("email"))
        entidad.SetEvent(fila.get("event"))
        entidad.SetIpAddress(fila.get("ip_address"))
        entidad.SetUserAgent(fila.get("user_agent"))
        entidad.SetCreatedAt(fila.get("created_at"))
        return entidad
