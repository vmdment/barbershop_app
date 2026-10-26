"""Definición de las 15 entidades del sistema y sus opciones de menú.

Cada entidad del menú se apoya en su clase de Entidades y en su objeto de Aplicaciones;
las reglas de negocio (validaciones entre campos) viven en la capa de Aplicaciones."""
from Aplicaciones import (BarberiasAplicacion, BarberosAplicacion, BloqueosAplicacion, CitasAplicacion,
                          ComprasAplicacion, DetalleVentasAplicacion, HorariosAplicacion,
                          ProductosAplicacion, ProveedoresAplicacion, RolesAplicacion,
                          ServiciosAplicacion, ServiciosBarberoAplicacion, ServiciosCitaAplicacion,
                          UsuariosAplicacion, VentasAplicacion)
from Entidades import (Barberias, Barberos, Bloqueos, Citas, Compras, DetalleVentas, Horarios, Productos,
                       Proveedores, Roles, Servicios, ServiciosBarbero, ServiciosCita, Usuarios, Ventas)
from Utilidades import Validaciones as v
from Utilidades.Errores import ErrorBD, ErrorValidacion
from crud import (Campo, Entidad, Referencia, aviso, elegir_registro, error, exito, mostrar_ficha,
                  mostrar_tabla, pedir_campo, registrar, si_no)

# ------------------------------------------------------------------
# Traducción de valores ENUM de la base de datos
# ------------------------------------------------------------------

DIAS = {"Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles", "Thursday": "Jueves",
        "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"}
ESTADOS = {"Pending": "Pendiente", "Confirmed": "Confirmada", "Completed": "Completada",
           "Cancelled": "Cancelada"}
UBICACIONES = {"Shop": "En barbería", "Home": "A domicilio"}
PAGOS = {"Cash": "Efectivo", "Card": "Tarjeta", "Transfer": "Transferencia"}

# Cambios de estado permitidos (los mismos que valida proc_update_appointment_status)
TRANSICIONES = {"Pending": ["Confirmed", "Cancelled"], "Confirmed": ["Completed", "Cancelled"]}

PRECIO_MAX = 99999999.99
fmt = v.formatear

# ------------------------------------------------------------------
# Objetos de la capa de Aplicaciones (uno por entidad)
# ------------------------------------------------------------------

ROLES_APP = RolesAplicacion.RolesAplicacion()
USUARIOS_APP = UsuariosAplicacion.UsuariosAplicacion()
BARBERIAS_APP = BarberiasAplicacion.BarberiasAplicacion()
BARBEROS_APP = BarberosAplicacion.BarberosAplicacion()
HORARIOS_APP = HorariosAplicacion.HorariosAplicacion()
BLOQUEOS_APP = BloqueosAplicacion.BloqueosAplicacion()
SERVICIOS_APP = ServiciosAplicacion.ServiciosAplicacion()
SERVICIOS_BARBERO_APP = ServiciosBarberoAplicacion.ServiciosBarberoAplicacion()
CITAS_APP = CitasAplicacion.CitasAplicacion()
SERVICIOS_CITA_APP = ServiciosCitaAplicacion.ServiciosCitaAplicacion()
PRODUCTOS_APP = ProductosAplicacion.ProductosAplicacion()
VENTAS_APP = VentasAplicacion.VentasAplicacion()
DETALLE_VENTAS_APP = DetalleVentasAplicacion.DetalleVentasAplicacion()
PROVEEDORES_APP = ProveedoresAplicacion.ProveedoresAplicacion()
COMPRAS_APP = ComprasAplicacion.ComprasAplicacion()


def filas(entidades: list) -> list[dict]:
    """Convierte una lista de entidades en filas (diccionarios) para mostrarlas en tabla."""
    return [entidad.ADiccionario() for entidad in entidades]


# ------------------------------------------------------------------
# Listas para elegir registros relacionados (claves foráneas)
# ------------------------------------------------------------------

R_ROLES = Referencia(lambda _: ROLES_APP.Consultar(), "name", "roles")
R_USUARIOS = Referencia(lambda _: USUARIOS_APP.Consultar(),
                        lambda r: f"{r['full_name']} ({r['role_name']})", "usuarios")
R_BARBERIAS = Referencia(lambda _: BARBERIAS_APP.Consultar(),
                         lambda r: f"{r['name']} - {r['city']}", "barberías")
