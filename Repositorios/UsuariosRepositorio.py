from Entidades import Usuarios
from Utilidades import Conexion


class UsuariosRepositorio:

    def Consultar(self) -> list:
        filas: list = Conexion.conexion.call("proc_select_users")
        return [self.__Construir(fila) for fila in filas]

    def BuscarPorId(self, id: int) -> Usuarios.Usuarios | None:
        filas: list = Conexion.conexion.call("proc_select_user_by_id", (id,))
        if not filas:
            return None
        return self.__Construir(filas[0])

    def Insertar(self, entidad: Usuarios.Usuarios) -> Usuarios.Usuarios:
        filas: list = Conexion.conexion.call(
            "proc_insert_user",
            (
                entidad.GetRoleId(),
                entidad.GetFullName(),
                entidad.GetEmail(),
                entidad.GetPasswordHash(),
                entidad.GetPhone(),
            ),
        )
        entidad.SetId(int(filas[0]["id"]))
        return entidad

    def Actualizar(self, entidad: Usuarios.Usuarios) -> Usuarios.Usuarios:
        Conexion.conexion.call(
            "proc_update_user",
            (
                entidad.GetId(),
                entidad.GetRoleId(),
                entidad.GetFullName(),
                entidad.GetEmail(),
                entidad.GetPasswordHash(),
                entidad.GetPhone(),
            ),
        )
        return entidad

    def Eliminar(self, id: int) -> None:
        Conexion.conexion.call("proc_delete_user", (id,))

    def __Construir(self, fila: dict) -> Usuarios.Usuarios:
        entidad: Usuarios.Usuarios = Usuarios.Usuarios()
        entidad.SetId(fila.get("id"))
        entidad.SetRoleId(fila.get("role_id"))
        entidad.SetRoleName(fila.get("role_name"))
        entidad.SetFullName(fila.get("full_name"))
        entidad.SetEmail(fila.get("email"))
        entidad.SetPasswordHash(fila.get("password_hash"))
        entidad.SetPhone(fila.get("phone"))
        entidad.SetCreatedAt(fila.get("created_at"))
        return entidad
