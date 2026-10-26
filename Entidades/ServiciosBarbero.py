from decimal import Decimal

from Utilidades import EntidadBase


class ServiciosBarbero(EntidadBase.EntidadBase):
    # Atributos que se intercambian con la consola y los procedimientos almacenados
    Campos: list = [
        "id",
        "barber_id",
        "service_id",
        "service_name",
        "custom_price",
        "custom_duration_minutes",
        "final_price",
        "final_duration",
    ]

    id: int = 0

    def GetId(self) -> int:
        return self.id

    def SetId(self, value: int) -> None:
        self.id = value

    barber_id: int = None

    def GetBarberId(self) -> int:
        return self.barber_id

    def SetBarberId(self, value: int) -> None:
        self.barber_id = value

    service_id: int = None

    def GetServiceId(self) -> int:
        return self.service_id

    def SetServiceId(self, value: int) -> None:
        self.service_id = value

    service_name: str = None

    def GetServiceName(self) -> str:
        return self.service_name

    def SetServiceName(self, value: str) -> None:
        self.service_name = value

    custom_price: Decimal = None

    def GetCustomPrice(self) -> Decimal:
        return self.custom_price

    def SetCustomPrice(self, value: Decimal) -> None:
        self.custom_price = value

    custom_duration_minutes: int = None

    def GetCustomDurationMinutes(self) -> int:
        return self.custom_duration_minutes

    def SetCustomDurationMinutes(self, value: int) -> None:
        self.custom_duration_minutes = value

    final_price: Decimal = None

    def GetFinalPrice(self) -> Decimal:
        return self.final_price

    def SetFinalPrice(self, value: Decimal) -> None:
        self.final_price = value

    final_duration: int = None

    def GetFinalDuration(self) -> int:
        return self.final_duration

    def SetFinalDuration(self, value: int) -> None:
        self.final_duration = value
