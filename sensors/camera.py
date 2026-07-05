# ─────────────────────────────────────────
# Camera Fire Detection — YOLOv8 AI Model
# BGR input for correct YOLO inference
# YOLO runs in separate thread
# AI Fire Detection System
# ─────────────────────────────────────────
import cv2
import time
import os
import threading
from datetime import datetime
from collections import deque
from picamera2 import Picamera2
from ultralytics import YOLO


class CameraDetector:
    def __init__(self, model_path="models/fire_model.pt",
                 fire_conf=0.20, imgsz=320,
                 hit_thresh=4, dataset_dir="dataset"):

        self.fire_conf   = fire_conf
        self.imgsz       = imgsz
        self.hit_thresh  = hit_thresh
        self.dataset_dir = dataset_dir
        self.window      = deque(maxlen=20)
        self.fire_area   = 0
        self.fire_regions = []
        self.frame       = None
        self.last_save   = 0
        self._lock       = threading.Lock()
        self._latest_bgr = None

        os.makedirs(f"{dataset_dir}/images", exist_ok=True)
        os.makedirs(f"{dataset_dir}/labels", exist_ok=True)

        print("Loading YOLOv8 fire detection model...")
        self.model = YOLO(model_path)
        print(f"Model ready — fire only, threshold:{fire_conf}")
        print("Note: passing BGR to YOLO for correct color inference")

        self.cam = Picamera2()
        self.cam.configure(self.cam.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"}
        ))
        self.cam.start()
        time.sleep(2)
        print("Camera ready.")

        threading.Thread(target=self._inference_loop, daemon=True).start()

    def _inference_loop(self):
        """YOLO inference in background — uses BGR for correct detection"""
        while True:
            with self._lock:
                bgr = self._latest_bgr

            if bgr is None:
                time.sleep(0.05)
                continue

            try:
                h, w    = bgr.shape[:2]
                results = self.model(
                    bgr,                # BGR input — correct for YOLO
                    conf    = self.fire_conf,
                    imgsz   = self.imgsz,
                    verbose = False,
                    classes = [0]       # fire only
                )

                fire_area    = 0
                fire_regions = []
                label_lines  = []
                boxes        = results[0].boxes

                if boxes is not None and len(boxes) > 0:
                    # Keep only highest confidence detection
                    best_conf = 0
                    best_box  = None
                    for box in boxes:
                        conf = float(box.conf[0])
                        if conf > best_conf:
                            best_conf = conf
                            best_box  = box

                    if best_box is not None:
                        x1, y1, x2, y2 = map(int, best_box.xyxy[0].tolist())
                        area = (x2 - x1) * (y2 - y1)
                        fire_area = area
                        fire_regions.append((x1, y1, x2-x1, y2-y1, 0, best_conf))

                        cx = ((x1 + x2) / 2) / w
                        cy = ((y1 + y2) / 2) / h
                        bw = (x2 - x1) / w
                        bh = (y2 - y1) / h
                        label_lines.append(
                            f"0 {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}"
                        )

                now = time.time()
                if label_lines and now - self.last_save > 3:
                    self._save_dataset(bgr, label_lines)
                    self.last_save = now

                with self._lock:
                    self.fire_area    = fire_area
                    self.fire_regions = fire_regions

            except Exception as e:
                print(f"Inference error: {e}")

            time.sleep(0.03)

    def read(self):
        """Capture RGB frame — convert to BGR for inference, keep RGB for display"""
        try:
            rgb        = self.cam.capture_array()
            self.frame = rgb.copy()
            bgr        = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

            with self._lock:
                self._latest_bgr = bgr        # pass BGR to inference thread
                fire_area        = self.fire_area
                fire_regions     = list(self.fire_regions)

            # Draw boxes on RGB frame for correct display colors
            display = rgb.copy()
            for (x1, y1, bw, bh, cls, conf) in fire_regions:
                x2 = x1 + bw
                y2 = y1 + bh
                cv2.rectangle(display, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(display, f"FIRE {conf:.0%}",
                    (x1, max(y1 - 8, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

            return fire_area, fire_regions, display

        except Exception as e:
            print(f"Camera error: {e}")
            return 0, [], self.frame

    def _save_dataset(self, bgr_frame, label_lines):
        ts       = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        img_path = f"{self.dataset_dir}/images/{ts}.jpg"
        lbl_path = f"{self.dataset_dir}/labels/{ts}.txt"
        cv2.imwrite(img_path, bgr_frame)
        with open(lbl_path, 'w') as f:
            f.write('\n'.join(label_lines))
        print(f"Dataset saved: {ts}.jpg")

    def is_fire_alert(self):
        with self._lock:
            area = self.fire_area
        self.window.append(1 if area > 0 else 0)
        return sum(self.window) >= self.hit_thresh

    def get_dataset_count(self):
        try:
            return len(os.listdir(f"{self.dataset_dir}/images"))
        except:
            return 0

    def get_detections_str(self):
        with self._lock:
            regions = list(self.fire_regions)
        if not regions:
            return []
        return [f"fire {r[5]:.0%}" for r in regions]

    def stop(self):
        self.cam.stop()
