from decimal import Decimal

from Utilidades import EntidadBase


class ServiciosCita(EntidadBase.EntidadBase):
    # Atributos que se intercambian con la consola y los procedimientos almacenados
    Campos: list = [
        "id",
        "appointment_id",
        "service_id",
        "service_name",
        "applied_price",
        "applied_duration_minutes",
    ]

    id: int = 0

    def GetId(self) -> int:
        return self.id

    def SetId(self, value: int) -> None:
        self.id = value

    appointment_id: int = None

    def GetAppointmentId(self) -> int:
        return self.appointment_id

    def SetAppointmentId(self, value: int) -> None:
        self.appointment_id = value

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

    applied_price: Decimal = None

    def GetAppliedPrice(self) -> Decimal:
        return self.applied_price

    def SetAppliedPrice(self, value: Decimal) -> None:
        self.applied_price = value

    applied_duration_minutes: int = None

    def GetAppliedDurationMinutes(self) -> int:
        return self.applied_duration_minutes

    def SetAppliedDurationMinutes(self, value: int) -> None:
        self.applied_duration_minutes = value
