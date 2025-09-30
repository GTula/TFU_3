from persistencia.db import get_conn

class ProveedorRepo:
    def findAll(self):
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM proveedores")
            return cur.fetchall()

    def findById(self, proveedor_id):
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM proveedores WHERE id = %s", (proveedor_id,))
            return cur.fetchone()

    def save(self, proveedor_data):
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO proveedores (nombre, contacto, email) VALUES (%s, %s, %s) RETURNING *",
                (proveedor_data["nombre"], proveedor_data["contacto"], proveedor_data["email"])
            )
            conn.commit()
            return cur.fetchone()

    def update(self, proveedor_id, proveedor_data):
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "UPDATE proveedores SET nombre=%s, contacto=%s, email=%s WHERE id=%s RETURNING *",
                (proveedor_data["nombre"], proveedor_data["contacto"], proveedor_data["email"], proveedor_id)
            )
            conn.commit()
            return cur.fetchone()

    def delete(self, proveedor_id):
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM proveedores WHERE id=%s RETURNING id", (proveedor_id,))
            conn.commit()
            return cur.fetchone()