from datetime import datetime
from decimal import Decimal

from Utilidades import EntidadBase


class Ventas(EntidadBase.EntidadBase):
    # Atributos que se intercambian con la consola y los procedimientos almacenados
    Campos: list = [
        "id",
        "customer_id",
        "customer_name",
        "seller_user_id",
        "seller_name",
        "sale_datetime",
        "total_amount",
        "payment_method",
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

    seller_user_id: int = None

    def GetSellerUserId(self) -> int:
        return self.seller_user_id

    def SetSellerUserId(self, value: int) -> None:
        self.seller_user_id = value

    seller_name: str = None

    def GetSellerName(self) -> str:
        return self.seller_name

    def SetSellerName(self, value: str) -> None:
        self.seller_name = value

    sale_datetime: datetime = None

    def GetSaleDatetime(self) -> datetime:
        return self.sale_datetime

    def SetSaleDatetime(self, value: datetime) -> None:
        self.sale_datetime = value

    total_amount: Decimal = None

    def GetTotalAmount(self) -> Decimal:
        return self.total_amount

    def SetTotalAmount(self, value: Decimal) -> None:
        self.total_amount = value

    payment_method: str = None

    def GetPaymentMethod(self) -> str:
        return self.payment_method

    def SetPaymentMethod(self, value: str) -> None:
        self.payment_method = value
