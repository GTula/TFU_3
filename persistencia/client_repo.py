from persistencia.db import get_conn

class ClienteRepo:
    def save(self, cliente_data):
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO clients (name, email, password) VALUES (%s, %s, %s) RETURNING *",
                (cliente_data["name"], cliente_data["email"], cliente_data["password"])
            )
            conn.commit()
            return cur.fetchone()

    def login(self, email, password):
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM clients WHERE email = %s AND password = %s",
                (email, password)
            )
            return cur.fetchone()

    def update(self, cliente_id, cliente_data):
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "UPDATE clients SET name = %s, email = %s, password = %s WHERE id = %s RETURNING *",
                (cliente_data["name"], cliente_data["email"], cliente_data["password"], cliente_id)
            )
            conn.commit()
            return cur.fetchone()

    def findById(self, cliente_id):
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM clients WHERE id = %s", (cliente_id,))
            return cur.fetchone()