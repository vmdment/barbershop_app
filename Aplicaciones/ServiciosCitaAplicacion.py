from Entidades import ServiciosCita
from Repositorios import ServiciosCitaRepositorio


class ServiciosCitaAplicacion:
    repositorio: ServiciosCitaRepositorio.ServiciosCitaRepositorio = None

    def __init__(self):
        self.repositorio = ServiciosCitaRepositorio.ServiciosCitaRepositorio()

    def Consultar(self, appointment_id: int) -> list:
        return self.repositorio.Consultar(appointment_id)

    def BuscarPorId(self, id: int) -> ServiciosCita.ServiciosCita | None:
        return self.repositorio.BuscarPorId(id)

    def Insertar(self, entidad: ServiciosCita.ServiciosCita) -> ServiciosCita.ServiciosCita:
        return self.repositorio.Insertar(entidad)

    def Actualizar(self, entidad: ServiciosCita.ServiciosCita) -> ServiciosCita.ServiciosCita:
        return self.repositorio.Actualizar(entidad)

    def Eliminar(self, id: int) -> None:
        self.repositorio.Eliminar(id)
