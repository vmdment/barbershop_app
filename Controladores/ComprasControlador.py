from Aplicaciones import ComprasAplicacion
from Controladores.ControladorBase import ControladorBase
from Entidades import Compras

controlador = ControladorBase("compras", Compras.Compras, ComprasAplicacion.ComprasAplicacion())
blueprint = controlador.blueprint
