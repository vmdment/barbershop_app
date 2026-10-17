"""Carga datos de prueba coherentes usando los procedimientos almacenados.

Uso: python datos_prueba.py
Requiere haber ejecutado bd.sql. Las citas se generan en fechas futuras
porque los procedimientos no permiten agendar en el pasado.
"""
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from conexion import ErrorBD, conexion
from validaciones import hashear_password

D = Decimal


def call(proc, *params):
    filas = conexion.call(proc, params)
    return filas[0]["id"] if filas and "id" in filas[0] else filas


def dia_habil(dias_adelante: int) -> date:
    """Fecha futura que cae de lunes a sábado (días en que atienden casi todos)."""
    fecha = date.today() + timedelta(days=dias_adelante)
    return fecha + timedelta(days=1) if fecha.weekday() == 6 else fecha


def rol(nombre: str) -> int:
    for fila in conexion.call("proc_select_roles"):
        if fila["name"].lower() == nombre.lower():
            return fila["id"]
    return call("proc_insert_role", nombre)


def cargar():
    print("Cargando datos de prueba...")
    clave = hashear_password("clave123")

    # 1. Roles (reutiliza los que ya existan)
    r_admin, r_barbero, r_cliente, r_asistente = (rol("Administrador"), rol("Barbero"),
                                                   rol("Cliente"), rol("Asistente"))

    # 2. Usuarios
    laura = call("proc_insert_user", r_admin, "Laura Gómez", "laura.gomez@barberia.com", clave, "3104567890")
    andres = call("proc_insert_user", r_admin, "Andrés Ruiz", "andres.ruiz@barberia.com", clave, "3112345678")
    sofia = call("proc_insert_user", r_asistente, "Sofía Vargas", "sofia.vargas@barberia.com", clave, "3127654321")
    u_carlos = call("proc_insert_user", r_barbero, "Carlos Pérez", "carlos.perez@barberia.com", clave, "3001112233")
    u_julian = call("proc_insert_user", r_barbero, "Julián Martínez", "julian.martinez@barberia.com", clave, "3002223344")
    u_santiago = call("proc_insert_user", r_barbero, "Santiago Ramírez", "santiago.ramirez@barberia.com", clave, "3003334455")
    u_felipe = call("proc_insert_user", r_barbero, "Felipe Torres", "felipe.torres@barberia.com", clave, "3004445566")
    maria = call("proc_insert_user", r_cliente, "María López", "maria.lopez@gmail.com", clave, "3151234567")
    juan = call("proc_insert_user", r_cliente, "Juan Herrera", "juan.herrera@gmail.com", clave, "3162345678")
    camila = call("proc_insert_user", r_cliente, "Camila Rodríguez", "camila.rodriguez@hotmail.com", clave, "3173456789")
    diego = call("proc_insert_user", r_cliente, "Diego Castro", "diego.castro@gmail.com", clave, "3184567890")
    valentina = call("proc_insert_user", r_cliente, "Valentina Morales", "valentina.morales@yahoo.com", clave, "3195678901")

    # 3. Barberías
    clasico = call("proc_insert_barbershop", laura, "Barbería El Clásico", "Calle 45 # 13-20", "Bogotá", "6013456789")
    studio = call("proc_insert_barbershop", andres, "Barber Studio 93", "Carrera 15 # 93-40", "Bogotá", "6017654321")

    # 4. Barberos (Felipe solo atiende a domicilio)
    carlos = call("proc_insert_barber", u_carlos, clasico, 1, 1, D("40.00"))
    julian = call("proc_insert_barber", u_julian, clasico, 0, 1, D("35.00"))
    santiago = call("proc_insert_barber", u_santiago, studio, 1, 1, D("45.00"))
    felipe = call("proc_insert_barber", u_felipe, None, 1, 0, D("50.00"))

    # 5. Horarios
    lunes_a_sabado = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    for barbero in (carlos, julian, santiago):
        for dia in lunes_a_sabado:
            call("proc_insert_barber_schedule", barbero, dia, time(9), time(19), time(13), time(14))
    for dia in lunes_a_sabado:
        call("proc_insert_barber_schedule", felipe, dia, time(10), time(18), None, None)

    # 7. Servicios
    corte = call("proc_insert_service", "Corte clásico", "Corte con tijera y máquina", D("25000"), 30, 10)
    fade = call("proc_insert_service", "Degradado (fade)", "Degradado bajo, medio o alto", D("30000"), 40, 10)
    barba = call("proc_insert_service", "Arreglo de barba", "Perfilado y recorte de barba", D("15000"), 20, 5)
    combo = call("proc_insert_service", "Corte + barba", "Combo de corte clásico y arreglo de barba", D("38000"), 50, 10)
    afeitado = call("proc_insert_service", "Afeitado con toalla caliente", None, D("20000"), 30, 10)
    cejas = call("proc_insert_service", "Diseño de cejas", None, D("8000"), 10, 5)
    call("proc_insert_service", "Tinte", "Coloración completa", D("45000"), 60, 15)

    # 8. Servicios por barbero (algunos con precio/duración propios)
    for svc in (corte, fade, barba, combo):
        call("proc_insert_barber_service", carlos, svc, None, None)
    call("proc_insert_barber_service", carlos, afeitado, D("22000"), None)
    for svc in (corte, barba, cejas):
        call("proc_insert_barber_service", julian, svc, None, None)
    call("proc_insert_barber_service", santiago, fade, D("35000"), 45)
    call("proc_insert_barber_service", santiago, combo, D("42000"), None)
    call("proc_insert_barber_service", santiago, cejas, None, None)
    call("proc_insert_barber_service", felipe, corte, D("35000"), None)
    call("proc_insert_barber_service", felipe, afeitado, D("30000"), 40)

    # 6. Bloqueos de agenda
    dia_bloqueo = dia_habil(5)
    call("proc_insert_schedule_block", julian, datetime.combine(dia_bloqueo, time(9)),
         datetime.combine(dia_bloqueo, time(19)), "Vacaciones")
    call("proc_insert_schedule_block", carlos, datetime.combine(dia_habil(3), time(16)),
         datetime.combine(dia_habil(3), time(18)), "Cita médica")

    # 9-10. Citas con sus servicios (el total se calcula solo)
    def cita(cliente, barbero, dias, inicio, fin, lugar="Shop", direccion=None, servicios=(), estados=()):
        id_ = call("proc_insert_appointment", cliente, barbero, None, dia_habil(dias),
                   inicio, fin, lugar, direccion)
        for svc in servicios:
            call("proc_insert_appointment_detail", id_, svc, None, None)
        for estado in estados:
            call("proc_update_appointment_status", id_, estado)
        return id_

    cita(maria, carlos, 1, time(9), time(9, 50), servicios=[combo], estados=["Confirmed"])
    cita(juan, carlos, 1, time(10), time(10, 40), servicios=[fade])
    cita(camila, julian, 2, time(11), time(11, 40), servicios=[corte, cejas], estados=["Confirmed", "Completed"])
    cita(diego, santiago, 2, time(15), time(16), servicios=[fade, cejas], estados=["Confirmed"])
    cita(valentina, santiago, 3, time(9, 30), time(10, 20), servicios=[combo], estados=["Cancelled"])
    cita(juan, felipe, 4, time(10), time(11), "Home", "Calle 127 # 7-15, apto 302",
         servicios=[corte, afeitado])
    cita(maria, julian, 6, time(14), time(14, 30), servicios=[barba])
    cita(diego, carlos, 7, time(17), time(17, 30), "Home", "Carrera 9 # 80-45", servicios=[barba])

    # 11. Productos (el último queda con stock bajo)
    cera = call("proc_insert_product", clasico, None, "Cera mate", "Fijación fuerte, acabado mate", D("28000"), 20, 5)
    pomada = call("proc_insert_product", clasico, None, "Pomada brillante", None, D("32000"), 15, 5)
    aceite = call("proc_insert_product", studio, None, "Aceite para barba", "Aroma sándalo, 30 ml", D("35000"), 12, 4)
    shampoo = call("proc_insert_product", studio, None, "Shampoo anticaspa", None, D("26000"), 10, 3)
    balsamo = call("proc_insert_product", None, felipe, "Bálsamo after shave", None, D("24000"), 8, 2)
    call("proc_insert_product", clasico, None, "Talco mentolado", None, D("12000"), 3, 5)

    # 12-13. Ventas con su detalle (descuentan stock y calculan total)
    venta1 = call("proc_insert_product_sale", maria, sofia, "Card")
    call("proc_insert_product_sale_detail", venta1, cera, 1, None)
    call("proc_insert_product_sale_detail", venta1, shampoo, 1, None)
    venta2 = call("proc_insert_product_sale", None, sofia, "Cash")
    call("proc_insert_product_sale_detail", venta2, pomada, 2, None)
    venta3 = call("proc_insert_product_sale", diego, andres, "Transfer")
    call("proc_insert_product_sale_detail", venta3, aceite, 1, D("32000"))
    call("proc_insert_product_sale_detail", venta3, balsamo, 1, None)

    # 14. Proveedores
    prov1 = call("proc_insert_supplier", "Distribuidora BarberPro S.A.S.", "Ricardo Díaz", "6012223344",
                 "ventas@barberpro.com", "Calle 13 # 68-30, Bogotá")
    prov2 = call("proc_insert_supplier", "Herramientas Wahl Colombia", "Patricia León", "6015556677",
                 "contacto@wahlco.com", None)
    call("proc_insert_supplier", "Cosméticos La Barba", None, "3209876543", None, "Medellín")

    # 15. Compras a proveedores
    call("proc_insert_supplier_purchase", prov1, None, clasico, "20 capas de corte y 5 sillas hidráulicas", D("4850000"))
    call("proc_insert_supplier_purchase", prov2, carlos, None, "Máquina de corte inalámbrica", D("520000"))
    call("proc_insert_supplier_purchase", prov2, santiago, studio, "Patillera y kit de cuchillas", D("310000"))
    call("proc_insert_supplier_purchase", prov1, felipe, None, "Maletín de herramientas para domicilio", D("180000"))

    print("Listo. Contraseña de todos los usuarios de prueba: clave123")


if __name__ == "__main__":
    try:
        conexion.openConnection()
        cargar()
    except ErrorBD as e:
        print(f"[ERROR] {e}")
    finally:
        conexion.closeConnection()
