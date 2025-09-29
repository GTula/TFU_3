from models.product import Product
from persistencia.product_repo import (
    get_all_products, get_product, add_product, update_product, delete_product
)
from sqlalchemy.orm import Session

def listar_productos(db: Session):
    return get_all_products(db)

def obtener_producto(db: Session, product_id: int):
    return get_product(db, product_id)

def crear_producto(db: Session, product_data: dict):
    product = Product(**product_data)
    return add_product(db, product)

def actualizar_producto(db: Session, product_id: int, data: dict):
    return update_product(db, product_id, data)

def eliminar_producto(db: Session, product_id: int):
    return delete_product(db, product_id)