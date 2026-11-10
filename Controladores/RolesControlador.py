from Aplicaciones import RolesAplicacion
from Controladores.ControladorBase import ControladorBase
from Entidades import Roles

controlador = ControladorBase("roles", Roles.Roles, RolesAplicacion.RolesAplicacion())
blueprint = controlador.blueprint
