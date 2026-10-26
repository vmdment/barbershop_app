from decimal import Decimal

from Utilidades import EntidadBase


class Productos(EntidadBase.EntidadBase):
    # Atributos que se intercambian con la consola y los procedimientos almacenados
    Campos: list = [
        "id",
        "barbershop_id",
        "barbershop_name",
        "barber_id",
        "barber_name",
        "name",
        "description",
        "selling_price",
        "stock_quantity",
        "min_stock_level",
    ]

    id: int = 0

    def GetId(self) -> int:
        return self.id

    def SetId(self, value: int) -> None:
        self.id = value

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

    selling_price: Decimal = None

    def GetSellingPrice(self) -> Decimal:
        return self.selling_price

    def SetSellingPrice(self, value: Decimal) -> None:
        self.selling_price = value

    stock_quantity: int = None

    def GetStockQuantity(self) -> int:
        return self.stock_quantity

    def SetStockQuantity(self, value: int) -> None:
        self.stock_quantity = value

    min_stock_level: int = None

    def GetMinStockLevel(self) -> int:
        return self.min_stock_level

    def SetMinStockLevel(self, value: int) -> None:
        self.min_stock_level = value