R_BARBEROS = Referencia(lambda _: BARBEROS_APP.Consultar(),
                        lambda r: r["barber_name"] + ("" if r["is_active"] else " (inactivo)"), "barberos")
R_BARBEROS_ACTIVOS = Referencia(R_BARBEROS.origen, "barber_name", "barberos activos",
                                filtrar=lambda r: bool(r["is_active"]))
R_SERVICIOS = Referencia(lambda _: SERVICIOS_APP.Consultar(),
                         lambda r: f"{r['name']} - ${fmt(r['base_price'])} / {r['duration_minutes']} min",
                         "servicios")
R_CITAS = Referencia(lambda _: CITAS_APP.Consultar(),
                     lambda r: f"{r['appointment_date']} {fmt(r['start_time'])} - {r['customer_name']} "
                               f"con {r['barber_name']} ({ESTADOS[r['status']]})", "citas")
R_CITAS_ABIERTAS = Referencia(R_CITAS.origen, R_CITAS.texto, "citas pendientes o confirmadas",
                              filtrar=lambda r: r["status"] in TRANSICIONES)
R_PRODUCTOS_CON_STOCK = Referencia(lambda _: PRODUCTOS_APP.ConsultarDisponibles(),
                                   lambda r: f"{r['name']} - ${fmt(r['selling_price'])} (stock: {r['stock_quantity']})",
                                   "productos con stock")
R_VENTAS = Referencia(lambda _: VENTAS_APP.Consultar(),
                      lambda r: f"{fmt(r['sale_datetime'])} - {r['customer_name'] or 'Sin cliente'} "
                                f"- ${fmt(r['total_amount'])}", "ventas")
R_PROVEEDORES = Referencia(lambda _: PROVEEDORES_APP.Consultar(), "company_name", "proveedores")


def _barbero_de_la_cita(valores: dict) -> int:
    cita = CITAS_APP.BuscarPorId(valores["appointment_id"])
    if not cita:
        raise v.Cancelado("La cita indicada no existe.")
    return cita.GetBarberId()


R_SERVICIOS_DE_LA_CITA = Referencia(
    lambda valores: SERVICIOS_BARBERO_APP.Consultar(_barbero_de_la_cita(valores)),
    lambda r: f"{r['service_name']} - ${fmt(r['final_price'])} / {r['final_duration']} min",
    "servicios asignados al barbero de la cita (vea 'Servicios por barbero')",
    id_col="service_id")

# ------------------------------------------------------------------
# Campos reutilizados
# ------------------------------------------------------------------

def campo_barbero(etiqueta="Barbero", obligatorio=True, referencia=R_BARBEROS):
    return Campo("barber_id", etiqueta, "ref", obligatorio, referencia=referencia)


def campo_barberia(etiqueta="Barbería", obligatorio=True, **extra):
    return Campo("barbershop_id", etiqueta, "ref", obligatorio, referencia=R_BARBERIAS, **extra)


COLUMNAS_PRODUCTO = [("id", "ID"), ("name", "Producto"), ("selling_price", "Precio"),
                     ("stock_quantity", "Stock"), ("min_stock_level", "Mínimo"),
                     ("barbershop_name", "Barbería"), ("barber_name", "Barbero"),
                     ("description", "Descripción")]
COLUMNAS_CITA = [("id", "ID"), ("customer_name", "Cliente"), ("barber_name", "Barbero"),
                 ("appointment_date", "Fecha"), ("start_time", "Inicio"), ("end_time", "Fin"),
                 ("location_type", "Lugar", UBICACIONES.get), ("home_address", "Dirección"),
                 ("status", "Estado", ESTADOS.get), ("total_amount", "Total")]

# ------------------------------------------------------------------
# Entidades
# ------------------------------------------------------------------

ROLES = Entidad(
    titulo="Roles", singular="rol",
    columnas=[("id", "ID"), ("name", "Nombre")],
    campos=[Campo("name", "Nombre del rol", largo=50)],
    clase=Roles.Roles, aplicacion=ROLES_APP,
)

