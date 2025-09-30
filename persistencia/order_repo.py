from persistencia.db import get_conn

class OrdenRepo:
    def save(self, orden_data):
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO orders (client_id) VALUES (%s) RETURNING id",
                (orden_data["client_id"],)
            )
            orden_id = cur.fetchone()["id"]
            for item in orden_data["items"]:
                cur.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s, %s, %s)",
                    (orden_id, item["product_id"], item["quantity"])
                )
                cur.execute(
                    "UPDATE products SET stock = stock - %s WHERE id = %s",
                    (item["quantity"], item["product_id"])
                )
            conn.commit()
            return {"id": orden_id, "client_id": orden_data["client_id"], "items": orden_data["items"]}

    def findById(self, orden_id):
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM orders WHERE id = %s", (orden_id,))
            orden = cur.fetchone()
            if orden:
                cur.execute("SELECT * FROM order_items WHERE order_id = %s", (orden_id,))
                orden["items"] = cur.fetchall()
            return orden

    def findAll(self):
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM orders")
            orders = cur.fetchall()
            for order in orders:
                cur.execute("SELECT * FROM order_items WHERE order_id = %s", (order["id"],))
                order["items"] = cur.fetchall()
            return orders