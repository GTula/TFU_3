import psycopg2
from psycopg2.extras import RealDictCursor
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/ecommerce")

def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)