USUARIOS = Entidad(
    titulo="Usuarios", singular="usuario",
    columnas=[("id", "ID"), ("full_name", "Nombre"), ("email", "Correo"), ("phone", "Teléfono"),
              ("role_name", "Rol"), ("created_at", "Creado")],
    campos=[
        Campo("role_id", "Rol", "ref", referencia=R_ROLES),
        Campo("full_name", "Nombre completo", largo=100),
        Campo("email", "Correo electrónico", "email"),
        Campo("password_hash", "Contraseña", "password"),
        Campo("phone", "Teléfono", "telefono"),
    ],
    clase=Usuarios.Usuarios, aplicacion=USUARIOS_APP,
)

BARBERIAS = Entidad(
    titulo="Barberías", singular="barbería", femenino=True,
    columnas=[("id", "ID"), ("name", "Nombre"), ("address", "Dirección"), ("city", "Ciudad"),
              ("phone", "Teléfono"), ("manager_name", "Administrador")],
    campos=[
        Campo("manager_id", "Administrador", "ref", referencia=R_USUARIOS),
        Campo("name", "Nombre", largo=100),
        Campo("address", "Dirección", largo=150),
        Campo("city", "Ciudad", largo=50),
        Campo("phone", "Teléfono", "telefono"),
    ],
    clase=Barberias.Barberias, aplicacion=BARBERIAS_APP,
)

_CAMPOS_BARBERO = [
    Campo("user_id", "Usuario", "ref", referencia=R_USUARIOS),
    campo_barberia(obligatorio=False, ayuda="Enter si solo atiende a domicilio"),
    Campo("provides_home_service", "¿Atiende a domicilio?", "sino"),
    Campo("provides_shop_service", "¿Atiende en barbería?", "sino"),
    Campo("commission_rate", "Comisión (%)", "decimal", minimo=0, maximo=100),
]
BARBEROS = Entidad(
    titulo="Barberos", singular="barbero",
    columnas=[("id", "ID"), ("barber_name", "Nombre"), ("barbershop_name", "Barbería"),
              ("provides_home_service", "Domicilio", si_no), ("provides_shop_service", "En local", si_no),
              ("commission_rate", "Comisión %"), ("is_active", "Activo", si_no)],
    campos=_CAMPOS_BARBERO,
    campos_actualizar=_CAMPOS_BARBERO + [Campo("is_active", "¿Activo?", "sino")],
    clase=Barberos.Barberos, aplicacion=BARBEROS_APP,
)

HORARIOS = Entidad(
    titulo="Horarios de barberos", singular="horario",
    columnas=[("id", "ID"), ("day_of_week", "Día", DIAS.get), ("start_time", "Entrada"),
              ("end_time", "Salida"), ("lunch_start_time", "Almuerzo desde"), ("lunch_end_time", "Almuerzo hasta")],
    filtro=campo_barbero(),
    campos=[
        campo_barbero(),
        Campo("day_of_week", "Día de la semana", "opcion", opciones=DIAS),
        Campo("start_time", "Hora de entrada", "hora"),
        Campo("end_time", "Hora de salida", "hora"),
        Campo("lunch_start_time", "Inicio del almuerzo", "hora", False, ayuda="Enter si no tiene almuerzo"),
        Campo("lunch_end_time", "Fin del almuerzo", "hora",
              condicion=lambda d: d["lunch_start_time"] is not None),
    ],
    clase=Horarios.Horarios, aplicacion=HORARIOS_APP,
)

BLOQUEOS = Entidad(
    titulo="Bloqueos de agenda", singular="bloqueo",
    columnas=[("id", "ID"), ("start_datetime", "Desde"), ("end_datetime", "Hasta"), ("reason", "Motivo")],
    filtro=campo_barbero(),
    campos=[
        campo_barbero(),
        Campo("start_datetime", "Inicio", "fechahora"),
        Campo("end_datetime", "Fin", "fechahora"),
        Campo("reason", "Motivo", obligatorio=False, largo=255),
    ],
    clase=Bloqueos.Bloqueos, aplicacion=BLOQUEOS_APP,
)

SERVICIOS = Entidad(
    titulo="Servicios", singular="servicio",
    columnas=[("id", "ID"), ("name", "Servicio"), ("base_price", "Precio"),
              ("duration_minutes", "Duración (min)"), ("buffer_minutes", "Preparación (min)"),
              ("description", "Descripción")],
    campos=[
        Campo("name", "Nombre", largo=100),
        Campo("description", "Descripción", obligatorio=False, largo=1000),
        Campo("base_price", "Precio base", "decimal", minimo=0, maximo=PRECIO_MAX),
        Campo("duration_minutes", "Duración (minutos)", "entero", minimo=1, maximo=600),
        Campo("buffer_minutes", "Tiempo de preparación (minutos)", "entero", False, minimo=0, maximo=240,
              ayuda="Enter = 10 minutos"),
    ],
    clase=Servicios.Servicios, aplicacion=SERVICIOS_APP,
)

