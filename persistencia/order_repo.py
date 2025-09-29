from models.order import Order, OrderItem
from models.product import Product
from sqlalchemy.orm import Session

def get_all_orders(db: Session):
    return db.query(Order).all()

def get_order(db: Session, order_id: int):
    return db.query(Order).filter(Order.id == order_id).first()

def add_order(db: Session, order: Order, items: list):
    db.add(order)
    db.commit()
    db.refresh(order)
    for item in items:
        order_item = OrderItem(order_id=order.id, product_id=item['product_id'], quantity=item['quantity'])
        db.add(order_item)
        # Descontar stock
        product = db.query(Product).filter(Product.id == item['product_id']).first()
        if product:
            product.stock -= item['quantity']
            db.commit()
    db.commit()
    return order

def delete_order(db: Session, order_id: int):
    order = get_order(db, order_id)
    if order:
        db.delete(order)
        db.commit()
    return order