from persistencia.order_repo import OrdenRepo

class OrdenService:
    def __init__(self):
        self.repo = OrdenRepo()

    def crearOrden(self, orden_data):
        return self.repo.save(orden_data)

    def obtenerOrden(self, orden_id):
        return self.repo.findById(orden_id)

    def listarOrdenes(self):
        return self.repo.findAll()