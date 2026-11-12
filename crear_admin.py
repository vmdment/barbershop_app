"""Crea el primer usuario Administrador para poder iniciar sesión en la API.

Uso: py crear_admin.py
La cuenta de cliente se crea sola desde la API (POST /api/auth/registro); los administradores y los
barberos los crea un administrador (POST /api/usuarios y POST /api/barberos).
"""
from Utilidades import Conexion, Validaciones
from Utilidades.Errores import ErrorBD

conexion = Conexion.conexion


def main():
    try:
        conexion.openConnection()
    except ErrorBD as e:
        print(f"[!] {e}")
        return
    try:
        rol = next((f["id"] for f in conexion.call("proc_select_roles") if f["name"].lower() == "administrador"),
                   None)
        if rol is None:
            rol = conexion.call("proc_insert_role", ("Administrador",))[0]["id"]
        print("Nuevo administrador (escriba 'cancelar' para salir)")
        nombre = Validaciones.pedir_texto("Nombre completo", largo=100)
        email = Validaciones.pedir_email("Correo")
        telefono = Validaciones.pedir_telefono("Teléfono")
        clave = Validaciones.pedir_password()
        id_ = conexion.call("proc_insert_user", (rol, nombre, email, clave, telefono))[0]["id"]
        print(f"Administrador creado con ID {id_}. Inicie sesión con {email}.")
    except Validaciones.Cancelado as e:
        print(e)
    except ErrorBD as e:
        print(f"[!] {e}")
    finally:
        conexion.closeConnection()


if __name__ == "__main__":
    main()
