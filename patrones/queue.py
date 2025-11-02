import os
import json
import pika
from typing import Callable

RABBIT_URL = os.getenv("RABBITMQ_URL") or os.getenv("RABBIT_URL") or "amqp://user:pass@rabbitmq:5672/"
ORDER_QUEUE = os.getenv("ORDER_QUEUE", "orders")
PUBLISHER_HEARTBEAT = int(os.getenv("RABBIT_HEARTBEAT", "600"))

def _connect():
    """Crea una conexión blocking a RabbitMQ."""
    params = pika.URLParameters(RABBIT_URL)
    params.heartbeat = PUBLISHER_HEARTBEAT
    return pika.BlockingConnection(params)

def publish_order(order_id: int, payload: dict = None):

    conn = _connect()
    ch = conn.channel()
    ch.queue_declare(queue=ORDER_QUEUE, durable=True)
    body = json.dumps({"order_id": order_id, "payload": payload or {}})
    ch.basic_publish(
        exchange='',
        routing_key=ORDER_QUEUE,
        body=body,
        properties=pika.BasicProperties(delivery_mode=2)  # mensaje persistente
    )
    conn.close()

def consume_orders(on_message: Callable[[dict], bool], prefetch: int = 1):

    conn = _connect()
    ch = conn.channel()
    ch.queue_declare(queue=ORDER_QUEUE, durable=True)
    ch.basic_qos(prefetch_count=prefetch)

    def _callback(ch, method, properties, body):
        try:
            payload = json.loads(body)
        except Exception:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print("[ERROR] mensaje en cola con payload inválido. Ack y descartar.")
            return

        try:
            ok = on_message(payload)
            if ok:
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
              
                ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:

            print(f"[ERROR] excepción procesando mensaje de orden: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    ch.basic_consume(queue=ORDER_QUEUE, on_message_callback=_callback, auto_ack=False)
    print("Consumidor de órdenes iniciado. Esperando mensajes...")
    try:
        ch.start_consuming()
    finally:
        try:
            ch.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass