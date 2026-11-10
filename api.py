"""Punto de entrada de la API REST (Flask). La consola sigue siendo main.py.

    py api.py          ->  http://localhost:4040/api
    Swagger            ->  http://localhost:4040/api/docs
"""
import atexit

import flask

from Controladores import (BarberiasControlador, BarberosControlador, BloqueosControlador, CitasControlador,
                           ComprasControlador, DetalleVentasControlador, HorariosControlador,
                           ProductosControlador, ProveedoresControlador, RolesControlador,
                           ServiciosBarberoControlador, ServiciosCitaControlador, ServiciosControlador,
                           SwaggerControlador, UsuariosControlador, VentasControlador)
from Utilidades import Conexion

CONTROLADORES = [
    RolesControlador, UsuariosControlador, BarberiasControlador, BarberosControlador,
    HorariosControlador, BloqueosControlador, ServiciosControlador, ServiciosBarberoControlador,
    CitasControlador, ServiciosCitaControlador, ProductosControlador, VentasControlador,
    DetalleVentasControlador, ProveedoresControlador, ComprasControlador,
]


def CrearApp() -> flask.Flask:
    app = flask.Flask(__name__)
    app.json.ensure_ascii = False   # tildes y ñ legibles en las respuestas
    app.json.sort_keys = False      # respeta el orden de los campos de cada entidad

    for modulo in CONTROLADORES:
        app.register_blueprint(modulo.blueprint)
    app.register_blueprint(SwaggerControlador.CrearBlueprint([m.controlador for m in CONTROLADORES]))

    @app.get("/api")
    def Rutas():
        """Lista todas las rutas disponibles."""
        rutas = sorted(
            f"{' '.join(sorted(regla.methods - {'HEAD', 'OPTIONS'}))} {regla.rule}"
            for regla in app.url_map.iter_rules() if regla.endpoint != "static"
        )
        return flask.jsonify({"Respuesta": rutas})

    @app.errorhandler(404)
    def NoEncontrada(_):
        return flask.jsonify({"Error": "Ruta no encontrada. Consulte GET /api."}), 404

    @app.errorhandler(405)
    def MetodoNoPermitido(_):
        return flask.jsonify({"Error": "Método HTTP no permitido en esta ruta."}), 405

    atexit.register(Conexion.conexion.closeConnection)
    return app


app = CrearApp()

if __name__ == "__main__":
    app.run("localhost", 4040)
