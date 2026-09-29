import pyodbc;

class Conexion:
    _connectionString = ""
    def __init__(self, connectionString: str):
        self._connectionString = connectionString
    def execute(self, script: str) -> pyodbc.Cursor:
        conexion = pyodbc.connect(self.connectionString)
        cursor = conexion.cursor()
        data = cursor.execute(script)
        cursor.close()
        conexion.close()
        return data

conexion = Conexion(
    (
        "Driver={MySQL ODBC 9.0 Unicode Driver};"
        "Server=localhost;"
        "Database=lab_1_luis_mosquera;"
        "PORT=3306;"
        "UID=usuario_python;"
        "PWD=5sd64g56dfg54;"
    )
)