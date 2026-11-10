from Aplicaciones import BloqueosAplicacion
from Controladores.ControladorBase import ControladorBase
from Entidades import Bloqueos

controlador = ControladorBase("bloqueos", Bloqueos.Bloqueos, BloqueosAplicacion.BloqueosAplicacion(), filtro="barber_id")
blueprint = controlador.blueprint
