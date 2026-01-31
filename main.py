from fastapi import FastAPI
from threading import Thread
import time

from pick_worker import pick_and_place_worker, state

app = FastAPI()

worker_thread = None


@app.on_event("startup")
def start_worker():
    global worker_thread

    print("[Main] Starting background worker thread")

    worker_thread = Thread(
        target=pick_and_place_worker,
        daemon=True
    )
    worker_thread.start()


@app.post("/start_orders")
def start_orders(data: dict):
    state["current_user"] = data.get("user")
    state["total_orders"] = data.get("total_orders", 0)
    state["dispatched_orders"] = 0
    state["stored_objects"] = 0
    state["picking"] = True

    print("[API] Orders started")
    return {"status": "started"}


@app.get("/status")
def get_status():
    return state
