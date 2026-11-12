from datetime import datetime

from Utilidades import EntidadBase


class Accesos(EntidadBase.EntidadBase):
    # Registro de accesos (tabla access_log): inicios de sesión, intentos fallidos, registros y salidas
    Campos: list = ["id", "user_id", "full_name", "role_name", "email", "event", "ip_address", "user_agent", "created_at"]

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

    full_name: str = None

    def GetFullName(self) -> str:
        return self.full_name

    def SetFullName(self, value: str) -> None:
        self.full_name = value

    role_name: str = None

    def GetRoleName(self) -> str:
        return self.role_name

    def SetRoleName(self, value: str) -> None:
        self.role_name = value

    email: str = None

    def GetEmail(self) -> str:
        return self.email

    def SetEmail(self, value: str) -> None:
        self.email = value

    event: str = None

    def GetEvent(self) -> str:
        return self.event

    def SetEvent(self, value: str) -> None:
        self.event = value

    ip_address: str = None

    def GetIpAddress(self) -> str:
        return self.ip_address

    def SetIpAddress(self, value: str) -> None:
        self.ip_address = value

    user_agent: str = None

    def GetUserAgent(self) -> str:
        return self.user_agent

    def SetUserAgent(self, value: str) -> None:
        self.user_agent = value

    created_at: datetime = None

    def GetCreatedAt(self) -> datetime:
        return self.created_at

    def SetCreatedAt(self, value: datetime) -> None:
        self.created_at = value
