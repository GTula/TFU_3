import psycopg2
from psycopg2.extras import RealDictCursor
from infraestructura.config_store import cfg

DATABASE_URL = cfg.get("DATABASE_URL", default="postgresql://user:pass@db:5432/ecommerce")

def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)