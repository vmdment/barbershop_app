from datetime import datetime

from Utilidades import EntidadBase


class Bloqueos(EntidadBase.EntidadBase):
    # Atributos que se intercambian con la consola y los procedimientos almacenados
    Campos: list = ["id", "barber_id", "start_datetime", "end_datetime", "reason"]

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

    start_datetime: datetime = None

    def GetStartDatetime(self) -> datetime:
        return self.start_datetime

    def SetStartDatetime(self, value: datetime) -> None:
        self.start_datetime = value

    end_datetime: datetime = None

    def GetEndDatetime(self) -> datetime:
        return self.end_datetime

    def SetEndDatetime(self, value: datetime) -> None:
        self.end_datetime = value

    reason: str = None

    def GetReason(self) -> str:
        return self.reason

    def SetReason(self, value: str) -> None:
        self.reason = value
