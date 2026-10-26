from Entidades import Servicios
from Repositorios import ServiciosRepositorio
from Utilidades import Errores


class ServiciosAplicacion:
    repositorio: ServiciosRepositorio.ServiciosRepositorio = None

    def __init__(self):
        self.repositorio = ServiciosRepositorio.ServiciosRepositorio()

    def Consultar(self) -> list:
        return self.repositorio.Consultar()

    def BuscarPorId(self, id: int) -> Servicios.Servicios | None:
        return self.repositorio.BuscarPorId(id)

    def Insertar(self, entidad: Servicios.Servicios) -> Servicios.Servicios:
        self.Validar(entidad)
        return self.repositorio.Insertar(entidad)

    def Actualizar(self, entidad: Servicios.Servicios) -> Servicios.Servicios:
        self.Validar(entidad)
        return self.repositorio.Actualizar(entidad)

    def Eliminar(self, id: int) -> None:
        self.repositorio.Eliminar(id)

    def Validar(self, entidad: Servicios.Servicios) -> None:
        if entidad.GetName() is None or str(entidad.GetName()).strip() == "":
            raise Errores.ErrorValidacion("El nombre del servicio es obligatorio.")
