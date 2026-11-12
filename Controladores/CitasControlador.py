from Aplicaciones import CitasAplicacion
from Controladores import Permisos
from Controladores.ControladorBase import ControladorBase, ErrorPeticion, LeerJson, Respuesta
from Entidades import Citas
from Controladores.Permisos import ADMIN, BARBERO, CLIENTE, TODOS, Prohibido

# Mismos estados que el ENUM de la tabla appointments
ESTADOS = ("Pending", "Confirmed", "Completed", "Cancelled")

# Estados a los que puede llevar una cita cada rol (sobre sus propias citas)
#   Barbero: aceptar (Confirmed), cancelar (Cancelled) y marcarla como atendida (Completed)
#   Cliente: solo cancelar
ESTADOS_POR_ROL = {
    ADMIN: ESTADOS,
    BARBERO: ("Confirmed", "Cancelled", "Completed"),
    CLIENTE: ("Cancelled",),
}

# Reprogramar = cambiar la fecha y la hora. El barbero no cambia el cliente, el barbero ni el lugar.
CAMPOS_REPROGRAMAR = {"appointment_date", "start_time", "end_time"}


def EsParticipante(sesion: Permisos.Sesion, cita) -> bool:
    """El cliente de la cita o el barbero que la atiende."""
    if sesion.rol == BARBERO:
        return cita.GetBarberId() == sesion.barbero_id
    if sesion.rol == CLIENTE:
        return cita.GetCustomerId() == sesion.usuario_id
    return sesion.EsAdmin()


class CitasControlador(ControladorBase):

    def __init__(self):
        super().__init__("citas", Citas.Citas, CitasAplicacion.CitasAplicacion(), crud=False)
        self.RegistrarRuta("", "consultar", self.Consultar, "GET", "Listar todas", lista=True, roles=(ADMIN,))
        self.RegistrarRuta("/mias", "mias", self.ConsultarMias, "GET",
                           "Citas de la sesión (cliente: las que pidió; barbero: las que atiende; "
                           "admin: todas)", lista=True, roles=TODOS)
        self.RegistrarRuta("/<int:id>", "buscar", self.BuscarPorId, "GET", "Buscar por ID", roles=TODOS)
        self.RegistrarRuta("", "insertar", self.Insertar, "POST",
                           "Solicitar cita (el cliente la pide a su nombre y elige el barbero)",
                           cuerpo="entidad", roles=(ADMIN, CLIENTE))
        self.RegistrarRuta("/<int:id>", "actualizar", self.Actualizar, "PUT",
                           "Actualizar (barbero: solo reprogramar fecha y horas)",
                           cuerpo="entidad", roles=(ADMIN, BARBERO))
        self.RegistrarRuta("/<int:id>", "eliminar", self.Eliminar, "DELETE", "Eliminar", respuesta="texto",
                           roles=(ADMIN,))
        self.RegistrarRuta("/cliente/<int:customer_id>", "por_cliente", self.ConsultarPorCliente, "GET",
                           "Citas de un cliente", lista=True, roles=(ADMIN, CLIENTE))
        self.RegistrarRuta("/barbero/<int:barber_id>", "por_barbero", self.ConsultarPorBarbero, "GET",
                           "Citas de un barbero", lista=True, roles=(ADMIN, BARBERO))
        self.RegistrarRuta("/<int:id>/estado", "cambiar_estado", self.CambiarEstado, "PATCH",
                           "Cambiar el estado (barbero: aceptar, cancelar o completar; cliente: cancelar)",
                           cuerpo={"type": "object", "required": ["status"],
                                   "properties": {"status": {"type": "string", "enum": list(ESTADOS)}}},
                           roles=TODOS)

    # --- Permisos ---

    def PrepararDatos(self, datos: dict, nuevo: bool) -> None:
        sesion = Permisos.SesionActual()
        if nuevo and sesion.rol == CLIENTE:
            datos["customer_id"] = sesion.usuario_id          # el cliente solo pide citas a su nombre
        if not nuevo and sesion.rol == BARBERO:
            otros = sorted(set(datos) - CAMPOS_REPROGRAMAR - {"id"})
            if otros:
                raise Prohibido("El barbero solo puede reprogramar la cita (appointment_date, start_time, "
                                f"end_time); no puede cambiar: {', '.join(otros)}.")

    def Autorizar(self, cita, accion: str) -> None:
        sesion = Permisos.SesionActual()
        if not sesion.EsAdmin() and not EsParticipante(sesion, cita):
            raise Prohibido("Solo puede ver o modificar sus propias citas.")

    # --- Rutas ---

    def ConsultarMias(self):
        sesion = Permisos.SesionActual()
        if sesion.rol == CLIENTE:
            return Respuesta(self.ListaJson(self.aplicacion.ConsultarPorCliente(sesion.usuario_id)))
        if sesion.rol == BARBERO:
            return Respuesta(self.ListaJson(self.aplicacion.ConsultarPorBarbero(sesion.barbero_id)))
        return Respuesta(self.ListaJson(self.aplicacion.Consultar()))

    def ConsultarPorCliente(self, customer_id: int):
        sesion = Permisos.SesionActual()
        if sesion.rol == CLIENTE and customer_id != sesion.usuario_id:
            raise Prohibido("Solo puede consultar sus propias citas.")
        return Respuesta(self.ListaJson(self.aplicacion.ConsultarPorCliente(customer_id)))

    def ConsultarPorBarbero(self, barber_id: int):
        sesion = Permisos.SesionActual()
        if sesion.rol == BARBERO and barber_id != sesion.barbero_id:
            raise Prohibido("Solo puede consultar sus propias citas.")
        return Respuesta(self.ListaJson(self.aplicacion.ConsultarPorBarbero(barber_id)))

    def CambiarEstado(self, id: int):
        """Cuerpo: {"status": "Confirmed"}. Las transiciones válidas las controla la base."""
        estado = LeerJson().get("status")
        if estado not in ESTADOS:
            raise ErrorPeticion(f"'status' debe ser uno de: {', '.join(ESTADOS)}.")
        sesion = Permisos.SesionActual()
        self.Autorizar(self.Obtener(id), "editar")
        if estado not in ESTADOS_POR_ROL[sesion.rol]:
            raise Prohibido(f"El rol {sesion.rol} solo puede cambiar el estado a: "
                            f"{', '.join(ESTADOS_POR_ROL[sesion.rol])}.")
        self.aplicacion.CambiarEstado(id, estado)
        return Respuesta(self.AJson(self.Obtener(id)))


controlador = CitasControlador()
blueprint = controlador.blueprint
