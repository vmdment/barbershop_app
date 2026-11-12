from Aplicaciones import BarberiasAplicacion
from Controladores import Permisos
from Controladores.ControladorBase import ControladorBase
from Entidades import Barberias


class BarberiasControlador(ControladorBase):
    """Todos ven las barberías. Cada administrador maneja solo las suyas (es su manager_id) y queda
    como administrador de las que registra; no puede pasarle una barbería a otro administrador."""

    def PrepararDatos(self, datos: dict, nuevo: bool) -> None:
        if nuevo:
            datos["manager_id"] = Permisos.SesionActual().usuario_id
        else:
            datos.pop("manager_id", None)

    def EnAlcance(self, barberia, alcance: Permisos.Alcance) -> bool:
        return barberia.GetManagerId() == Permisos.SesionActual().usuario_id


controlador = BarberiasControlador("barberias", Barberias.Barberias, BarberiasAplicacion.BarberiasAplicacion(),
                                   leer=Permisos.TODOS)
blueprint = controlador.blueprint
