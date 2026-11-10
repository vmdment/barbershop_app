from Aplicaciones import ProductosAplicacion
from Controladores.ControladorBase import ControladorBase, Respuesta
from Entidades import Productos


class ProductosControlador(ControladorBase):

    def __init__(self):
        super().__init__("productos", Productos.Productos, ProductosAplicacion.ProductosAplicacion())
        self.RegistrarRuta("/disponibles", "disponibles", self.ConsultarDisponibles, "GET",
                           "Productos con stock disponible", lista=True)
        self.RegistrarRuta("/stock-bajo", "stock_bajo", self.ConsultarStockBajo, "GET",
                           "Productos con stock bajo el mínimo", lista=True)

    def ConsultarDisponibles(self):
        return Respuesta(self.ListaJson(self.aplicacion.ConsultarDisponibles()))

    def ConsultarStockBajo(self):
        return Respuesta(self.ListaJson(self.aplicacion.ConsultarStockBajo()))


controlador = ProductosControlador()
blueprint = controlador.blueprint