SERVICIOS_BARBERO = Entidad(
    titulo="Servicios por barbero", singular="asignación", femenino=True,
    columnas=[("id", "ID"), ("service_name", "Servicio"), ("custom_price", "Precio propio"),
              ("custom_duration_minutes", "Duración propia"), ("final_price", "Precio final"),
              ("final_duration", "Duración final")],
    filtro=campo_barbero(),
    campos=[
        campo_barbero(),
        Campo("service_id", "Servicio", "ref", referencia=R_SERVICIOS),
        Campo("custom_price", "Precio personalizado", "decimal", False, minimo=0, maximo=PRECIO_MAX,
              ayuda="Enter = usar el precio base del servicio"),
        Campo("custom_duration_minutes", "Duración personalizada (min)", "entero", False, minimo=1, maximo=600,
              ayuda="Enter = usar la duración del servicio"),
    ],
    clase=ServiciosBarbero.ServiciosBarbero, aplicacion=SERVICIOS_BARBERO_APP,
)

SERVICIOS_CITA = Entidad(
    titulo="Servicios de citas", singular="servicio de la cita",
    columnas=[("id", "ID"), ("service_name", "Servicio"), ("applied_price", "Precio"),
              ("applied_duration_minutes", "Duración (min)")],
    filtro=Campo("appointment_id", "Cita", "ref", referencia=R_CITAS),
    campos=[
        Campo("appointment_id", "Cita", "ref", referencia=R_CITAS_ABIERTAS),
        Campo("service_id", "Servicio", "ref", referencia=R_SERVICIOS_DE_LA_CITA),
        Campo("applied_price", "Precio", "decimal", False, minimo=0, maximo=PRECIO_MAX,
              ayuda="Enter = precio del barbero para ese servicio"),
        Campo("applied_duration_minutes", "Duración (min)", "entero", False, minimo=1, maximo=600,
              ayuda="Enter = duración del barbero para ese servicio"),
    ],
    campos_actualizar=[
        Campo("applied_price", "Precio", "decimal", minimo=0, maximo=PRECIO_MAX),
        Campo("applied_duration_minutes", "Duración (min)", "entero", minimo=1, maximo=600),
    ],
    clase=ServiciosCita.ServiciosCita, aplicacion=SERVICIOS_CITA_APP,
)


def agregar_servicios_a_cita(cita_id: int, _valores=None) -> None:
    while v.confirmar("¿Desea agregar un servicio a la cita?"):
        try:
            registrar(SERVICIOS_CITA, fijos={"appointment_id": cita_id})
        except (v.Cancelado, ErrorValidacion) as e:
            aviso(str(e))
        except ErrorBD as e:
            error(str(e))
    cita = CITAS_APP.BuscarPorId(cita_id)
    if cita:
        aviso(f"Total de la cita: ${fmt(cita.GetTotalAmount())}")


def listar_citas_por_cliente() -> None:
    cliente = pedir_campo(Campo("customer_id", "Cliente", "ref", referencia=R_USUARIOS), {})
    citas = filas(CITAS_APP.ConsultarPorCliente(cliente))
    mostrar_tabla(citas, [c for c in COLUMNAS_CITA if c[0] != "customer_name"])


def listar_citas_por_barbero() -> None:
    barbero = pedir_campo(campo_barbero(), {})
    citas = filas(CITAS_APP.ConsultarPorBarbero(barbero))
    mostrar_tabla(citas, [c for c in COLUMNAS_CITA if c[0] != "barber_name"])


def cambiar_estado_cita() -> None:
    cita = elegir_registro(CITAS, "cambiar de estado")
    opciones = TRANSICIONES.get(cita["status"])
    if not opciones:
        raise v.Cancelado(f"La cita está {ESTADOS[cita['status']].lower()}; ya no se puede cambiar su estado.")
    print(f"\n  Estado actual: {ESTADOS[cita['status']]}")
    nuevo = v.pedir_opcion("Nuevo estado", {estado: ESTADOS[estado] for estado in opciones})
    CITAS_APP.CambiarEstado(cita["id"], nuevo)
    exito(f"La cita ahora está {ESTADOS[nuevo].lower()}.")


