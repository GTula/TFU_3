from models.client import Client

clients_db = {}

def get_all_clients():
    return list(clients_db.values())

def get_client(client_id: int):
    return clients_db.get(client_id)

def add_client(client: Client):
    clients_db[client.id] = client
    return client

def update_client(client_id: int, client: Client):
    clients_db[client_id] = client
    return client

def delete_client(client_id: int):
    return clients_db.pop(client_id, None)