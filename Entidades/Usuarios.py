from datetime import datetime

from Utilidades import EntidadBase


class Usuarios(EntidadBase.EntidadBase):
    # Atributos que se intercambian con la consola y los procedimientos almacenados
    Campos: list = [
        "id",
        "role_id",
        "role_name",
        "full_name",
        "email",
        "password_hash",
        "phone",
        "created_at",
    ]

    id: int = 0

    def GetId(self) -> int:
        return self.id

    def SetId(self, value: int) -> None:
        self.id = value

    role_id: int = None

    def GetRoleId(self) -> int:
        return self.role_id

    def SetRoleId(self, value: int) -> None:
        self.role_id = value

    role_name: str = None

    def GetRoleName(self) -> str:
        return self.role_name

    def SetRoleName(self, value: str) -> None:
        self.role_name = value

    full_name: str = None

    def GetFullName(self) -> str:
        return self.full_name

    def SetFullName(self, value: str) -> None:
        self.full_name = value

    email: str = None

    def GetEmail(self) -> str:
        return self.email

    def SetEmail(self, value: str) -> None:
        self.email = value

    password_hash: str = None

    def GetPasswordHash(self) -> str:
        return self.password_hash

    def SetPasswordHash(self, value: str) -> None:
        self.password_hash = value

    phone: str = None

    def GetPhone(self) -> str:
        return self.phone

    def SetPhone(self, value: str) -> None:
        self.phone = value

    created_at: datetime = None

    def GetCreatedAt(self) -> datetime:
        return self.created_at

    def SetCreatedAt(self, value: datetime) -> None:
        self.created_at = value
