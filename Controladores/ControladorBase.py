"""Controlador REST genérico sobre la capa de Aplicaciones.

Cada controlador de entidad crea un ControladorBase que registra en un Blueprint de Flask:

    GET    /api/<nombre>            Consultar()  (si hay filtro: ?<filtro>=<id> obligatorio)
    GET    /api/<nombre>/<id>       BuscarPorId(id)
    POST   /api/<nombre>            Insertar(entidad)     cuerpo JSON
    PUT    /api/<nombre>/<id>       Actualizar(entidad)   cuerpo JSON (solo los campos a cambiar)
    DELETE /api/<nombre>/<id>       Eliminar(id)

Las respuestas siguen el formato {"Respuesta": ...} o {"Error": "..."}.
"""
import functools
import threading
import typing
from datetime import date, datetime, time, timedelta
from decimal import Decimal, InvalidOperation

import flask

from Utilidades import Conexion, Errores

# La conexión ODBC es una sola y compartida: se usa por turnos (una petición a la vez)
_candado = threading.Lock()


class ErrorPeticion(Exception):
    """La petición HTTP está mal formada (JSON inválido, parámetro faltante, tipo incorrecto)."""


class NoEncontrado(Exception):
    """El registro solicitado no existe."""


# ------------------------------------------------------------------
# Respuestas y manejo de errores
# ------------------------------------------------------------------

def Respuesta(datos, codigo: int = 200):
    return flask.jsonify({"Respuesta": datos}), codigo


def RespuestaError(mensaje: str, codigo: int):
    return flask.jsonify({"Error": mensaje}), codigo


def Responder(funcion):
    """Decorador de cada ruta: abre la conexión si hace falta, usa la conexión por turnos
    y traduce las excepciones de las capas inferiores a códigos HTTP."""
    @functools.wraps(funcion)
    def envoltura(*args, **kwargs):
        with _candado:
            try:
                if Conexion.conexion._conexion is None:
                    Conexion.conexion.openConnection()
                return funcion(*args, **kwargs)
            except ErrorPeticion as e:
                return RespuestaError(str(e), 400)
            except Errores.ErrorValidacion as e:
                return RespuestaError(str(e), 400)
            except NoEncontrado as e:
                return RespuestaError(str(e), 404)
            except Errores.ErrorBD as e:
                return RespuestaError(str(e), 409)
            except (TypeError, AttributeError):
                # Una regla de negocio recibió un campo vacío o de otro tipo
                flask.current_app.logger.exception("Datos incompletos")
                return RespuestaError("Datos incompletos o con un tipo incorrecto.", 400)
            except Exception:
                flask.current_app.logger.exception("Error inesperado")
                return RespuestaError("Error interno del servidor.", 500)
    return envoltura


# ------------------------------------------------------------------
# Conversión JSON <-> Entidad
# ------------------------------------------------------------------

def ConvertirValor(campo: str, valor, tipo):
    """Convierte un valor recibido en JSON al tipo declarado en la entidad."""
    if valor is None:
        return None
    if tipo is str:
        return str(valor)
    if isinstance(valor, str) and valor.strip() == "":
        return None
    try:
        if tipo is int:
            if isinstance(valor, float) and not valor.is_integer():
                raise ValueError
            return int(valor)
        if tipo is Decimal:
            numero = Decimal(str(valor).replace(",", "."))
            if not numero.is_finite():
                raise ValueError
            return numero
        if tipo is datetime:
            return datetime.fromisoformat(str(valor).replace("T", " "))
        if tipo is date:
            return date.fromisoformat(str(valor))
        if tipo is time:
            return time.fromisoformat(str(valor))
    except (ValueError, TypeError, InvalidOperation):
        formatos = {int: "un número entero", Decimal: "un número", datetime: "AAAA-MM-DD HH:MM",
                    date: "AAAA-MM-DD", time: "HH:MM"}
        raise ErrorPeticion(f"El campo '{campo}' debe ser {formatos.get(tipo, tipo.__name__)}.") from None
    return valor


def ValorJson(valor):
    """Convierte un valor de la entidad a algo que JSON entienda."""
    if isinstance(valor, (datetime, date, time)):
        return valor.isoformat()
    if isinstance(valor, timedelta):
        return str(valor)
    if isinstance(valor, Decimal):
        return float(valor)
    return valor


def LeerJson() -> dict:
    datos = flask.request.get_json(silent=True)
    if not isinstance(datos, dict):
        raise ErrorPeticion("El cuerpo de la petición debe ser un objeto JSON.")
    return datos


def LeerEnteroQuery(nombre: str) -> int:
    valor = flask.request.args.get(nombre, "")
    if not valor.isdigit():
        raise ErrorPeticion(f"Falta el parámetro '?{nombre}=<id>' (número entero).")
    return int(valor)


# ------------------------------------------------------------------
# Controlador genérico
# ------------------------------------------------------------------

