from fastapi import FastAPI
from models.product import Product
from models.client import Client
from models.order import Order

from logica.product_service import (
    listar_productos, obtener_producto, crear_producto, actualizar_producto, eliminar_producto
)
from logica.client_service import (
    listar_clientes, obtener_cliente, crear_cliente, actualizar_cliente, eliminar_cliente
)
from logica.order_service import (
    listar_ordenes, obtener_orden, crear_orden, actualizar_orden, eliminar_orden
)

app = FastAPI()

# Productos
@app.get("/productos")
def get_productos():
    return listar_productos()

@app.get("/productos/{product_id}")
def get_producto(product_id: int):
    return obtener_producto(product_id)

@app.post("/productos")
def post_producto(product: Product):
    return crear_producto(product)

@app.put("/productos/{product_id}")
def put_producto(product_id: int, product: Product):
    return actualizar_producto(product_id, product)

@app.delete("/productos/{product_id}")
def delete_producto(product_id: int):
    return eliminar_producto(product_id)

# Clientes
@app.get("/clientes")
def get_clientes():
    return listar_clientes()

@app.get("/clientes/{client_id}")
def get_cliente(client_id: int):
    return obtener_cliente(client_id)

@app.post("/clientes")
def post_cliente(client: Client):
    return crear_cliente(client)

@app.put("/clientes/{client_id}")
def put_cliente(client_id: int, client: Client):
    return actualizar_cliente(client_id, client)

@app.delete("/clientes/{client_id}")
def delete_cliente(client_id: int):
    return eliminar_cliente(client_id)

# Ordenes
@app.get("/ordenes")
def get_ordenes():
    return listar_ordenes()

@app.get("/ordenes/{order_id}")
def get_orden(order_id: int):
    return obtener_orden(order_id)

@app.post("/ordenes")
def post_orden(order: Order):
    return crear_orden(order)

@app.put("/ordenes/{order_id}")
def put_orden(order_id: int, order: Order):
    return actualizar_orden(order_id, order)

@app.delete("/ordenes/{order_id}")
def delete_orden(order_id: int):
    return eliminar_orden(order_id)