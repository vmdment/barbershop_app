from Aplicaciones import BarberosAplicacion
from Controladores import Permisos
from Controladores.ControladorBase import ControladorBase
from Entidades import Barberos


class BarberosControlador(ControladorBase):
    """Todos ven los barberos (el cliente elige uno al pedir cita); solo el administrador los gestiona."""

    def EnAlcance(self, barbero, alcance: Permisos.Alcance) -> bool:
        # Sin barbería (solo a domicilio): cualquier administrador lo ve y puede asignarlo a una suya
        return barbero.GetBarbershopId() is None or alcance.Barberia(barbero.GetBarbershopId())

    def AJson(self, entidad) -> dict:
        datos = super().AJson(entidad)
        if not Permisos.SesionActual().EsAdmin():
            datos.pop("commission_rate", None)   # dato interno de la barbería
        return datos


controlador = BarberosControlador("barberos", Barberos.Barberos, BarberosAplicacion.BarberosAplicacion(),
                                  leer=Permisos.TODOS)
blueprint = controlador.blueprint
