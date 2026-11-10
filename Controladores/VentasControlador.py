from Aplicaciones import VentasAplicacion
from Controladores.ControladorBase import ControladorBase
from Entidades import Ventas

controlador = ControladorBase("ventas", Ventas.Ventas, VentasAplicacion.VentasAplicacion())
blueprint = controlador.blueprint
