from datetime import datetime

from Entidades import Citas
from Repositorios import CitasRepositorio
from Utilidades import Errores


class CitasAplicacion:
    repositorio: CitasRepositorio.CitasRepositorio = None

    def __init__(self):
        self.repositorio = CitasRepositorio.CitasRepositorio()

    def Consultar(self) -> list:
        return self.repositorio.Consultar()

    def ConsultarPorCliente(self, customer_id: int) -> list:
        return self.repositorio.ConsultarPorCliente(customer_id)

    def ConsultarPorBarbero(self, barber_id: int) -> list:
        return self.repositorio.ConsultarPorBarbero(barber_id)

    def BuscarPorId(self, id: int) -> Citas.Citas | None:
        return self.repositorio.BuscarPorId(id)

    def Insertar(self, entidad: Citas.Citas) -> Citas.Citas:
        self.Validar(entidad)
        return self.repositorio.Insertar(entidad)

    def Actualizar(self, entidad: Citas.Citas) -> Citas.Citas:
        self.Validar(entidad)
        return self.repositorio.Actualizar(entidad)

    def Eliminar(self, id: int) -> None:
        self.repositorio.Eliminar(id)

    def CambiarEstado(self, id: int, estado: str) -> None:
        self.repositorio.CambiarEstado(id, estado)

    def Validar(self, entidad: Citas.Citas) -> None:
        if entidad.GetEndTime() <= entidad.GetStartTime():
            raise Errores.ErrorValidacion("La hora de fin debe ser posterior a la hora de inicio.")
        if datetime.combine(entidad.GetAppointmentDate(), entidad.GetStartTime()) <= datetime.now():
            raise Errores.ErrorValidacion("No se pueden agendar citas en el pasado.")
