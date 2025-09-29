from persistencia.db import get_conn

def listar_ordenes():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM orders")
        orders = cur.fetchall()
        for order in orders:
            cur.execute("SELECT * FROM order_items WHERE order_id = %s", (order["id"],))
            order["items"] = cur.fetchall()
        return orders

def obtener_orden(order_id):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
        ord = cur.fetchone()
        if ord:
            cur.execute("SELECT * FROM order_items WHERE order_id = %s", (order_id,))
            ord["items"] = cur.fetchall()
        return ord

def crear_orden(order):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM clients WHERE id = %s", (order["client_id"],))
        if not cur.fetchone():
            return None
        cur.execute("INSERT INTO orders (client_id) VALUES (%s) RETURNING id", (order["client_id"],))
        order_id = cur.fetchone()["id"]
        for item in order["items"]:
            cur.execute("SELECT * FROM products WHERE id = %s", (item["product_id"],))
            prod = cur.fetchone()
            if not prod or prod["stock"] < item["quantity"]:
                return None
            cur.execute(
                "INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s, %s, %s)",
                (order_id, item["product_id"], item["quantity"])
            )
            cur.execute(
                "UPDATE products SET stock = stock - %s WHERE id = %s",
                (item["quantity"], item["product_id"])
            )
        conn.commit()
        return {"id": order_id, "client_id": order["client_id"], "items": order["items"]}