import configparser
import re
from pathlib import Path

import pyodbc

ARCHIVO_CONFIG = Path(__file__).with_name("config.ini")


class ErrorBD(Exception):
    """Error de base de datos con un mensaje legible para el usuario."""


def leerConfiguracion(ruta: Path = ARCHIVO_CONFIG) -> str:
    """Arma la cadena de conexión con los datos de config.ini (sección [mysql])."""
    if not ruta.exists():
        raise ErrorBD(f"No se encontró {ruta.name}. Copie config.example.ini como "
                      f"config.ini y complete los datos de conexión.")
    config = configparser.ConfigParser(interpolation=None)
    config.read(ruta, encoding="utf-8")
    try:
        mysql = config["mysql"]
        datos = {clave: mysql[clave] for clave in ("driver", "server", "port", "database", "user", "password")}
    except KeyError as e:
        raise ErrorBD(f"Falta {e} en {ruta.name} (sección [mysql]).") from None
    # Las llaves permiten usar ; u otros símbolos en la contraseña
    password = datos["password"].replace("}", "}}")
    return (
        f"Driver={{{datos['driver']}}};"
        f"Server={datos['server']};"
        f"Database={datos['database']};"
        f"PORT={datos['port']};"
        f"UID={datos['user']};"
        f"PWD={{{password}}};"
    )


# Códigos de error de MySQL más comunes y su explicación
_MENSAJES_MYSQL = {
    "1045": "Usuario o contraseña de la base de datos incorrectos (revise conexion.py).",
    "1049": "La base de datos barbershop_db no existe. Ejecute primero el script bd.sql.",
    "1062": "Ya existe un registro con esos datos.",
    "1264": "Un valor numérico está fuera del rango permitido.",
    "1292": "Una fecha u hora tiene un formato inválido.",
    "1305": "El procedimiento almacenado no existe. Ejecute el script bd.sql para crearlo.",
    "1318": "Número de parámetros incorrecto para el procedimiento. Actualice la base con bd.sql.",
    "1366": "Un valor no tiene el tipo de dato correcto.",
    "1406": "Uno de los textos es demasiado largo.",
    "1451": "No se puede eliminar porque tiene registros relacionados.",
    "1452": "Se hace referencia a un registro que no existe.",
    "2002": "No se pudo conectar al servidor MySQL. Verifique que esté encendido.",
    "2003": "No se pudo conectar al servidor MySQL. Verifique que esté encendido.",
    "2006": "Se perdió la conexión con el servidor MySQL.",
    "2013": "Se perdió la conexión con el servidor MySQL.",
}


def traducirError(error: pyodbc.Error) -> str:
    mensaje = str(error.args[1]) if len(error.args) > 1 else str(error)
    codigo = re.search(r"\((\d{4})\)", mensaje)
    if codigo and codigo.group(1) in _MENSAJES_MYSQL:
        return _MENSAJES_MYSQL[codigo.group(1)]
    # Errores lanzados por SIGNAL en los procedimientos (1644) u otros:
    # se quitan los prefijos "[HY000] [MySQL][ODBC ...]" y los sufijos "(1644) (SQLExecDirectW)"
    mensaje = re.split(r";\s*\[", mensaje)[0]   # pyodbc une varios diagnósticos con "; ["
    mensaje = re.sub(r"^\s*(\[[^\]]*\]\s*)+", "", mensaje)
    mensaje = re.sub(r"(\s*\(\w+\))+\s*$", "", mensaje)
    return mensaje.strip() or "Error desconocido de base de datos."


class Conexion:
    _connectionString = ""
    _cursor: pyodbc.Cursor = None
    _conexion: pyodbc.Connection = None

    def __init__(self, connectionString: str = ""):
        self._connectionString = connectionString

    def openConnection(self) -> None:
        if not self._connectionString:
            self._connectionString = leerConfiguracion()
        try:
            self._conexion = pyodbc.connect(self._connectionString)
        except pyodbc.Error as e:
            raise ErrorBD(traducirError(e)) from e
        self._cursor = self._conexion.cursor()

    def execute(self, script: str, isQuery: bool = False) -> pyodbc.Cursor:
        data = self._cursor.execute(script)
        if not isQuery:
            self._conexion.commit()
        return data

    def call(self, procedure: str, params: tuple = ()) -> list[dict]:
        """Ejecuta un procedimiento almacenado con parámetros seguros (?)
        y devuelve las filas del primer resultado como diccionarios."""
        if self._conexion is None:
            raise ErrorBD("No hay una conexión abierta con la base de datos.")
        sql = "{CALL %s(%s)}" % (procedure, ", ".join("?" * len(params)))
        try:
            self._cursor.execute(sql, *params)
            rows = []
            if self._cursor.description:
                columns = [column[0] for column in self._cursor.description]
                rows = [dict(zip(columns, row)) for row in self._cursor.fetchall()]
            # Un CALL devuelve resultados extra (estado); hay que consumirlos
            while self._cursor.nextset():
                pass
            self._conexion.commit()
            return rows
        except pyodbc.Error as e:
            try:
                self._conexion.rollback()
            except pyodbc.Error:
                pass
            raise ErrorBD(traducirError(e)) from e

    def closeConnection(self) -> None:
        if self._cursor:
            self._cursor.close()
        if self._conexion:
            self._conexion.close()
        self._cursor = None
        self._conexion = None


# Los datos de conexión se leen de config.ini al abrir la conexión
conexion = Conexion()
