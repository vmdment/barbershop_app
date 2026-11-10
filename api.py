"""Punto de entrada de la API REST (Flask). La consola sigue siendo main.py.

    py api.py          ->  http://localhost:4040        (aplicación web, carpeta Front/)
    API                ->  http://localhost:4040/api
    Swagger            ->  http://localhost:4040/api/docs
"""
import atexit
import mimetypes

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


# En Windows el registro puede asociar .js a text/plain y el navegador rechaza los módulos
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("text/css", ".css")


def CrearApp() -> flask.Flask:
    # La carpeta Front/ (HTML, CSS y JS de la aplicación web) se sirve desde la raíz del sitio
    app = flask.Flask(__name__, static_folder="Front", static_url_path="")
    app.json.ensure_ascii = False   # tildes y ñ legibles en las respuestas
    app.json.sort_keys = False      # respeta el orden de los campos de cada entidad

    for modulo in CONTROLADORES:
        app.register_blueprint(modulo.blueprint)
    app.register_blueprint(SwaggerControlador.CrearBlueprint([m.controlador for m in CONTROLADORES]))

    @app.get("/")
    def Inicio():
        return app.send_static_file("index.html")

    @app.get("/api")
    def Rutas():
        """Lista todas las rutas disponibles."""
        rutas = sorted(
            f"{' '.join(sorted(regla.methods - {'HEAD', 'OPTIONS'}))} {regla.rule}"
            for regla in app.url_map.iter_rules() if regla.rule.startswith("/api")
        )
        return flask.jsonify({"Respuesta": rutas})

    @app.errorhandler(404)
    def NoEncontrada(_):
        if not flask.request.path.startswith("/api"):
            return "Página no encontrada.", 404
        return flask.jsonify({"Error": "Ruta no encontrada. Consulte GET /api."}), 404

    @app.errorhandler(405)
    def MetodoNoPermitido(_):
        return flask.jsonify({"Error": "Método HTTP no permitido en esta ruta."}), 405

    atexit.register(Conexion.conexion.closeConnection)
    return app


app = CrearApp()

if __name__ == "__main__":
    app.run("localhost", 4040)
