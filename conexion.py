import pyodbc;

class Conexion:
    _connectionString = ""
    _cursor:pyodbc.Cursor = None
    _conexion: pyodbc.Connection = None
    def __init__(self, connectionString: str):
        self._connectionString = connectionString
    
    def openConnection(self) -> None:
        self._conexion = pyodbc.connect(self._connectionString)
        self._cursor = self._conexion.cursor()
    
    def execute(self, script: str,isQuery: bool=False) -> pyodbc.Cursor:   
        data = self._cursor.execute(script)
        if not isQuery:
            self._conexion.commit()
        return data
    
    def closeConnection(self) -> None:
        if self._cursor:
            self._cursor.close()
        if self._conexion:
            self._conexion.close()

       
    
conexion = Conexion(
    (
        "Driver={MySQL ODBC 26.7 Unicode Driver};"
        "Server=localhost;"
        "Database=barbershop_db;"
        "PORT=3306;"
        "UID=usuario_python;"
        "PWD=5sd64g56dfg54;"
    )
)
