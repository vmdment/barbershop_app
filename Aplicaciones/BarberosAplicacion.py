from Entidades import Barberos
from Repositorios import BarberosRepositorio
from Utilidades import Errores


class BarberosAplicacion:
    repositorio: BarberosRepositorio.BarberosRepositorio = None

    def __init__(self):
        self.repositorio = BarberosRepositorio.BarberosRepositorio()

    def Consultar(self) -> list:
        return self.repositorio.Consultar()

    def BuscarPorId(self, id: int) -> Barberos.Barberos | None:
        return self.repositorio.BuscarPorId(id)

    def Insertar(self, entidad: Barberos.Barberos) -> Barberos.Barberos:
        self.Validar(entidad)
        return self.repositorio.Insertar(entidad)

    def Actualizar(self, entidad: Barberos.Barberos) -> Barberos.Barberos:
        self.Validar(entidad)
        return self.repositorio.Actualizar(entidad)

    def Eliminar(self, id: int) -> None:
        self.repositorio.Eliminar(id)

    def Validar(self, entidad: Barberos.Barberos) -> None:
        if not entidad.GetProvidesHomeService() and not entidad.GetProvidesShopService():
            raise Errores.ErrorValidacion("El barbero debe atender en barbería, a domicilio o ambos.")
        if entidad.GetProvidesShopService() and entidad.GetBarbershopId() is None:
            raise Errores.ErrorValidacion("Si atiende en barbería debe indicar a qué barbería pertenece.")
