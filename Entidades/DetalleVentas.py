from decimal import Decimal

from Utilidades import EntidadBase


class DetalleVentas(EntidadBase.EntidadBase):
    # Atributos que se intercambian con la consola y los procedimientos almacenados
    Campos: list = [
        "id",
        "product_sale_id",
        "product_id",
        "product_name",
        "quantity",
        "unit_price",
        "subtotal",
    ]

    id: int = 0

    def GetId(self) -> int:
        return self.id

    def SetId(self, value: int) -> None:
        self.id = value

    product_sale_id: int = None

    def GetProductSaleId(self) -> int:
        return self.product_sale_id

    def SetProductSaleId(self, value: int) -> None:
        self.product_sale_id = value

    product_id: int = None

    def GetProductId(self) -> int:
        return self.product_id

    def SetProductId(self, value: int) -> None:
        self.product_id = value

    product_name: str = None

    def GetProductName(self) -> str:
        return self.product_name

    def SetProductName(self, value: str) -> None:
        self.product_name = value

    quantity: int = None

    def GetQuantity(self) -> int:
        return self.quantity

    def SetQuantity(self, value: int) -> None:
        self.quantity = value

    unit_price: Decimal = None

    def GetUnitPrice(self) -> Decimal:
        return self.unit_price

    def SetUnitPrice(self, value: Decimal) -> None:
        self.unit_price = value

    subtotal: Decimal = None

    def GetSubtotal(self) -> Decimal:
        return self.subtotal

    def SetSubtotal(self, value: Decimal) -> None:
        self.subtotal = value
