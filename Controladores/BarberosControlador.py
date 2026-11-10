from Aplicaciones import BarberosAplicacion
from Controladores.ControladorBase import ControladorBase
from Entidades import Barberos

controlador = ControladorBase("barberos", Barberos.Barberos, BarberosAplicacion.BarberosAplicacion())
blueprint = controlador.blueprint
