from persistencia.product_repo import ProductoRepo
from patrones.bulkhead import BulkheadManager
import logging

logger = logging.getLogger(__name__)


class ProductoService:
    def __init__(self):
        self.repo = ProductoRepo()
        # con la instancia de BulkheadManager, se crean recursos que serán llamados desde afuera
        # internamente implementan bulkhead y llaman al metodo interno que se encarga
        # de realizar la logica del servicio, pero que, en caso de sobrecarga,
        # no afectarán a otros servicios :)
        self.bulkhead = BulkheadManager().get_bulkhead("productos")

    # listar productos con bulkhead
    def listarProductos(self):
        logger.info("Listando productos con protección Bulkhead")
        return self.bulkhead.execute(self._listar_productos_interno)
    
    def _listar_productos_interno(self):
        """Método interno que ejecuta la lógica real"""
        return self.repo.findAll()

    # obtener producto con bulkhead
    def obtenerProducto(self, producto_id):
        logger.info(f"Obteniendo producto {producto_id} con protección Bulkhead")
        return self.bulkhead.execute(self._obtener_producto_interno, producto_id)
    
    def _obtener_producto_interno(self, producto_id):
        return self.repo.findById(producto_id)

    # agregar producto con bulkhead
    def agregarProducto(self, producto_data):
        logger.info("Agregando producto con protección Bulkhead")
        return self.bulkhead.execute(self._agregar_producto_interno, producto_data)
    
    def _agregar_producto_interno(self, producto_data):
        return self.repo.save(producto_data)

    # update de producto con bulkhead
    def actualizarProducto(self, producto_id, producto_data):
        logger.info(f"Actualizando producto {producto_id} con protección Bulkhead")
        return self.bulkhead.execute(
            self._actualizar_producto_interno, producto_id, producto_data
        )
    
    def _actualizar_producto_interno(self, producto_id, producto_data):
        return self.repo.update(producto_id, producto_data)

    # eliminar producto con bulkhead
    def eliminarProducto(self, producto_id):
        logger.info(f"Eliminando producto {producto_id} con protección Bulkhead")
        return self.bulkhead.execute(self._eliminar_producto_interno, producto_id)
    
    def _eliminar_producto_interno(self, producto_id):
        return self.repo.delete(producto_id)