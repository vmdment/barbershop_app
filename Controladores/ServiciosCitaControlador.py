from Aplicaciones import ServiciosCitaAplicacion
from Controladores.ControladorBase import ControladorBase
from Entidades import ServiciosCita

controlador = ControladorBase("servicios-cita", ServiciosCita.ServiciosCita, ServiciosCitaAplicacion.ServiciosCitaAplicacion(), filtro="appointment_id")
blueprint = controlador.blueprint
