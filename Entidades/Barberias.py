from Utilidades import EntidadBase


class Barberias(EntidadBase.EntidadBase):
    # Atributos que se intercambian con la consola y los procedimientos almacenados
    Campos: list = ["id", "manager_id", "manager_name", "name", "address", "city", "phone"]

    id: int = 0

    def GetId(self) -> int:
        return self.id

    def SetId(self, value: int) -> None:
        self.id = value

    manager_id: int = None

    def GetManagerId(self) -> int:
        return self.manager_id

    def SetManagerId(self, value: int) -> None:
        self.manager_id = value

    manager_name: str = None

    def GetManagerName(self) -> str:
        return self.manager_name

    def SetManagerName(self, value: str) -> None:
        self.manager_name = value

    name: str = None

    def GetName(self) -> str:
        return self.name

    def SetName(self, value: str) -> None:
        self.name = value

    address: str = None

    def GetAddress(self) -> str:
        return self.address

    def SetAddress(self, value: str) -> None:
        self.address = value

    city: str = None

    def GetCity(self) -> str:
        return self.city

    def SetCity(self, value: str) -> None:
        self.city = value

    phone: str = None

    def GetPhone(self) -> str:
        return self.phone

    def SetPhone(self, value: str) -> None:
        self.phone = value
