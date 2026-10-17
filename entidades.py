"""Definición de las 15 entidades del sistema y sus opciones de menú."""
from datetime import datetime

import validaciones as v
from conexion import ErrorBD, conexion
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
# Listas para elegir registros relacionados (claves foráneas)
# ------------------------------------------------------------------

R_ROLES = Referencia("proc_select_roles", "name", "roles")
R_USUARIOS = Referencia("proc_select_users", lambda r: f"{r['full_name']} ({r['role_name']})", "usuarios")
R_BARBERIAS = Referencia("proc_select_barbershops", lambda r: f"{r['name']} - {r['city']}", "barberías")
R_BARBEROS = Referencia("proc_select_barbers",
                        lambda r: r["barber_name"] + ("" if r["is_active"] else " (inactivo)"), "barberos")
R_BARBEROS_ACTIVOS = Referencia("proc_select_barbers", "barber_name", "barberos activos",
                                filtrar=lambda r: bool(r["is_active"]))
R_SERVICIOS = Referencia("proc_select_services",
                         lambda r: f"{r['name']} - ${fmt(r['base_price'])} / {r['duration_minutes']} min",
                         "servicios")
R_CITAS = Referencia("proc_select_appointments",
                     lambda r: f"{r['appointment_date']} {fmt(r['start_time'])} - {r['customer_name']} "
                               f"con {r['barber_name']} ({ESTADOS[r['status']]})", "citas")
R_CITAS_ABIERTAS = Referencia(R_CITAS.proc, R_CITAS.texto, "citas pendientes o confirmadas",
                              filtrar=lambda r: r["status"] in TRANSICIONES)
R_PRODUCTOS_CON_STOCK = Referencia("proc_select_products",
                                   lambda r: f"{r['name']} - ${fmt(r['selling_price'])} (stock: {r['stock_quantity']})",
                                   "productos con stock")
R_VENTAS = Referencia("proc_select_product_sales",
                      lambda r: f"{fmt(r['sale_datetime'])} - {r['customer_name'] or 'Sin cliente'} "
                                f"- ${fmt(r['total_amount'])}", "ventas")
R_PROVEEDORES = Referencia("proc_select_suppliers", "company_name", "proveedores")


def _barbero_de_la_cita(valores: dict) -> tuple:
    cita = conexion.call("proc_select_appointment_by_id", (valores["appointment_id"],))
    if not cita:
        raise v.Cancelado("La cita indicada no existe.")
    return (cita[0]["barber_id"],)


R_SERVICIOS_DE_LA_CITA = Referencia(
    "proc_select_barber_services",
    lambda r: f"{r['service_name']} - ${fmt(r['final_price'])} / {r['final_duration']} min",
    "servicios asignados al barbero de la cita (vea 'Servicios por barbero')",
    id_col="service_id", params=_barbero_de_la_cita)

# ------------------------------------------------------------------
# Validaciones entre campos (se revisan antes de llamar a la BD)
# ------------------------------------------------------------------


def validar_barbero(d):
    if not d["provides_home_service"] and not d["provides_shop_service"]:
        return "El barbero debe atender en barbería, a domicilio o ambos."
    if d["provides_shop_service"] and d["barbershop_id"] is None:
        return "Si atiende en barbería debe indicar a qué barbería pertenece."


def validar_horario(d):
    if d["end_time"] <= d["start_time"]:
        return "La hora de salida debe ser posterior a la de entrada."
    if d["lunch_start_time"] is not None:
        if d["lunch_end_time"] is None:
            return "Debe indicar el fin del almuerzo."
        if d["lunch_end_time"] <= d["lunch_start_time"]:
            return "El fin del almuerzo debe ser posterior a su inicio."
        if d["lunch_start_time"] < d["start_time"] or d["lunch_end_time"] > d["end_time"]:
            return "El almuerzo debe estar dentro del horario de trabajo."


def validar_bloqueo(d):
    if d["end_datetime"] <= d["start_datetime"]:
        return "El fin del bloqueo debe ser posterior a su inicio."


def validar_cita(d):
    if d["end_time"] <= d["start_time"]:
        return "La hora de fin debe ser posterior a la hora de inicio."
    if datetime.combine(d["appointment_date"], d["start_time"]) <= datetime.now():
        return "No se pueden agendar citas en el pasado."


def validar_producto(d):
    if d["barbershop_id"] is None and d["barber_id"] is None:
        return "El producto debe pertenecer a una barbería o a un barbero."


