from Aplicaciones import ServiciosAplicacion
from Controladores.ControladorBase import ControladorBase
from Entidades import Servicios

controlador = ControladorBase("servicios", Servicios.Servicios, ServiciosAplicacion.ServiciosAplicacion())
blueprint = controlador.blueprint
