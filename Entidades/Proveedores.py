from Utilidades import EntidadBase


class Proveedores(EntidadBase.EntidadBase):
    # Atributos que se intercambian con la consola y los procedimientos almacenados
    Campos: list = ["id", "company_name", "contact_name", "phone", "email", "address"]

    id: int = 0

    def GetId(self) -> int:
        return self.id

    def SetId(self, value: int) -> None:
        self.id = value

    company_name: str = None

    def GetCompanyName(self) -> str:
        return self.company_name

    def SetCompanyName(self, value: str) -> None:
        self.company_name = value

    contact_name: str = None

    def GetContactName(self) -> str:
        return self.contact_name

    def SetContactName(self, value: str) -> None:
        self.contact_name = value

    phone: str = None

    def GetPhone(self) -> str:
        return self.phone

    def SetPhone(self, value: str) -> None:
        self.phone = value

    email: str = None

    def GetEmail(self) -> str:
        return self.email

    def SetEmail(self, value: str) -> None:
        self.email = value

    address: str = None

    def GetAddress(self) -> str:
        return self.address

    def SetAddress(self, value: str) -> None:
        self.address = value
