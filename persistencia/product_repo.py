from persistencia.db import get_conn

def listar_productos():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM products")
        return cur.fetchall()

def obtener_producto(product_id):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        return cur.fetchone()

def crear_producto(product):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO products (name, price, stock) VALUES (%s, %s, %s) RETURNING *",
            (product["name"], product["price"], product["stock"])
        )
        conn.commit()
        return cur.fetchone()