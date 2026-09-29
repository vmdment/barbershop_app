from conexion import conexion
def main():
    conexion.openConnection()
    conexion.execute("Call proc_insert_role('Administrador');")
    conexion.execute("Call proc_insert_role('Asistente');")
    for row in conexion.execute("Call proc_select_roles",isQuery=True):
        print(row)
    conexion.closeConnection()
main()