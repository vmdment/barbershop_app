from Aplicaciones import CitasAplicacion, ServiciosCitaAplicacion
from Controladores import Permisos
from Controladores.CitasControlador import EsParticipante
from Controladores.ControladorBase import ControladorBase, LeerEnteroQuery, NoEncontrado, Respuesta
from Entidades import ServiciosCita
from Controladores.Permisos import ADMIN, BARBERO, CLIENTE, TODOS, Prohibido

_citas = CitasAplicacion.CitasAplicacion()


class ServiciosCitaControlador(ControladorBase):
    """Servicios de una cita. Cada usuario solo ve y toca los de sus propias citas:
    - Cliente: agrega o quita servicios al pedir la cita (el precio lo pone la base, no el cliente).
    - Barbero: además puede ajustar el precio y la duración aplicados.
    La base solo deja modificar los servicios de citas pendientes o confirmadas."""

    def __init__(self):
        super().__init__("servicios-cita", ServiciosCita.ServiciosCita,
                         ServiciosCitaAplicacion.ServiciosCitaAplicacion(), filtro="appointment_id", crud=False)
        consulta = [{"nombre": "appointment_id", "en": "query"}]
        self.RegistrarRuta("", "consultar", self.Consultar, "GET", "Listar los servicios de una cita",
                           parametros=consulta, lista=True, roles=TODOS)
        self.RegistrarRuta("/<int:id>", "buscar", self.BuscarPorId, "GET", "Buscar por ID", roles=TODOS)
        self.RegistrarRuta("", "insertar", self.Insertar, "POST", "Agregar un servicio a la cita",
                           cuerpo="entidad", roles=TODOS)
        self.RegistrarRuta("/<int:id>", "actualizar", self.Actualizar, "PUT",
                           "Ajustar precio o duración aplicados", cuerpo="entidad", roles=(ADMIN, BARBERO))
        self.RegistrarRuta("/<int:id>", "eliminar", self.Eliminar, "DELETE", "Quitar el servicio de la cita",
                           respuesta="texto", roles=TODOS)

    def ValidarCita(self, appointment_id) -> None:
        sesion = Permisos.SesionActual()
        if sesion.EsAdmin():
            return
        cita = _citas.BuscarPorId(appointment_id) if appointment_id else None
        if cita is None:
            raise NoEncontrado(f"No existe la cita con ID {appointment_id}.")
        if not EsParticipante(sesion, cita):
            raise Prohibido("Solo puede ver o modificar los servicios de sus propias citas.")

    def PrepararDatos(self, datos: dict, nuevo: bool) -> None:
        if Permisos.SesionActual().rol == CLIENTE:
            datos.pop("applied_price", None)             # se toma el precio del barbero o del servicio
            datos.pop("applied_duration_minutes", None)

    def Autorizar(self, detalle, accion: str) -> None:
        self.ValidarCita(detalle.GetAppointmentId())

    def Consultar(self):
        appointment_id = LeerEnteroQuery("appointment_id")
        self.ValidarCita(appointment_id)
        return Respuesta(self.ListaJson(self.aplicacion.Consultar(appointment_id)))


controlador = ServiciosCitaControlador()
blueprint = controlador.blueprint
