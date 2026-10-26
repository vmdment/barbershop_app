# Configuracion
    py -3 --version
    py -m pip install pyodbc

1. Ejecute `bd.sql` en MySQL (crea `barbershop_db`, las 15 tablas y los procedimientos almacenados).
2. Copie `.env.example` como `.env` y ajuste el driver ODBC, el usuario y la contraseña.
3. (Opcional) Cargue datos de prueba: `py datos_prueba.py`
4. Inicie la aplicación: `py main.py`

# Estructura (arquitectura en capas)

    main.py              Punto de entrada: abre la conexión y muestra el menú principal
    menus.py             Define el menú de cada entidad (campos, columnas, opciones extra)
    crud.py              Motor genérico de menús: listar, buscar, registrar, actualizar, eliminar
    datos_prueba.py      Carga datos de ejemplo
    bd.sql               Script de la base de datos (tablas + procedimientos almacenados)

    Entidades/           Una clase por tabla, solo con atributos y Get/Set
    Repositorios/        Acceso a datos: llaman a los procedimientos almacenados (proc_*)
    Aplicaciones/        Reglas de negocio: validan y delegan en el repositorio
    Utilidades/
        Configuracion.py   Lee el .env y arma la cadena de conexión
        Conexion.py        Conexión ODBC compartida (openConnection / call / closeConnection)
        Errores.py         ErrorBD (error de base de datos) y ErrorValidacion (regla de negocio)
        Validaciones.py    Lectura de datos por consola con validación
        EntidadBase.py     Convierte una entidad a diccionario y viceversa (para la consola)

Flujo de una operación: `menus.py / crud.py` → `Aplicaciones` → `Repositorios` → procedimiento almacenado.
Las reglas de negocio se validan en la Aplicación (lanza `ErrorValidacion`); los errores de la base
de datos llegan como `ErrorBD` con un mensaje legible.

# Usar las capas directamente (sin menú)

    from Aplicaciones import RolesAplicacion
    from Entidades import Roles
    from Utilidades import Conexion

    Conexion.conexion.openConnection()
    aplicacion = RolesAplicacion.RolesAplicacion()

    nuevo = Roles.Roles()
    nuevo.SetName("Gerente")
    nuevo = aplicacion.Insertar(nuevo)          # devuelve la entidad con su Id
    print("Insertado con Id:", nuevo.GetId())

    for rol in aplicacion.Consultar():
        print(rol.GetId(), rol.GetName())

    Conexion.conexion.closeConnection()
