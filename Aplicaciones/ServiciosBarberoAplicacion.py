from Entidades import ServiciosBarbero
from Repositorios import ServiciosBarberoRepositorio


class ServiciosBarberoAplicacion:
    repositorio: ServiciosBarberoRepositorio.ServiciosBarberoRepositorio = None

    def __init__(self):
        self.repositorio = ServiciosBarberoRepositorio.ServiciosBarberoRepositorio()

    def Consultar(self, barber_id: int) -> list:
        return self.repositorio.Consultar(barber_id)

    def BuscarPorId(self, id: int) -> ServiciosBarbero.ServiciosBarbero | None:
        return self.repositorio.BuscarPorId(id)

    def Insertar(self, entidad: ServiciosBarbero.ServiciosBarbero) -> ServiciosBarbero.ServiciosBarbero:
        return self.repositorio.Insertar(entidad)

    def Actualizar(self, entidad: ServiciosBarbero.ServiciosBarbero) -> ServiciosBarbero.ServiciosBarbero:
        return self.repositorio.Actualizar(entidad)

    def Eliminar(self, id: int) -> None:
        self.repositorio.Eliminar(id)
