from Aplicaciones import HorariosAplicacion
from Controladores.ControladorBase import ControladorBase
from Entidades import Horarios

controlador = ControladorBase("horarios", Horarios.Horarios, HorariosAplicacion.HorariosAplicacion(), filtro="barber_id")
blueprint = controlador.blueprint
