from persistencia.db import get_conn

def listar_clientes():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM clients")
        return cur.fetchall()

def obtener_cliente(client_id):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM clients WHERE id = %s", (client_id,))
        return cur.fetchone()

def crear_cliente(client):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO clients (name, email) VALUES (%s, %s) RETURNING *",
            (client["name"], client["email"])
        )
        conn.commit()
        return cur.fetchone()