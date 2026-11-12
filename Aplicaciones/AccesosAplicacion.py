from Repositorios import AccesosRepositorio

EVENTOS = ("Login", "Failed", "Register", "Logout")


class AccesosAplicacion:
    """Registro de accesos al sistema. Registrar nunca debe impedir el inicio de sesión."""
    repositorio: AccesosRepositorio.AccesosRepositorio = None

    def __init__(self):
        self.repositorio = AccesosRepositorio.AccesosRepositorio()

    def Consultar(self, user_id: int | None = None, limite: int = 200) -> list:
        return self.repositorio.Consultar(user_id, max(1, min(int(limite), 1000)))

    def Registrar(self, user_id: int | None, email: str, evento: str, ip: str | None = None,
                  agente: str | None = None) -> None:
        if evento not in EVENTOS:
            raise ValueError(f"Evento de acceso desconocido: {evento}")
        self.repositorio.Registrar(user_id, (email or "").strip()[:100], evento, ip, (agente or "")[:255] or None)
