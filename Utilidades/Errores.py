class ErrorBD(Exception):
    """Error de base de datos con un mensaje legible para el usuario."""


class ErrorValidacion(Exception):
    """Una regla de negocio de la capa de Aplicaciones no se cumple."""
