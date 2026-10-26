from Entidades import Barberias
from Repositorios import BarberiasRepositorio
from Utilidades import Errores


class BarberiasAplicacion:
    repositorio: BarberiasRepositorio.BarberiasRepositorio = None

    def __init__(self):
        self.repositorio = BarberiasRepositorio.BarberiasRepositorio()

    def Consultar(self) -> list:
        return self.repositorio.Consultar()

    def BuscarPorId(self, id: int) -> Barberias.Barberias | None:
        return self.repositorio.BuscarPorId(id)

    def Insertar(self, entidad: Barberias.Barberias) -> Barberias.Barberias:
        self.Validar(entidad)
        return self.repositorio.Insertar(entidad)

    def Actualizar(self, entidad: Barberias.Barberias) -> Barberias.Barberias:
        self.Validar(entidad)
        return self.repositorio.Actualizar(entidad)

    def Eliminar(self, id: int) -> None:
        self.repositorio.Eliminar(id)

    def Validar(self, entidad: Barberias.Barberias) -> None:
        if entidad.GetName() is None or str(entidad.GetName()).strip() == "":
            raise Errores.ErrorValidacion("El nombre de la barbería es obligatorio.")
        if entidad.GetAddress() is None or str(entidad.GetAddress()).strip() == "":
            raise Errores.ErrorValidacion("La dirección es obligatoria.")
        if entidad.GetCity() is None or str(entidad.GetCity()).strip() == "":
            raise Errores.ErrorValidacion("La ciudad es obligatoria.")
