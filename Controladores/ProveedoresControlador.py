from Aplicaciones import ProveedoresAplicacion
from Controladores.ControladorBase import ControladorBase
from Entidades import Proveedores

controlador = ControladorBase("proveedores", Proveedores.Proveedores, ProveedoresAplicacion.ProveedoresAplicacion())
blueprint = controlador.blueprint
