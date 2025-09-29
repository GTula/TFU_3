from persistencia.product_repo import (
    get_all_products, get_product, add_product, update_product, delete_product
)
from models.product import Product

def listar_productos():
    return get_all_products()

def obtener_producto(product_id: int):
    return get_product(product_id)

def crear_producto(product: Product):
    return add_product(product)

def actualizar_producto(product_id: int, product: Product):
    return update_product(product_id, product)

def eliminar_producto(product_id: int):
    return delete_product(product_id)