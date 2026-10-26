from Utilidades import Conexion
from Utilidades.Errores import ErrorBD
from crud import elegir_opcion, error, menu_entidad, titulo
from menus import MENU_PRINCIPAL


def main():
    try:
        Conexion.conexion.openConnection()
    except ErrorBD as e:
        error(str(e))
        return
    try:
        while True:
            titulo("Barbería - Menú principal")
            opcion = elegir_opcion([entidad.titulo for entidad in MENU_PRINCIPAL], "Salir")
            if opcion == 0:
                break
            menu_entidad(MENU_PRINCIPAL[opcion - 1])
    except (KeyboardInterrupt, EOFError):
        print()
    finally:
        Conexion.conexion.closeConnection()
    print("\n  Hasta luego.\n")


if __name__ == "__main__":
    main()
