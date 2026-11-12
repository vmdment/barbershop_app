"""Documentación Swagger (OpenAPI 3) generada a partir de los controladores.

    GET /api/docs           Interfaz de Swagger UI para probar la API desde el navegador
    GET /api/openapi.json   Especificación OpenAPI

El esquema de cada entidad sale de sus `Campos` y de los tipos declarados en la clase,
y las rutas de lo que cada controlador registró con RegistrarRuta(); no hay que editar
este archivo al agregar una entidad o una ruta.
"""
import re
from datetime import date, datetime, time
from decimal import Decimal

import flask

TIPOS_OPENAPI = {
    int: {"type": "integer"},
    Decimal: {"type": "number", "format": "double", "example": 15000.00},
    str: {"type": "string"},
    date: {"type": "string", "format": "date", "example": "2026-12-31"},
    time: {"type": "string", "pattern": "^\\d{2}:\\d{2}(:\\d{2})?$", "example": "14:30"},
    datetime: {"type": "string", "format": "date-time", "example": "2026-12-31 14:30"},
}

SWAGGER_UI = """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Barbershop API - Swagger</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.14/swagger-ui.css">
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.14/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({ url: "/api/openapi.json", dom_id: "#swagger-ui", docExpansion: "none",
                      tryItOutEnabled: true, displayRequestDuration: true });
  </script>
</body>
</html>"""


def NombreEsquema(controlador) -> str:
    return controlador.clase.__name__


def EsquemaEntidad(controlador) -> dict:
    propiedades = {}
    for campo in controlador.clase.Campos:
        if campo in controlador.ocultos:
            continue
        propiedad = dict(TIPOS_OPENAPI.get(controlador.tipos.get(campo, str), {"type": "string"}))
        if campo == "id":
            propiedad["readOnly"] = True
        propiedad["nullable"] = True
        propiedades[campo] = propiedad
    propiedades.update(getattr(controlador, "extrasEsquema", {}))
    return {"type": "object", "properties": propiedades}


def Envolver(esquema: dict) -> dict:
    return {"type": "object", "properties": {"Respuesta": esquema}}


def Operacion(controlador, ruta: dict) -> dict:
    ref = {"$ref": f"#/components/schemas/{NombreEsquema(controlador)}"}
    parametros = [{"name": nombre, "in": "path", "required": True, "schema": {"type": "integer"}}
                  for nombre in re.findall(r"<int:(\w+)>", ruta["ruta"])]
    parametros += [{"name": p["nombre"], "in": p["en"], "required": True, "schema": {"type": "integer"},
                    "description": f"ID requerido para listar ({p['nombre']})"}
                   for p in ruta["parametros"]]

    if isinstance(ruta["respuesta"], dict):
        exito = ruta["respuesta"]
    elif ruta["respuesta"] == "texto":
        exito = {"type": "string"}
    else:
        exito = {"type": "array", "items": ref} if ruta["lista"] else ref
    codigo = "201" if ruta["metodo"] == "POST" else "200"
    error = {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}

    operacion = {
        "tags": [controlador.nombre],
        "summary": ruta["resumen"],
        "description": ("Pública: no requiere iniciar sesión." if ruta.get("roles") is None
                        else "Roles: " + ", ".join(ruta["roles"])),
        "operationId": f"{controlador.nombre}_{ruta['metodo'].lower()}_{ruta['ruta']}",
        "parameters": parametros,
        "responses": {
            codigo: {"description": "Correcto",
                     "content": {"application/json": {"schema": Envolver(exito)}}},
            "400": {"description": "Datos inválidos o regla de negocio incumplida", **error},
            "401": {"description": "Sin sesión, token inválido o vencido", **error},
            "403": {"description": "El rol no tiene permiso o el registro no es suyo", **error},
            "404": {"description": "El registro no existe", **error},
            "409": {"description": "Error de la base de datos", **error},
            "500": {"description": "Error interno", **error},
        },
    }
    if ruta.get("roles") is None:
        operacion["security"] = []      # ruta pública
    if ruta["cuerpo"] is not None:
        esquema = ref if ruta["cuerpo"] == "entidad" else ruta["cuerpo"]
        operacion["requestBody"] = {"required": True, "content": {"application/json": {"schema": esquema}}}
    return operacion


def GenerarEspecificacion(controladores: list) -> dict:
    rutas: dict = {}
    esquemas: dict = {"Error": {"type": "object", "properties": {"Error": {"type": "string"}}}}
    for controlador in controladores:
        esquemas[NombreEsquema(controlador)] = EsquemaEntidad(controlador)
        for ruta in controlador.documentacion:
            url = re.sub(r"<int:(\w+)>", r"{\1}", f"/api/{controlador.nombre}{ruta['ruta']}")
            rutas.setdefault(url, {})[ruta["metodo"].lower()] = Operacion(controlador, ruta)
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Barbershop API",
            "version": "1.0.0",
            "description": "API REST de la barbería. Todas las respuestas tienen la forma "
                           "`{\"Respuesta\": ...}` o `{\"Error\": \"...\"}`. Fechas `AAAA-MM-DD`, "
                           "horas `HH:MM`, fecha y hora `AAAA-MM-DD HH:MM`. En `PUT` solo se envían "
                           "los campos a cambiar.\n\n**Inicio de sesión:** use `POST /api/auth/login`, "
                           "copie el `token` y péguelo en el botón **Authorize**. Roles: Administrador "
                           "(todo), Barbero (sus citas y ventas) y Cliente (pide y cancela sus citas).",
        },
        "servers": [{"url": "/"}],
        "tags": [{"name": c.nombre} for c in controladores],
        "paths": rutas,
        "security": [{"bearerAuth": []}],
        "components": {"schemas": esquemas,
                       "securitySchemes": {"bearerAuth": {"type": "http", "scheme": "bearer"}}},
    }


def CrearBlueprint(controladores: list) -> flask.Blueprint:
    blueprint = flask.Blueprint("swagger", __name__, url_prefix="/api")
    especificacion = GenerarEspecificacion(controladores)

    @blueprint.get("/openapi.json")
    def Especificacion():
        return flask.jsonify(especificacion)

    @blueprint.get("/docs")
    def Documentacion():
        return SWAGGER_UI

    return blueprint
