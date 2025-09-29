from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from persistencia.database import get_db, Base, engine
from logica.product_service import listar_productos, obtener_producto, crear_producto, actualizar_producto, eliminar_producto
from logica.client_service import listar_clientes, obtener_cliente, crear_cliente, actualizar_cliente, eliminar_cliente
from logica.order_service import listar_ordenes, obtener_orden, crear_orden, eliminar_orden

Base.metadata.create_all(bind=engine)
app = FastAPI()

# Productos
@app.get("/productos")
def get_productos(db: Session = Depends(get_db)):
    return listar_productos(db)

@app.get("/productos/{product_id}")
def get_producto(product_id: int, db: Session = Depends(get_db)):
    producto = obtener_producto(db, product_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@app.post("/productos")
def post_producto(product_data: dict, db: Session = Depends(get_db)):
    return crear_producto(db, product_data)

@app.put("/productos/{product_id}")
def put_producto(product_id: int, product_data: dict, db: Session = Depends(get_db)):
    producto = actualizar_producto(db, product_id, product_data)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@app.delete("/productos/{product_id}")
def delete_producto(product_id: int, db: Session = Depends(get_db)):
    producto = eliminar_producto(db, product_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

# Clientes
@app.get("/clientes")
def get_clientes(db: Session = Depends(get_db)):
    return listar_clientes(db)

@app.get("/clientes/{client_id}")
def get_cliente(client_id: int, db: Session = Depends(get_db)):
    cliente = obtener_cliente(db, client_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

@app.post("/clientes")
def post_cliente(client_data: dict, db: Session = Depends(get_db)):
    return crear_cliente(db, client_data)

@app.put("/clientes/{client_id}")
def put_cliente(client_id: int, client_data: dict, db: Session = Depends(get_db)):
    cliente = actualizar_cliente(db, client_id, client_data)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

@app.delete("/clientes/{client_id}")
def delete_cliente(client_id: int, db: Session = Depends(get_db)):
    cliente = eliminar_cliente(db, client_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

# Órdenes
@app.get("/ordenes")
def get_ordenes(db: Session = Depends(get_db)):
    return listar_ordenes(db)

@app.get("/ordenes/{order_id}")
def get_orden(order_id: int, db: Session = Depends(get_db)):
    orden = obtener_orden(db, order_id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return orden

@app.post("/ordenes")
def post_orden(order_data: dict, db: Session = Depends(get_db)):
    return crear_orden(db, order_data)

@app.delete("/ordenes/{order_id}")
def delete_orden(order_id: int, db: Session = Depends(get_db)):
    orden = eliminar_orden(db, order_id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return orden