from Aplicaciones import ServiciosAplicacion
from Controladores import Permisos
from Controladores.ControladorBase import ControladorBase
from Entidades import Servicios

controlador = ControladorBase("servicios", Servicios.Servicios, ServiciosAplicacion.ServiciosAplicacion(),
                              leer=Permisos.TODOS)
blueprint = controlador.blueprint
