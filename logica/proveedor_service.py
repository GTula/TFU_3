from persistencia.proveedor_repo import ProveedorRepo

class ProveedorService:
    def __init__(self):
        self.repo = ProveedorRepo()

    def listarProveedores(self):
        return self.repo.findAll()

    def obtenerProveedor(self, proveedor_id):
        return self.repo.findById(proveedor_id)

    def agregarProveedor(self, proveedor_data):
        return self.repo.save(proveedor_data)

    def actualizarProveedor(self, proveedor_id, proveedor_data):
        return self.repo.update(proveedor_id, proveedor_data)

    def eliminarProveedor(self, proveedor_id):
        return self.repo.delete(proveedor_id)