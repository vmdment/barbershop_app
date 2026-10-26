from Utilidades import EntidadBase


class Roles(EntidadBase.EntidadBase):
    # Atributos que se intercambian con la consola y los procedimientos almacenados
    Campos: list = ["id", "name"]

    id: int = 0

    def GetId(self) -> int:
        return self.id

    def SetId(self, value: int) -> None:
        self.id = value

    name: str = None

    def GetName(self) -> str:
        return self.name

    def SetName(self, value: str) -> None:
        self.name = value
