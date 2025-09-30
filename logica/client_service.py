from persistencia.client_repo import ClienteRepo

class ClienteService:
    def __init__(self):
        self.repo = ClienteRepo()

    def registrarCliente(self, cliente_data):
        return self.repo.save(cliente_data)

    def loginCliente(self, email, password):
        return self.repo.login(email, password)

    def actualizarCliente(self, cliente_id, cliente_data):
        return self.repo.update(cliente_id, cliente_data)

    def obtenerCliente(self, cliente_id):
        return self.repo.findById(cliente_id)