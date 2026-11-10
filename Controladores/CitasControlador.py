from Aplicaciones import CitasAplicacion
from Controladores.ControladorBase import ControladorBase, ErrorPeticion, LeerJson, Respuesta
from Entidades import Citas

# Mismos estados que el ENUM de la tabla appointments
ESTADOS = ("Pending", "Confirmed", "Completed", "Cancelled")


class CitasControlador(ControladorBase):

    def __init__(self):
        super().__init__("citas", Citas.Citas, CitasAplicacion.CitasAplicacion())
        self.RegistrarRuta("/cliente/<int:customer_id>", "por_cliente", self.ConsultarPorCliente, "GET",
                           "Citas de un cliente", lista=True)
        self.RegistrarRuta("/barbero/<int:barber_id>", "por_barbero", self.ConsultarPorBarbero, "GET",
                           "Citas de un barbero", lista=True)
        self.RegistrarRuta("/<int:id>/estado", "cambiar_estado", self.CambiarEstado, "PATCH",
                           "Cambiar el estado (Pending→Confirmed/Cancelled, Confirmed→Completed/Cancelled)",
                           cuerpo={"type": "object", "required": ["status"],
                                   "properties": {"status": {"type": "string", "enum": list(ESTADOS)}}})

    def ConsultarPorCliente(self, customer_id: int):
        return Respuesta(self.ListaJson(self.aplicacion.ConsultarPorCliente(customer_id)))

    def ConsultarPorBarbero(self, barber_id: int):
        return Respuesta(self.ListaJson(self.aplicacion.ConsultarPorBarbero(barber_id)))

    def CambiarEstado(self, id: int):
        """Cuerpo: {"status": "Confirmed"}. Las transiciones válidas las controla la base."""
        estado = LeerJson().get("status")
        if estado not in ESTADOS:
            raise ErrorPeticion(f"'status' debe ser uno de: {', '.join(ESTADOS)}.")
        self.Obtener(id)
        self.aplicacion.CambiarEstado(id, estado)
        return Respuesta(self.AJson(self.Obtener(id)))


controlador = CitasControlador()
blueprint = controlador.blueprint
