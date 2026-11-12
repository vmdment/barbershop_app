from Aplicaciones import BloqueosAplicacion
from Controladores import Permisos
from Controladores.ControladorBase import ControladorBase
from Entidades import Bloqueos

controlador = ControladorBase("bloqueos", Bloqueos.Bloqueos, BloqueosAplicacion.BloqueosAplicacion(), filtro="barber_id",
                              leer=(Permisos.ADMIN, Permisos.BARBERO),
                              alcance=lambda e, a: a.Barbero(e.GetBarberId()))
blueprint = controlador.blueprint
