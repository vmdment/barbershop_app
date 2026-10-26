from decimal import Decimal

from Utilidades import EntidadBase


class Servicios(EntidadBase.EntidadBase):
    # Atributos que se intercambian con la consola y los procedimientos almacenados
    Campos: list = [
        "id",
        "name",
        "description",
        "base_price",
        "duration_minutes",
        "buffer_minutes",
    ]

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

    description: str = None

    def GetDescription(self) -> str:
        return self.description

    def SetDescription(self, value: str) -> None:
        self.description = value

    base_price: Decimal = None

    def GetBasePrice(self) -> Decimal:
        return self.base_price

    def SetBasePrice(self, value: Decimal) -> None:
        self.base_price = value

    duration_minutes: int = None

    def GetDurationMinutes(self) -> int:
        return self.duration_minutes

    def SetDurationMinutes(self, value: int) -> None:
        self.duration_minutes = value

    buffer_minutes: int = None

    def GetBufferMinutes(self) -> int:
        return self.buffer_minutes

    def SetBufferMinutes(self, value: int) -> None:
        self.buffer_minutes = value
