# ─────────────────────────────────────────
# Forest Fire Detection System
# AI Enhanced — YOLOv8 + DHT22 + MQ135
# Blynk IoT Dashboard
# Graduation Project
# ─────────────────────────────────────────
import cv2
import threading
import time
import os
from datetime import datetime

from config import (
    EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER,
    SMOKE_THRESHOLD, TEMP_THRESHOLD, HUMIDITY_DROP,
    ALERT_CONFIRM, EMAIL_COOLDOWN, SNAPSHOT_DIR,
    BLYNK_TOKEN
)
from sensors.dht22        import DHT22Sensor
from sensors.mq135        import MQ135Sensor
from sensors.camera       import CameraDetector
from alerts.email_alert   import EmailAlert
from alerts.blynk_alert   import BlynkAlert
from web.stream           import create_stream

os.makedirs(SNAPSHOT_DIR, exist_ok=True)

print("=" * 55)
print("  Forest Fire Detection System — AI Enhanced")
print("  YOLOv8 Nano + DHT22 + MQ135 + Blynk IoT")
print("  Graduation Project")
print("=" * 55)

dht    = DHT22Sensor()
mq135  = MQ135Sensor()
camera = CameraDetector(
    model_path  = "models/fire_model.pt",
    fire_conf   = 0.20,
    imgsz       = 320,
    hit_thresh  = 4,
    dataset_dir = "dataset"
)
# email = EmailAlert(EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER)
blynk = BlynkAlert(BLYNK_TOKEN)

lock         = threading.Lock()
latest_frame = None
status = {
    "fire":          False,
    "heat":          False,
    "smoke":         False,
    "camera":        False,
    "temperature":   0.0,
    "humidity":      0.0,
    "smoke_raw":     0,
    "alert_count":   0,
    "dataset_count": 0,
    "detections":    [],
}
last_email    = 0
last_blynk    = 0
alert_counter = 0