def ver_servicios_de_cita() -> None:
    cita = elegir_registro(CITAS, "consultar")
    mostrar_ficha(cita, COLUMNAS_CITA)
    mostrar_tabla(filas(SERVICIOS_CITA_APP.Consultar(cita["id"])), SERVICIOS_CITA.columnas)


def agregar_servicio_a_cita() -> None:
    cita_id = pedir_campo(Campo("appointment_id", "Cita", "ref", referencia=R_CITAS_ABIERTAS), {})
    agregar_servicios_a_cita(cita_id)


CITAS = Entidad(
    titulo="Citas", singular="cita", femenino=True,
    columnas=COLUMNAS_CITA,
    campos=[
        Campo("customer_id", "Cliente", "ref", referencia=R_USUARIOS),
        campo_barbero(referencia=R_BARBEROS_ACTIVOS),
        Campo("location_type", "Lugar de atención", "opcion", opciones=UBICACIONES),
        campo_barberia(obligatorio=False, ayuda="Enter = la barbería del barbero",
                       condicion=lambda d: d["location_type"] == "Shop"),
        Campo("home_address", "Dirección del domicilio", largo=200,
              condicion=lambda d: d["location_type"] == "Home"),
        Campo("appointment_date", "Fecha", "fecha"),
        Campo("start_time", "Hora de inicio", "hora"),
        Campo("end_time", "Hora de fin", "hora"),
    ],
    despues_de_insertar=agregar_servicios_a_cita,
    extras=[
        ("Cambiar estado (confirmar / completar / cancelar)", cambiar_estado_cita),
        ("Ver servicios de una cita", ver_servicios_de_cita),
        ("Agregar servicios a una cita", agregar_servicio_a_cita),
        ("Listar citas de un cliente", listar_citas_por_cliente),
        ("Listar citas de un barbero", listar_citas_por_barbero),
    ],
    clase=Citas.Citas, aplicacion=CITAS_APP,
)

PRODUCTOS = Entidad(
    titulo="Productos", singular="producto",
    columnas=COLUMNAS_PRODUCTO,
    campos=[
        campo_barberia("Barbería dueña", obligatorio=False, ayuda="Enter si pertenece a un barbero"),
        campo_barbero("Barbero dueño", obligatorio=False),
        Campo("name", "Nombre", largo=100),
        Campo("description", "Descripción", obligatorio=False, largo=1000),
        Campo("selling_price", "Precio de venta", "decimal", minimo=0, maximo=PRECIO_MAX),
        Campo("stock_quantity", "Stock", "entero", minimo=0, maximo=1_000_000),
        Campo("min_stock_level", "Stock mínimo", "entero", False, minimo=0, maximo=1_000_000,
              ayuda="Enter = 5"),
    ],
    extras=[
        ("Listar disponibles (con stock)",
         lambda: mostrar_tabla(filas(PRODUCTOS_APP.ConsultarDisponibles()), COLUMNAS_PRODUCTO)),
        ("Listar con stock bajo",
         lambda: mostrar_tabla(filas(PRODUCTOS_APP.ConsultarStockBajo()), COLUMNAS_PRODUCTO)),
    ],
    clase=Productos.Productos, aplicacion=PRODUCTOS_APP,
)

DETALLE_VENTAS = Entidad(
    titulo="Detalle de ventas", singular="detalle",
    columnas=[("id", "ID"), ("product_name", "Producto"), ("quantity", "Cantidad"),
              ("unit_price", "Precio unitario"), ("subtotal", "Subtotal")],
    filtro=Campo("product_sale_id", "Venta", "ref", referencia=R_VENTAS),
    campos=[
        Campo("product_sale_id", "Venta", "ref", referencia=R_VENTAS),
        Campo("product_id", "Producto", "ref", referencia=R_PRODUCTOS_CON_STOCK),
        Campo("quantity", "Cantidad", "entero", minimo=1, maximo=1_000_000),
        Campo("unit_price", "Precio unitario", "decimal", False, minimo=0, maximo=PRECIO_MAX,
              ayuda="Enter = precio de venta del producto"),
    ],
    campos_actualizar=[
        Campo("quantity", "Cantidad", "entero", minimo=1, maximo=1_000_000),
        Campo("unit_price", "Precio unitario", "decimal", minimo=0, maximo=PRECIO_MAX),
    ],
    clase=DetalleVentas.DetalleVentas, aplicacion=DETALLE_VENTAS_APP,
)


