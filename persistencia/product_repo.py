from persistencia.db import get_conn

class ProductoRepo:
    def findAll(self):
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM products")
            return cur.fetchall()

    def findById(self, producto_id):
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM products WHERE id = %s", (producto_id,))
            return cur.fetchone()

    def save(self, producto_data):
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO products (name, price, stock) VALUES (%s, %s, %s) RETURNING *",
                (producto_data["name"], producto_data["price"], producto_data["stock"])
            )
            conn.commit()
            return cur.fetchone()

    def update(self, producto_id, producto_data):
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "UPDATE products SET name=%s, price=%s, stock=%s WHERE id=%s RETURNING *",
                (producto_data["name"], producto_data["price"], producto_data["stock"], producto_id)
            )
            conn.commit()
            return cur.fetchone()

    def delete(self, producto_id):
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM products WHERE id=%s RETURNING id", (producto_id,))
            conn.commit()
            return cur.fetchone()