def validar_detalle_venta(d):
    if "product_id" not in d:   # al actualizar, el stock lo valida la BD
        return None
    producto = conexion.call("proc_select_product_by_id", (d["product_id"],))
    if producto and d["quantity"] > producto[0]["stock_quantity"]:
        return f"Stock insuficiente: solo hay {producto[0]['stock_quantity']} unidad(es)."


def validar_compra(d):
    if d["barber_id"] is None and d["barbershop_id"] is None:
        return "La compra debe asignarse a un barbero o a una barbería."


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
    proc_listar="proc_select_roles", proc_buscar="proc_select_role_by_id",
    proc_insertar="proc_insert_role", proc_actualizar="proc_update_role", proc_eliminar="proc_delete_role",
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
    proc_listar="proc_select_users", proc_buscar="proc_select_user_by_id",
    proc_insertar="proc_insert_user", proc_actualizar="proc_update_user", proc_eliminar="proc_delete_user",
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
    proc_listar="proc_select_barbershops", proc_buscar="proc_select_barbershop_by_id",
    proc_insertar="proc_insert_barbershop", proc_actualizar="proc_update_barbershop",
    proc_eliminar="proc_delete_barbershop",
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
    validar=validar_barbero,
    proc_listar="proc_select_barbers", proc_buscar="proc_select_barber_by_id",
    proc_insertar="proc_insert_barber", proc_actualizar="proc_update_barber", proc_eliminar="proc_delete_barber",
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
    validar=validar_horario,
    proc_listar="proc_select_barber_schedule", proc_buscar="proc_select_barber_schedule_by_id",
    proc_insertar="proc_insert_barber_schedule", proc_actualizar="proc_update_barber_schedule",
    proc_eliminar="proc_delete_barber_schedule",
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
    validar=validar_bloqueo,
    proc_listar="proc_select_schedule_blocks", proc_buscar="proc_select_schedule_block_by_id",
    proc_insertar="proc_insert_schedule_block", proc_actualizar="proc_update_schedule_block",
    proc_eliminar="proc_delete_schedule_block",
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
    proc_listar="proc_select_services", proc_buscar="proc_select_service_by_id",
    proc_insertar="proc_insert_service", proc_actualizar="proc_update_service",
    proc_eliminar="proc_delete_service",
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
    proc_listar="proc_select_barber_services", proc_buscar="proc_select_barber_service_by_id",
    proc_insertar="proc_insert_barber_service", proc_actualizar="proc_update_barber_service",
    proc_eliminar="proc_delete_barber_service",
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
    proc_listar="proc_select_appointment_details", proc_buscar="proc_select_appointment_detail_by_id",
    proc_insertar="proc_insert_appointment_detail", proc_actualizar="proc_update_appointment_detail",
    proc_eliminar="proc_delete_appointment_detail",
)


def agregar_servicios_a_cita(cita_id: int, _valores=None) -> None:
    while v.confirmar("¿Desea agregar un servicio a la cita?"):
        try:
            registrar(SERVICIOS_CITA, fijos={"appointment_id": cita_id})
        except v.Cancelado as e:
            aviso(str(e))
        except ErrorBD as e:
            error(str(e))
    cita = conexion.call("proc_select_appointment_by_id", (cita_id,))
    if cita:
        aviso(f"Total de la cita: ${fmt(cita[0]['total_amount'])}")


def listar_citas_por_cliente() -> None:
    cliente = pedir_campo(Campo("customer_id", "Cliente", "ref", referencia=R_USUARIOS), {})
    filas = conexion.call("proc_select_appointments_by_customer", (cliente,))
    mostrar_tabla(filas, [c for c in COLUMNAS_CITA if c[0] != "customer_name"])


def listar_citas_por_barbero() -> None:
    barbero = pedir_campo(campo_barbero(), {})
    filas = conexion.call("proc_select_appointments_by_barber", (barbero,))
    mostrar_tabla(filas, [c for c in COLUMNAS_CITA if c[0] != "barber_name"])


def cambiar_estado_cita() -> None:
    cita = elegir_registro(CITAS, "cambiar de estado")
    opciones = TRANSICIONES.get(cita["status"])
    if not opciones:
        raise v.Cancelado(f"La cita está {ESTADOS[cita['status']].lower()}; ya no se puede cambiar su estado.")
    print(f"\n  Estado actual: {ESTADOS[cita['status']]}")
    nuevo = v.pedir_opcion("Nuevo estado", {estado: ESTADOS[estado] for estado in opciones})
    conexion.call("proc_update_appointment_status", (cita["id"], nuevo))
    exito(f"La cita ahora está {ESTADOS[nuevo].lower()}.")