def agregar_productos_a_venta(venta_id: int, _valores=None) -> None:
    while v.confirmar("¿Desea agregar un producto a la venta?"):
        try:
            registrar(DETALLE_VENTAS, fijos={"product_sale_id": venta_id})
        except (v.Cancelado, ErrorValidacion) as e:
            aviso(str(e))
        except ErrorBD as e:
            error(str(e))
    venta = VENTAS_APP.BuscarPorId(venta_id)
    if venta:
        aviso(f"Total de la venta: ${fmt(venta.GetTotalAmount())}")


def ver_detalle_de_venta() -> None:
    venta = elegir_registro(VENTAS, "consultar")
    mostrar_ficha(venta, VENTAS.columnas)
    mostrar_tabla(filas(DETALLE_VENTAS_APP.Consultar(venta["id"])), DETALLE_VENTAS.columnas)


def agregar_producto_a_venta() -> None:
    venta_id = pedir_campo(Campo("product_sale_id", "Venta", "ref", referencia=R_VENTAS), {})
    agregar_productos_a_venta(venta_id)


VENTAS = Entidad(
    titulo="Ventas de productos", singular="venta", femenino=True,
    columnas=[("id", "ID"), ("sale_datetime", "Fecha"), ("customer_name", "Cliente"),
              ("seller_name", "Vendedor"), ("payment_method", "Pago", PAGOS.get), ("total_amount", "Total")],
    campos=[
        Campo("customer_id", "Cliente", "ref", False, referencia=R_USUARIOS,
              ayuda="Enter si el cliente no está registrado"),
        Campo("seller_user_id", "Vendedor", "ref", referencia=R_USUARIOS),
        Campo("payment_method", "Método de pago", "opcion", opciones=PAGOS),
    ],
    despues_de_insertar=agregar_productos_a_venta,
    extras=[
        ("Ver detalle de una venta", ver_detalle_de_venta),
        ("Agregar productos a una venta", agregar_producto_a_venta),
    ],
    clase=Ventas.Ventas, aplicacion=VENTAS_APP,
)

PROVEEDORES = Entidad(
    titulo="Proveedores", singular="proveedor",
    columnas=[("id", "ID"), ("company_name", "Empresa"), ("contact_name", "Contacto"),
              ("phone", "Teléfono"), ("email", "Correo"), ("address", "Dirección")],
    campos=[
        Campo("company_name", "Empresa", largo=100),
        Campo("contact_name", "Persona de contacto", obligatorio=False, largo=100),
        Campo("phone", "Teléfono", "telefono"),
        Campo("email", "Correo electrónico", "email", False),
        Campo("address", "Dirección", obligatorio=False, largo=150),
    ],
    clase=Proveedores.Proveedores, aplicacion=PROVEEDORES_APP,
)

COMPRAS = Entidad(
    titulo="Compras a proveedores", singular="compra", femenino=True,
    columnas=[("id", "ID"), ("purchase_datetime", "Fecha"), ("company_name", "Proveedor"),
              ("barber_name", "Barbero"), ("barbershop_name", "Barbería"),
              ("tools_description", "Descripción"), ("total_paid", "Total")],
    campos=[
        Campo("supplier_id", "Proveedor", "ref", referencia=R_PROVEEDORES),
        campo_barbero(obligatorio=False),
        campo_barberia(obligatorio=False),
        Campo("tools_description", "Descripción de lo comprado", largo=1000),
        Campo("total_paid", "Total pagado", "decimal", minimo=0.01, maximo=PRECIO_MAX),
    ],
    clase=Compras.Compras, aplicacion=COMPRAS_APP,
)

MENU_PRINCIPAL = [
    ROLES, USUARIOS, BARBERIAS, BARBEROS, HORARIOS, BLOQUEOS, SERVICIOS, SERVICIOS_BARBERO,
    CITAS, SERVICIOS_CITA, PRODUCTOS, VENTAS, DETALLE_VENTAS, PROVEEDORES, COMPRAS,
]
