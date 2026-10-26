from Entidades import Bloqueos
from Repositorios import BloqueosRepositorio
from Utilidades import Errores


class BloqueosAplicacion:
    repositorio: BloqueosRepositorio.BloqueosRepositorio = None

    def __init__(self):
        self.repositorio = BloqueosRepositorio.BloqueosRepositorio()

    def Consultar(self, barber_id: int) -> list:
        return self.repositorio.Consultar(barber_id)

    def BuscarPorId(self, id: int) -> Bloqueos.Bloqueos | None:
        return self.repositorio.BuscarPorId(id)

    def Insertar(self, entidad: Bloqueos.Bloqueos) -> Bloqueos.Bloqueos:
        self.Validar(entidad)
        return self.repositorio.Insertar(entidad)

    def Actualizar(self, entidad: Bloqueos.Bloqueos) -> Bloqueos.Bloqueos:
        self.Validar(entidad)
        return self.repositorio.Actualizar(entidad)

    def Eliminar(self, id: int) -> None:
        self.repositorio.Eliminar(id)

    def Validar(self, entidad: Bloqueos.Bloqueos) -> None:
        if entidad.GetEndDatetime() <= entidad.GetStartDatetime():
            raise Errores.ErrorValidacion("El fin del bloqueo debe ser posterior a su inicio.")
