from Aplicaciones import ServiciosBarberoAplicacion
from Controladores import Permisos
from Controladores.ControladorBase import ControladorBase
from Entidades import ServiciosBarbero

controlador = ControladorBase("servicios-barbero", ServiciosBarbero.ServiciosBarbero, ServiciosBarberoAplicacion.ServiciosBarberoAplicacion(), filtro="barber_id",
                              leer=Permisos.TODOS)
blueprint = controlador.blueprint