def save_snapshot(frame):
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{SNAPSHOT_DIR}/fire_{ts}.jpg"
    cv2.imwrite(filename, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    print(f"Snapshot saved: {filename}")
    return filename

# ── Camera loop — fast ~20fps ──
def camera_loop():
    global latest_frame
    while True:
        try:
            fire_area, fire_regions, display = camera.read()

            if display is None:
                time.sleep(0.05)
                continue

            with lock:
                s = dict(status)

            label = "*** FIRE DETECTED ***" if s['fire'] else "Monitoring..."
            color = (255, 50, 50) if s['fire'] else (50, 220, 50)

            cv2.putText(display, label, (10, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
            cv2.putText(display,
                f"Temp:{s['temperature']:.1f}C  "
                f"Hum:{s['humidity']:.1f}%  "
                f"Smoke:{s['smoke_raw']}",
                (10, 65),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(display,
                f"Heat:{'!' if s['heat'] else 'OK'}  "
                f"Smoke:{'!' if s['smoke'] else 'OK'}  "
                f"AI:{'!' if s['camera'] else 'OK'}  "
                f"Alert:{s['alert_count']}/20",
                (10, 88),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
            cv2.putText(display,
                f"Dataset: {s['dataset_count']} images",
                (10, 110),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (100, 220, 100), 1)
            cv2.putText(display,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                (10, 468),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, (160, 160, 160), 1)

            with lock:
                latest_frame = display

        except Exception as e:
            print(f"Camera loop error: {e}")
        time.sleep(0.05)

# ── Sensor loop — every 2 seconds ──
def sensor_loop():
    global last_email, last_blynk, alert_counter
    while True:
        try:
            temp, humidity, _ = dht.read()
            smoke_raw, _, _   = mq135.read()

            heat_alert    = dht.is_heat_alert(TEMP_THRESHOLD)
            smoke_alert   = mq135.is_smoke_alert(SMOKE_THRESHOLD)
            camera_alert  = camera.is_fire_alert()
            detections    = camera.get_detections_str()
            dataset_count = camera.get_dataset_count()

            # 2 of 3 voting
            alerts = sum([heat_alert, smoke_alert, camera_alert])
            if alerts >= 2:
                alert_counter = min(alert_counter + 1, 20)
            else:
                alert_counter = max(alert_counter - 1, 0)

            fire_confirmed = alert_counter >= ALERT_CONFIRM

            # ── Send email alert ──
            if fire_confirmed:
                now = time.time()
                if now - last_email > EMAIL_COOLDOWN:
                    with lock:
                        frame = latest_frame
                    if frame is not None:
                        snapshot = save_snapshot(frame)
                        reasons  = []
                        if heat_alert:
                            reasons.append(f"Temp {temp:.1f}C")
                        if smoke_alert:
                            reasons.append(f"Smoke {smoke_raw}")
                        if camera_alert:
                            reasons.append(
                                f"AI: {', '.join(detections) if detections else 'fire/smoke'}"
                            )
                        current = {
                            "temperature":   temp,
                            "humidity":      humidity,
                            "smoke_raw":     smoke_raw,
                            "heat":          heat_alert,
                            "smoke":         smoke_alert,
                            "camera":        camera_alert,
                            "dataset_count": dataset_count,
                        }
                        threading.Thread(
#                             target=email.send,
                            args=(" + ".join(reasons), current, snapshot),
                            daemon=True
                        ).start()
                        last_email = now

            # ── Send Blynk alert notification ──
            if fire_confirmed:
                now = time.time()
                if now - last_blynk > 30:  # notify max every 30 seconds
                    reasons = []
                    if heat_alert:   reasons.append(f"Temp {temp:.1f}C")
                    if smoke_alert:  reasons.append(f"Smoke {smoke_raw}")
                    if camera_alert: reasons.append("Visual fire detected")
                    blynk.send_alert(
                        f"FIRE ALERT! {' + '.join(reasons)}"
                    )
                    last_blynk = now

            # ── Update Blynk dashboard every 2 seconds ──
            blynk.update(
                temperature   = temp,
                humidity      = humidity,
                smoke_raw     = smoke_raw,
                fire_alert    = fire_confirmed,
                heat_alert    = heat_alert,
                smoke_alert   = smoke_alert,
                camera_alert  = camera_alert,
                dataset_count = dataset_count,
            )

            # Update shared status
            with lock:
                status.update({
                    "fire":          fire_confirmed,
                    "heat":          heat_alert,
                    "smoke":         smoke_alert,
                    "camera":        camera_alert,
                    "temperature":   temp,
                    "humidity":      humidity,
                    "smoke_raw":     smoke_raw,
                    "alert_count":   alert_counter,
                    "dataset_count": dataset_count,
                    "detections":    detections,
                })

            print(
                f"[{datetime.now().strftime('%H:%M:%S')}]  "
                f"Temp:{temp:.1f}C  Hum:{humidity:.1f}%  "
                f"Smoke:{smoke_raw}  "
                f"Heat:{'!' if heat_alert else 'OK'}  "
                f"Smoke:{'!' if smoke_alert else 'OK'}  "
                f"AI:{'!' if camera_alert else 'OK'}  "
                f"Fire:{fire_confirmed}  "
                f"Dataset:{dataset_count}imgs"
            )

        except Exception as e:
            print(f"Sensor loop error: {e}")
        time.sleep(2)

# ── Frame generator ──
def get_frames():
    while True:
        with lock:
            frame = latest_frame
        if frame is None:
            time.sleep(0.05)
            continue
        _, buffer = cv2.imencode(
            '.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50]
        )
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' +
               buffer.tobytes() + b'\r\n')
        time.sleep(0.05)

def get_status():
    with lock:
        return dict(status)

if __name__ == '__main__':
    threading.Thread(target=camera_loop, daemon=True).start()
    threading.Thread(target=sensor_loop, daemon=True).start()

    print("\nSystem running!")
    print("Open stream: http://raspberrypi.local:5000")
    print("Open Blynk app on your phone\n")

    flask_app = create_stream(get_frames, get_status)
    flask_app.run(host='0.0.0.0', port=5000, threaded=True)