def ver_servicios_de_cita() -> None:
    cita = elegir_registro(CITAS, "consultar")
    mostrar_ficha(cita, COLUMNAS_CITA)
    mostrar_tabla(conexion.call("proc_select_appointment_details", (cita["id"],)), SERVICIOS_CITA.columnas)


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
    parametros=["customer_id", "barber_id", "barbershop_id", "appointment_date", "start_time",
                "end_time", "location_type", "home_address"],
    validar=validar_cita,
    despues_de_insertar=agregar_servicios_a_cita,
    extras=[
        ("Cambiar estado (confirmar / completar / cancelar)", cambiar_estado_cita),
        ("Ver servicios de una cita", ver_servicios_de_cita),
        ("Agregar servicios a una cita", agregar_servicio_a_cita),
        ("Listar citas de un cliente", listar_citas_por_cliente),
        ("Listar citas de un barbero", listar_citas_por_barbero),
    ],
    proc_listar="proc_select_appointments", proc_buscar="proc_select_appointment_by_id",
    proc_insertar="proc_insert_appointment", proc_actualizar="proc_update_appointment",
    proc_eliminar="proc_delete_appointment",
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
    validar=validar_producto,
    extras=[
        ("Listar disponibles (con stock)",
         lambda: mostrar_tabla(conexion.call("proc_select_products"), COLUMNAS_PRODUCTO)),
        ("Listar con stock bajo",
         lambda: mostrar_tabla(conexion.call("proc_select_low_stock_products"), COLUMNAS_PRODUCTO)),
    ],
    proc_listar="proc_select_all_products", proc_buscar="proc_select_product_by_id",
    proc_insertar="proc_insert_product", proc_actualizar="proc_update_product",
    proc_eliminar="proc_delete_product",
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
    validar=validar_detalle_venta,
    proc_listar="proc_select_product_sale_details", proc_buscar="proc_select_product_sale_detail_by_id",
    proc_insertar="proc_insert_product_sale_detail", proc_actualizar="proc_update_product_sale_detail",
    proc_eliminar="proc_delete_product_sale_detail",
)


def agregar_productos_a_venta(venta_id: int, _valores=None) -> None:
    while v.confirmar("¿Desea agregar un producto a la venta?"):
        try:
            registrar(DETALLE_VENTAS, fijos={"product_sale_id": venta_id})
        except v.Cancelado as e:
            aviso(str(e))
        except ErrorBD as e:
            error(str(e))
    venta = conexion.call("proc_select_product_sale_by_id", (venta_id,))
    if venta:
        aviso(f"Total de la venta: ${fmt(venta[0]['total_amount'])}")


def ver_detalle_de_venta() -> None:
    venta = elegir_registro(VENTAS, "consultar")
    mostrar_ficha(venta, VENTAS.columnas)
    mostrar_tabla(conexion.call("proc_select_product_sale_details", (venta["id"],)), DETALLE_VENTAS.columnas)


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
    proc_listar="proc_select_product_sales", proc_buscar="proc_select_product_sale_by_id",
    proc_insertar="proc_insert_product_sale", proc_actualizar="proc_update_product_sale",
    proc_eliminar="proc_delete_product_sale",
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
    proc_listar="proc_select_suppliers", proc_buscar="proc_select_supplier_by_id",
    proc_insertar="proc_insert_supplier", proc_actualizar="proc_update_supplier",
    proc_eliminar="proc_delete_supplier",
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
    validar=validar_compra,
    proc_listar="proc_select_supplier_purchases", proc_buscar="proc_select_supplier_purchase_by_id",
    proc_insertar="proc_insert_supplier_purchase", proc_actualizar="proc_update_supplier_purchase",
    proc_eliminar="proc_delete_supplier_purchase",
)

MENU_PRINCIPAL = [
    ROLES, USUARIOS, BARBERIAS, BARBEROS, HORARIOS, BLOQUEOS, SERVICIOS, SERVICIOS_BARBERO,
    CITAS, SERVICIOS_CITA, PRODUCTOS, VENTAS, DETALLE_VENTAS, PROVEEDORES, COMPRAS,
]
