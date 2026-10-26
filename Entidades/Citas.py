from datetime import date, time
from decimal import Decimal

from Utilidades import EntidadBase


class Citas(EntidadBase.EntidadBase):
    # Atributos que se intercambian con la consola y los procedimientos almacenados
    Campos: list = [
        "id",
        "customer_id",
        "customer_name",
        "barber_id",
        "barber_name",
        "barbershop_id",
        "appointment_date",
        "start_time",
        "end_time",
        "location_type",
        "home_address",
        "status",
        "total_amount",
    ]

    id: int = 0

    def GetId(self) -> int:
        return self.id

    def SetId(self, value: int) -> None:
        self.id = value

    customer_id: int = None

    def GetCustomerId(self) -> int:
        return self.customer_id

    def SetCustomerId(self, value: int) -> None:
        self.customer_id = value

    customer_name: str = None

    def GetCustomerName(self) -> str:
        return self.customer_name

    def SetCustomerName(self, value: str) -> None:
        self.customer_name = value

    barber_id: int = None

    def GetBarberId(self) -> int:
        return self.barber_id

    def SetBarberId(self, value: int) -> None:
        self.barber_id = value

    barber_name: str = None

    def GetBarberName(self) -> str:
        return self.barber_name

    def SetBarberName(self, value: str) -> None:
        self.barber_name = value

    barbershop_id: int = None

    def GetBarbershopId(self) -> int:
        return self.barbershop_id

    def SetBarbershopId(self, value: int) -> None:
        self.barbershop_id = value

    appointment_date: date = None

    def GetAppointmentDate(self) -> date:
        return self.appointment_date

    def SetAppointmentDate(self, value: date) -> None:
        self.appointment_date = value

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

    location_type: str = None

    def GetLocationType(self) -> str:
        return self.location_type

    def SetLocationType(self, value: str) -> None:
        self.location_type = value

    home_address: str = None

    def GetHomeAddress(self) -> str:
        return self.home_address

    def SetHomeAddress(self, value: str) -> None:
        self.home_address = value

    status: str = None

    def GetStatus(self) -> str:
        return self.status

    def SetStatus(self, value: str) -> None:
        self.status = value

    total_amount: Decimal = None

    def GetTotalAmount(self) -> Decimal:
        return self.total_amount

    def SetTotalAmount(self, value: Decimal) -> None:
        self.total_amount = value
