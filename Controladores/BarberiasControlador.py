from Aplicaciones import BarberiasAplicacion
from Controladores import Permisos
from Controladores.ControladorBase import ControladorBase
from Entidades import Barberias

controlador = ControladorBase("barberias", Barberias.Barberias, BarberiasAplicacion.BarberiasAplicacion(),
                              leer=Permisos.TODOS)
blueprint = controlador.blueprint
