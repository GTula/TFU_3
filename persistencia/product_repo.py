from models.product import Product

products_db = {}

def get_all_products():
    return list(products_db.values())

def get_product(product_id: int):
    return products_db.get(product_id)

def add_product(product: Product):
    products_db[product.id] = product
    return product

def update_product(product_id: int, product: Product):
    products_db[product_id] = product
    return product

def delete_product(product_id: int):
    return products_db.pop(product_id, None)