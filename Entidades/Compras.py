from datetime import datetime
from decimal import Decimal

from Utilidades import EntidadBase


class Compras(EntidadBase.EntidadBase):
    # Atributos que se intercambian con la consola y los procedimientos almacenados
    Campos: list = [
        "id",
        "supplier_id",
        "company_name",
        "barber_id",
        "barber_name",
        "barbershop_id",
        "barbershop_name",
        "purchase_datetime",
        "tools_description",
        "total_paid",
    ]

    id: int = 0

    def GetId(self) -> int:
        return self.id

    def SetId(self, value: int) -> None:
        self.id = value

    supplier_id: int = None

    def GetSupplierId(self) -> int:
        return self.supplier_id

    def SetSupplierId(self, value: int) -> None:
        self.supplier_id = value

    company_name: str = None

    def GetCompanyName(self) -> str:
        return self.company_name

    def SetCompanyName(self, value: str) -> None:
        self.company_name = value

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

    barbershop_name: str = None

    def GetBarbershopName(self) -> str:
        return self.barbershop_name

    def SetBarbershopName(self, value: str) -> None:
        self.barbershop_name = value

    purchase_datetime: datetime = None

    def GetPurchaseDatetime(self) -> datetime:
        return self.purchase_datetime

    def SetPurchaseDatetime(self, value: datetime) -> None:
        self.purchase_datetime = value

    tools_description: str = None

    def GetToolsDescription(self) -> str:
        return self.tools_description

    def SetToolsDescription(self, value: str) -> None:
        self.tools_description = value

    total_paid: Decimal = None

    def GetTotalPaid(self) -> Decimal:
        return self.total_paid

    def SetTotalPaid(self, value: Decimal) -> None:
        self.total_paid = value
