import pyodbc;

class Conexion:
    _connectionString = ""
    _cursor:pyodbc.Cursor = None
    _conexion: pyodbc.Connection = None
    def __init__(self, connectionString: str):
        self._connectionString = connectionString
    
    def openConnection(self) -> None:
        self._conexion = pyodbc.connect(self.connectionString)
        self._cursor = conexion.cursor()
    
    def execute(self, script: str) -> pyodbc.Cursor:
        data = self._cursor.execute(script)
        return data
    
    def closeConnection(self) -> None:
        self._cursor.close()
        self._conexion.close()
    
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
