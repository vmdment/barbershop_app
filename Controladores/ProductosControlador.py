from Aplicaciones import ProductosAplicacion
from Controladores import Permisos
from Controladores.ComprasControlador import EnAlcance
from Controladores.ControladorBase import ControladorBase, Respuesta
from Entidades import Productos

# El barbero consulta los productos para venderlos; solo el administrador maneja el inventario
VENDEDORES = (Permisos.ADMIN, Permisos.BARBERO)


class ProductosControlador(ControladorBase):

    def __init__(self):
        super().__init__("productos", Productos.Productos, ProductosAplicacion.ProductosAplicacion(),
                         leer=VENDEDORES, alcance=EnAlcance)   # misma regla: barbería y barbero dueños
        self.RegistrarRuta("/disponibles", "disponibles", self.ConsultarDisponibles, "GET",
                           "Productos con stock disponible", lista=True, roles=VENDEDORES)
        self.RegistrarRuta("/stock-bajo", "stock_bajo", self.ConsultarStockBajo, "GET",
                           "Productos con stock bajo el mínimo", lista=True, roles=VENDEDORES)

    def ConsultarDisponibles(self):
        return Respuesta(self.ListaJson(self.FiltrarLista(self.aplicacion.ConsultarDisponibles())))

    def ConsultarStockBajo(self):
        return Respuesta(self.ListaJson(self.FiltrarLista(self.aplicacion.ConsultarStockBajo())))


controlador = ProductosControlador()
blueprint = controlador.blueprint
