from persistencia.product_repo import ProductoRepo

class ProductoService:
    def __init__(self):
        self.repo = ProductoRepo()

    def listarProductos(self):
        return self.repo.findAll()

    def obtenerProducto(self, producto_id):
        return self.repo.findById(producto_id)

    def agregarProducto(self, producto_data):
        return self.repo.save(producto_data)

    def actualizarProducto(self, producto_id, producto_data):
        return self.repo.update(producto_id, producto_data)

    def eliminarProducto(self, producto_id):
        return self.repo.delete(producto_id)