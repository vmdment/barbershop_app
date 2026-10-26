from decimal import Decimal

from Utilidades import EntidadBase


class Barberos(EntidadBase.EntidadBase):
    # Atributos que se intercambian con la consola y los procedimientos almacenados
    Campos: list = [
        "id",
        "user_id",
        "barber_name",
        "barbershop_id",
        "barbershop_name",
        "provides_home_service",
        "provides_shop_service",
        "commission_rate",
        "is_active",
    ]

    id: int = 0

    def GetId(self) -> int:
        return self.id

    def SetId(self, value: int) -> None:
        self.id = value

    user_id: int = None

    def GetUserId(self) -> int:
        return self.user_id

    def SetUserId(self, value: int) -> None:
        self.user_id = value

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

    provides_home_service: int = None

    def GetProvidesHomeService(self) -> int:
        return self.provides_home_service

    def SetProvidesHomeService(self, value: int) -> None:
        self.provides_home_service = value

    provides_shop_service: int = None

    def GetProvidesShopService(self) -> int:
        return self.provides_shop_service

    def SetProvidesShopService(self, value: int) -> None:
        self.provides_shop_service = value

    commission_rate: Decimal = None

    def GetCommissionRate(self) -> Decimal:
        return self.commission_rate

    def SetCommissionRate(self, value: Decimal) -> None:
        self.commission_rate = value

    is_active: int = None

    def GetIsActive(self) -> int:
        return self.is_active

    def SetIsActive(self, value: int) -> None:
        self.is_active = value
