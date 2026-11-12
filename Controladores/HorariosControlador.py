from Aplicaciones import HorariosAplicacion
from Controladores import Permisos
from Controladores.ControladorBase import ControladorBase
from Entidades import Horarios

controlador = ControladorBase("horarios", Horarios.Horarios, HorariosAplicacion.HorariosAplicacion(), filtro="barber_id",
                              leer=Permisos.TODOS)
blueprint = controlador.blueprint
