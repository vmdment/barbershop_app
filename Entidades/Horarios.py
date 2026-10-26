from datetime import time

from Utilidades import EntidadBase


class Horarios(EntidadBase.EntidadBase):
    # Atributos que se intercambian con la consola y los procedimientos almacenados
    Campos: list = [
        "id",
        "barber_id",
        "day_of_week",
        "start_time",
        "end_time",
        "lunch_start_time",
        "lunch_end_time",
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

    day_of_week: str = None

    def GetDayOfWeek(self) -> str:
        return self.day_of_week

    def SetDayOfWeek(self, value: str) -> None:
        self.day_of_week = value

    start_time: time = None

    def GetStartTime(self) -> time:
        return self.start_time

    def SetStartTime(self, value: time) -> None:
        self.start_time = value

    end_time: time = None

    def GetEndTime(self) -> time:
        return self.end_time

    def SetEndTime(self, value: time) -> None:
        self.end_time = value

    lunch_start_time: time = None

    def GetLunchStartTime(self) -> time:
        return self.lunch_start_time

    def SetLunchStartTime(self, value: time) -> None:
        self.lunch_start_time = value

    lunch_end_time: time = None

    def GetLunchEndTime(self) -> time:
        return self.lunch_end_time

    def SetLunchEndTime(self, value: time) -> None:
        self.lunch_end_time = value
