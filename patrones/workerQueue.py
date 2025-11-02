"""
Ejemplo de worker que usa infraestructura/order_queue.publish_order/consume_orders.

Ejecuta:
    python worker/order_worker.py
"""
import time
from queue import consume_orders
from persistencia.order_repo import OrdenRepo

repo = OrdenRepo()

def handle_order_message(msg: dict) -> bool:
   
    order_id = msg.get("order_id")
    if not order_id:
        print("[WARN] mensaje sin order_id")
        return True  # ack y descartar

    print(f"[WORKER] procesando orden {order_id}")
    order = repo.findById(order_id)
    if not order:
        print(f"[WARN] orden {order_id} no encontrada en BD")
        return True

    if order.get("status") == "completed":
        print(f"[WORKER] orden {order_id} ya completada")
        return True

    try:
        time.sleep(1)
        try:
            repo.update_status(order_id, "completed")
        except Exception:
            print("[INFO] update_status no implementado en repo; omitiendo actualización")
        print(f"[WORKER] orden {order_id} procesada OK")
        return True
    except Exception as e:
        print(f"[ERROR] fallo procesando orden {order_id}: {e}")
        return False

if __name__ == "__main__":
    consume_orders(handle_order_message, prefetch=1)