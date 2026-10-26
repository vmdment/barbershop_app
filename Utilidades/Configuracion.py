import os
from pathlib import Path

from Utilidades import Errores

# El .env vive en la carpeta del proyecto (junto a main.py)
ARCHIVO_ENV = Path(__file__).resolve().parent.parent / ".env"
VARIABLES_BD = ("DB_DRIVER", "DB_SERVER", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD")


class Configuracion:

    @staticmethod
    def LeerEnv(ruta: Path) -> dict:
        """Lee un archivo .env con líneas CLAVE=valor (ignora vacías y comentarios #)."""
        valores = {}
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, valor = linea.split("=", 1)
            valor = valor.strip()
            if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in "\"'":
                valor = valor[1:-1]
            valores[clave.strip()] = valor
        return valores

    @staticmethod
    def StringConexion(ruta: Path = ARCHIVO_ENV) -> str:
        """Arma la cadena de conexión con las variables DB_* del archivo .env.
        Las variables de entorno del sistema tienen prioridad sobre el archivo."""
        archivo = Configuracion.LeerEnv(ruta) if ruta.exists() else {}
        datos = {clave: os.environ.get(clave, archivo.get(clave)) for clave in VARIABLES_BD}
        faltantes = [clave for clave, valor in datos.items() if not valor]
        if faltantes:
            if not ruta.exists():
                raise Errores.ErrorBD("No se encontró el archivo .env. Copie .env.example como .env "
                                      "y complete los datos de conexión.")
            raise Errores.ErrorBD(f"Faltan datos de conexión en .env: {', '.join(faltantes)}.")
        # Las llaves permiten usar ; u otros símbolos en la contraseña
        password = datos["DB_PASSWORD"].replace("}", "}}")
        return (
            f"Driver={{{datos['DB_DRIVER']}}};"
            f"Server={datos['DB_SERVER']};"
            f"Database={datos['DB_NAME']};"
            f"PORT={datos['DB_PORT']};"
            f"UID={datos['DB_USER']};"
            f"PWD={{{password}}};"
        )
