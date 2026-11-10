# Barbershop - Back (API REST y consola)

Aplicación de consola en Python para administrar una barbería (usuarios, barberos, horarios, citas,
servicios, ventas, inventario y compras) sobre MySQL, usando procedimientos almacenados vía ODBC.

# Configuracion

Requiere Python 3.10 o superior y el driver ODBC de MySQL.

    py -3 --version
    py -m pip install pyodbc flask

1. Ejecute `bd.sql` en MySQL (crea `barbershop_db`, las 15 tablas y los procedimientos almacenados).
2. Copie `.env.example` como `.env` y ajuste el driver ODBC, el usuario y la contraseña.
3. (Opcional) Cargue datos de prueba: `py datos_prueba.py`
4. Inicie la aplicación de consola: `py main.py`
5. O inicie la API REST: `py api.py` (http://localhost:4040/api lista todas las rutas)

La aplicación web es un proyecto aparte (`barbershop_front`, en la carpeta vecina) que consume esta API. Los orígenes desde los que
puede llamarla se configuran con `CORS_ORIGENES` en el `.env` (por defecto http://localhost:5500).

# Estructura (arquitectura en capas)

    main.py              Punto de entrada: abre la conexión y muestra el menú principal
    api.py               Punto de entrada de la API REST (Flask) en el puerto 4040
    menus.py             Define el menú de cada entidad (campos, columnas, opciones extra)
    crud.py              Motor genérico de menús: listar, buscar, registrar, actualizar, eliminar
    datos_prueba.py      Carga datos de ejemplo
    bd.sql               Script de la base de datos (tablas + procedimientos almacenados)
    .env.example         Plantilla de configuración de la base de datos (copiar como .env)

    Entidades/           Una clase por tabla, solo con atributos y Get/Set
    Repositorios/        Acceso a datos: llaman a los procedimientos almacenados (proc_*)
    Aplicaciones/        Reglas de negocio: validan y delegan en el repositorio
    Controladores/       API REST: un Blueprint de Flask por entidad que llama a Aplicaciones
    Utilidades/
        Configuracion.py   Lee el .env y arma la cadena de conexión
        Conexion.py        Conexión ODBC compartida (openConnection / call / closeConnection)
        Errores.py         ErrorBD (error de base de datos) y ErrorValidacion (regla de negocio)
        Validaciones.py    Lectura de datos por consola con validación
        EntidadBase.py     Convierte una entidad a diccionario y viceversa (para la consola)

## Entidades

Cada una de las 15 tablas tiene un archivo con el mismo nombre en cada capa:

| Entidad (`Entidades/`) | Repositorio (`Repositorios/`)   | Aplicación (`Aplicaciones/`)    |
|------------------------|---------------------------------|---------------------------------|
| `Roles`                | `RolesRepositorio`              | `RolesAplicacion`               |
| `Usuarios`             | `UsuariosRepositorio`           | `UsuariosAplicacion`            |
| `Barberias`            | `BarberiasRepositorio`          | `BarberiasAplicacion`           |
| `Barberos`             | `BarberosRepositorio`           | `BarberosAplicacion`            |
| `Horarios`             | `HorariosRepositorio`           | `HorariosAplicacion`            |
| `Bloqueos`             | `BloqueosRepositorio`           | `BloqueosAplicacion`            |
| `Servicios`            | `ServiciosRepositorio`          | `ServiciosAplicacion`           |
| `ServiciosBarbero`     | `ServiciosBarberoRepositorio`   | `ServiciosBarberoAplicacion`    |
| `Citas`                | `CitasRepositorio`              | `CitasAplicacion`               |
| `ServiciosCita`        | `ServiciosCitaRepositorio`      | `ServiciosCitaAplicacion`       |
| `Productos`            | `ProductosRepositorio`          | `ProductosAplicacion`           |
| `Ventas`               | `VentasRepositorio`             | `VentasAplicacion`              |
| `DetalleVentas`        | `DetalleVentasRepositorio`      | `DetalleVentasAplicacion`       |
| `Proveedores`          | `ProveedoresRepositorio`        | `ProveedoresAplicacion`         |
| `Compras`              | `ComprasRepositorio`            | `ComprasAplicacion`             |

Los repositorios y las aplicaciones exponen los mismos métodos:
`Consultar()`, `BuscarPorId(id)`, `Insertar(entidad)`, `Actualizar(entidad)` y `Eliminar(id)`.
La aplicación agrega `Validar(entidad)`, que se ejecuta antes de insertar o actualizar.

## Flujo de una operación

    menus.py / crud.py  →  Aplicaciones  →  Repositorios  →  procedimiento almacenado (bd.sql)

Las reglas de negocio se validan en la Aplicación (lanza `ErrorValidacion`); los errores de la base
de datos llegan como `ErrorBD` con un mensaje legible.

## Agregar una entidad nueva

1. Cree los procedimientos almacenados en `bd.sql` (`proc_select_*`, `proc_insert_*`, ...).
2. `Entidades/Nueva.py`: clase que hereda de `EntidadBase`, con su lista `Campos` y sus Get/Set.
3. `Repositorios/NuevaRepositorio.py`: llama a los procedimientos y construye la entidad.
4. `Aplicaciones/NuevaAplicacion.py`: valida y delega en el repositorio.
5. `menus.py`: defina su `Entidad(...)` (columnas y campos) y agréguela a `MENU_PRINCIPAL`.

# API REST (Controladores)

Documentación interactiva (Swagger UI): http://localhost:4040/api/docs — la especificación OpenAPI
se genera sola desde los controladores en http://localhost:4040/api/openapi.json.

`Controladores/ControladorBase.py` registra para cada entidad las rutas CRUD:

| Método   | Ruta                   | Llama a                           |
|----------|------------------------|-----------------------------------|
| `GET`    | `/api/<entidad>`       | `Consultar()`                     |
| `GET`    | `/api/<entidad>/<id>`  | `BuscarPorId(id)`                 |
| `POST`   | `/api/<entidad>`       | `Insertar(entidad)` (cuerpo JSON) |
| `PUT`    | `/api/<entidad>/<id>`  | `Actualizar(entidad)` (parcial)   |
| `DELETE` | `/api/<entidad>/<id>`  | `Eliminar(id)`                    |

Entidades: `roles`, `usuarios`, `barberias`, `barberos`, `horarios`, `bloqueos`, `servicios`,
`servicios-barbero`, `citas`, `servicios-cita`, `productos`, `ventas`, `detalle-ventas`,
`proveedores`, `compras`.

- Listados que dependen de otro registro exigen un parámetro: `horarios`, `bloqueos` y
  `servicios-barbero` → `?barber_id=1`; `servicios-cita` → `?appointment_id=1`;
  `detalle-ventas` → `?product_sale_id=1`.
- Rutas extra: `GET /api/citas/cliente/<id>`, `GET /api/citas/barbero/<id>`,
  `PATCH /api/citas/<id>/estado` (`{"status": "Confirmed"}`), `GET /api/productos/disponibles`,
  `GET /api/productos/stock-bajo`.
- Usuarios: se envía `password` (mín. 6 caracteres) y se guarda su hash; `password_hash` nunca se devuelve.
- Formatos: fechas `AAAA-MM-DD`, horas `HH:MM`, fecha y hora `AAAA-MM-DD HH:MM`.
- Respuestas: `{"Respuesta": ...}` o `{"Error": "..."}` con código 400 (datos inválidos),
  404 (no existe), 409 (error de base de datos) o 500.

Ejemplo:

    curl -X POST http://localhost:4040/api/roles -H "Content-Type: application/json" -d "{\"name\": \"Gerente\"}"

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
