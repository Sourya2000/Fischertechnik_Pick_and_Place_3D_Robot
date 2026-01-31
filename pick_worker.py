import time
import cv2
from ultralytics import YOLO

from motor_config import (
    select_motor,
    run_motor_forward,
    run_motor_backward,
    stop_motor,
    stop_all,
    magnet_on,
    magnet_off
)

state = {
    "total_orders": 0,
    "dispatched_orders": 0,
    "stored_objects": 0,
    "current_user": None,
    "picking": False
}

MODEL_PATH = "my_model.onnx"
CONF_THRESH = 0.5
TARGET_LABELS = ["Object", "Orders"]

model = YOLO(MODEL_PATH,task='detect')
labels = model.names


def run_motor_sequence():
    print("[Motor] Sequence start")

    stop_motor()
    time.sleep(0.2)

    select_motor(x=True)
    run_motor_backward()
    time.sleep(7.5)
    stop_motor()

    magnet_on()
    time.sleep(0.2)

    run_motor_forward()
    time.sleep(2)
    stop_motor()

    select_motor(y=True)
    run_motor_forward()
    time.sleep(5)

    select_motor(x=True)
    run_motor_backward()
    time.sleep(7.5)
    stop_motor()

    magnet_off()
    time.sleep(1)
    magnet_on()

    select_motor(y=True)
    run_motor_backward()
    print("[Motor] Sequence complete")


def pick_and_place_worker():
    print("[Worker] Thread started, waiting for Start")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Camera not opened")
        return

    DETECTION_DELAY_AFTER_Y_START = 4 # seconds

    while True:
        if not state["picking"]:
            time.sleep(0.2)
            continue

        print("[Worker] Picking started")

        # Initialize motors
        stop_all()
        magnet_on()
        select_motor(y=True)
        run_motor_backward()

        # --- wait a bit before starting detection ---
        print(f"[Worker] Waiting {DETECTION_DELAY_AFTER_Y_START}s before object detection")
        time.sleep(DETECTION_DELAY_AFTER_Y_START)

        while state["picking"] and state["dispatched_orders"] < state["total_orders"]:
            ret, frame = cap.read()
            if not ret:
                continue

            results = model(frame, verbose=False)
            detected = False

            for det in results[0].boxes:
                if det.conf.item() < CONF_THRESH:
                    continue
                label = labels[int(det.cls.item())]
                if label in TARGET_LABELS:
                    detected = True
                    break

            if detected:
                print("[YOLO] Object detected")
                run_motor_sequence()

                state["dispatched_orders"] += 1
                state["stored_objects"] += 1

                print(f"[Worker] {state['dispatched_orders']} / {state['total_orders']}")
                time.sleep(1)

        print("[Worker] Orders complete")
        stop_all()
        magnet_off()
        state["picking"] = False
