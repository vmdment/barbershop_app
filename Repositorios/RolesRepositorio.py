from Entidades import Roles
from Utilidades import Conexion


class RolesRepositorio:

    def Consultar(self) -> list:
        filas: list = Conexion.conexion.call("proc_select_roles")
        return [self.__Construir(fila) for fila in filas]

    def BuscarPorId(self, id: int) -> Roles.Roles | None:
        filas: list = Conexion.conexion.call("proc_select_role_by_id", (id,))
        if not filas:
            return None
        return self.__Construir(filas[0])

    def Insertar(self, entidad: Roles.Roles) -> Roles.Roles:
        filas: list = Conexion.conexion.call("proc_insert_role", (entidad.GetName(),))
        entidad.SetId(int(filas[0]["id"]))
        return entidad

    def Actualizar(self, entidad: Roles.Roles) -> Roles.Roles:
        Conexion.conexion.call("proc_update_role", (entidad.GetId(), entidad.GetName()))
        return entidad

    def Eliminar(self, id: int) -> None:
        Conexion.conexion.call("proc_delete_role", (id,))

    def __Construir(self, fila: dict) -> Roles.Roles:
        entidad: Roles.Roles = Roles.Roles()
        entidad.SetId(fila.get("id"))
        entidad.SetName(fila.get("name"))
        return entidad
