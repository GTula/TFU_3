import os
import requests

CONSUL = os.getenv("CONSUL_HOST", "localhost")
PORT = os.getenv("CONSUL_PORT", "8500")
BASE = f"http://{CONSUL}:{PORT}/v1/kv"

# Ejemplos
DEFAULTS = {
    "DATABASE_URL": "postgresql://user:pass@db:5432/ecommerce",
    "RABBITMQ_URL": "amqp://user:pass@rabbitmq:5672/",
    "ORDER_QUEUE": "orders",
    "BULKHEAD_PRODUCTOS_WORKERS": "5",
    "BULKHEAD_PRODUCTOS_TIMEOUT": "30",
    "BULKHEAD_CLIENTES_WORKERS": "5",
    "BULKHEAD_ORDENES_WORKERS": "3",
}


def put(key, value):
    url = f"{BASE}/{key}"
    r = requests.put(url, data=str(value))
    return r.ok


if __name__ == '__main__':
    for k, v in DEFAULTS.items():
        ok = put(k, v)
        print(k, v, ok)
