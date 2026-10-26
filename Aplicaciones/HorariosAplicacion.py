from Entidades import Horarios
from Repositorios import HorariosRepositorio
from Utilidades import Errores


class HorariosAplicacion:
    repositorio: HorariosRepositorio.HorariosRepositorio = None

    def __init__(self):
        self.repositorio = HorariosRepositorio.HorariosRepositorio()

    def Consultar(self, barber_id: int) -> list:
        return self.repositorio.Consultar(barber_id)

    def BuscarPorId(self, id: int) -> Horarios.Horarios | None:
        return self.repositorio.BuscarPorId(id)

    def Insertar(self, entidad: Horarios.Horarios) -> Horarios.Horarios:
        self.Validar(entidad)
        return self.repositorio.Insertar(entidad)

    def Actualizar(self, entidad: Horarios.Horarios) -> Horarios.Horarios:
        self.Validar(entidad)
        return self.repositorio.Actualizar(entidad)

    def Eliminar(self, id: int) -> None:
        self.repositorio.Eliminar(id)

    def Validar(self, entidad: Horarios.Horarios) -> None:
        if entidad.GetEndTime() <= entidad.GetStartTime():
            raise Errores.ErrorValidacion("La hora de salida debe ser posterior a la de entrada.")
        if entidad.GetLunchStartTime() is not None and entidad.GetLunchEndTime() is None:
            raise Errores.ErrorValidacion("Debe indicar el fin del almuerzo.")
        if entidad.GetLunchStartTime() is not None and entidad.GetLunchEndTime() <= entidad.GetLunchStartTime():
            raise Errores.ErrorValidacion("El fin del almuerzo debe ser posterior a su inicio.")
        if entidad.GetLunchStartTime() is not None and (entidad.GetLunchStartTime() < entidad.GetStartTime() or entidad.GetLunchEndTime() > entidad.GetEndTime()):
            raise Errores.ErrorValidacion("El almuerzo debe estar dentro del horario de trabajo.")