class ControladorBase:
    # Campos que nunca se devuelven en las respuestas (ej. password_hash)
    ocultos: tuple = ()

    def __init__(self, nombre: str, clase, aplicacion, filtro: str | None = None):
        """nombre: segmento de la URL (/api/<nombre>); clase: clase de Entidades;
        aplicacion: objeto de Aplicaciones; filtro: parámetro obligatorio de Consultar()."""
        self.nombre = nombre
        self.clase = clase
        self.aplicacion = aplicacion
        self.filtro = filtro
        self.tipos = typing.get_type_hints(clase)
        self.blueprint = flask.Blueprint(nombre, __name__, url_prefix=f"/api/{nombre}")

        # Documentación de cada ruta, usada para generar el Swagger (Controladores/SwaggerControlador.py)
        self.documentacion: list[dict] = []

        consulta = [{"nombre": filtro, "en": "query"}] if filtro else []
        self.RegistrarRuta("", "consultar", self.Consultar, "GET", "Listar", parametros=consulta, lista=True)
        self.RegistrarRuta("/<int:id>", "buscar", self.BuscarPorId, "GET", "Buscar por ID")
        self.RegistrarRuta("", "insertar", self.Insertar, "POST", "Registrar", cuerpo="entidad")
        self.RegistrarRuta("/<int:id>", "actualizar", self.Actualizar, "PUT",
                           "Actualizar (solo los campos enviados)", cuerpo="entidad")
        self.RegistrarRuta("/<int:id>", "eliminar", self.Eliminar, "DELETE", "Eliminar", respuesta="texto")

    def RegistrarRuta(self, ruta: str, endpoint: str, funcion, metodo: str, resumen: str,
                      parametros: list | None = None, cuerpo=None, lista: bool = False,
                      respuesta: str = "entidad") -> None:
        """Registra la ruta en el Blueprint y guarda sus datos para el Swagger.
        cuerpo: None, "entidad" o un esquema OpenAPI; respuesta: "entidad" o "texto"."""
        self.blueprint.add_url_rule(ruta, endpoint, Responder(funcion), methods=[metodo])
        self.documentacion.append({"ruta": ruta, "metodo": metodo, "resumen": resumen,
                                   "parametros": parametros or [], "cuerpo": cuerpo,
                                   "lista": lista, "respuesta": respuesta})

    # --- Conversión ---

    def AJson(self, entidad) -> dict:
        return {campo: ValorJson(valor) for campo, valor in entidad.ADiccionario().items()
                if campo not in self.ocultos}

    def ListaJson(self, entidades: list) -> list:
        return [self.AJson(entidad) for entidad in entidades]

    def AplicarDatos(self, entidad, datos: dict) -> None:
        """Copia en la entidad los campos conocidos del JSON, convertidos a su tipo."""
        valores = {campo: ConvertirValor(campo, valor, self.tipos.get(campo, str))
                   for campo, valor in datos.items() if campo in entidad.Campos and campo != "id"}
        entidad.DesdeDiccionario(valores)

    def PrepararDatos(self, datos: dict, nuevo: bool) -> None:
        """Gancho para que un controlador ajuste el JSON antes de aplicarlo (ej. contraseñas)."""

    def Obtener(self, id: int):
        entidad = self.aplicacion.BuscarPorId(id)
        if entidad is None:
            raise NoEncontrado(f"No existe un registro de {self.nombre} con ID {id}.")
        return entidad

    # --- Rutas CRUD ---

    def Consultar(self):
        if self.filtro:
            return Respuesta(self.ListaJson(self.aplicacion.Consultar(LeerEnteroQuery(self.filtro))))
        return Respuesta(self.ListaJson(self.aplicacion.Consultar()))

    def BuscarPorId(self, id: int):
        return Respuesta(self.AJson(self.Obtener(id)))

    def Insertar(self):
        datos = LeerJson()
        self.PrepararDatos(datos, nuevo=True)
        entidad = self.clase()
        self.AplicarDatos(entidad, datos)
        entidad = self.aplicacion.Insertar(entidad)
        # Se vuelve a leer para devolver también los campos calculados (nombres, totales...)
        guardada = self.aplicacion.BuscarPorId(entidad.GetId()) or entidad
        return Respuesta(self.AJson(guardada), 201)

    def Actualizar(self, id: int):
        datos = LeerJson()
        self.PrepararDatos(datos, nuevo=False)
        entidad = self.Obtener(id)        # se parte del registro actual: PUT parcial
        self.AplicarDatos(entidad, datos)
        entidad.SetId(id)
        self.aplicacion.Actualizar(entidad)
        return Respuesta(self.AJson(self.aplicacion.BuscarPorId(id) or entidad))

    def Eliminar(self, id: int):
        self.Obtener(id)
        self.aplicacion.Eliminar(id)
        return Respuesta(f"Registro {id} de {self.nombre} eliminado.")
