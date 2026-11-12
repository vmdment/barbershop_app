from Aplicaciones import ServiciosBarberoAplicacion
from Controladores import Permisos
from Controladores.ControladorBase import ControladorBase
from Entidades import ServiciosBarbero

controlador = ControladorBase("servicios-barbero", ServiciosBarbero.ServiciosBarbero, ServiciosBarberoAplicacion.ServiciosBarberoAplicacion(), filtro="barber_id",
                              leer=Permisos.TODOS,
                              alcance=lambda e, a: a.Barbero(e.GetBarberId()))
blueprint = controlador.blueprint
