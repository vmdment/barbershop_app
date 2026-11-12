from Aplicaciones import ComprasAplicacion
from Controladores.ControladorBase import ControladorBase
from Entidades import Compras


def EnAlcance(compra, alcance) -> bool:
    """La barbería y el barbero indicados (si los hay) deben ser del administrador."""
    return ((compra.GetBarbershopId() is None or alcance.Barberia(compra.GetBarbershopId()))
            and (compra.GetBarberId() is None or alcance.Barbero(compra.GetBarberId())))


controlador = ControladorBase("compras", Compras.Compras, ComprasAplicacion.ComprasAplicacion(), alcance=EnAlcance)
blueprint = controlador.blueprint
