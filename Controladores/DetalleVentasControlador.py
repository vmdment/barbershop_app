from Aplicaciones import DetalleVentasAplicacion
from Controladores.ControladorBase import ControladorBase
from Entidades import DetalleVentas

controlador = ControladorBase("detalle-ventas", DetalleVentas.DetalleVentas, DetalleVentasAplicacion.DetalleVentasAplicacion(), filtro="product_sale_id")
blueprint = controlador.blueprint
