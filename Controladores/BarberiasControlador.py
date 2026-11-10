from Aplicaciones import BarberiasAplicacion
from Controladores.ControladorBase import ControladorBase
from Entidades import Barberias

controlador = ControladorBase("barberias", Barberias.Barberias, BarberiasAplicacion.BarberiasAplicacion())
blueprint = controlador.blueprint
