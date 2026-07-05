# 🌲 Forest Fire Detection System

A **multi-sensor embedded platform** with **AI-enhanced visual detection** built on **Raspberry Pi 4**.  
This project integrates thermal, gas, and visual sensing with a **democratic voting mechanism** to minimize false positives, while enabling **real-time IoT monitoring** via the Blynk cloud.

---

## 📖 Table of Contents
1. [Overview](#overview)
2. [System Motivation](#system-motivation)
3. [Hardware Architecture](#hardware-architecture)
4. [Software Design](#software-design)
5. [Dual Use Cases](#dual-use-cases)
6. [IoT Integration](#iot-integration)
7. [Testing & Results](#testing--results)
8. [Future Recommendations](#future-recommendations)
9. [Getting Started](#getting-started)
10. [License](#license)

---

## 🔥 Overview
The system addresses the **critical need for reliable early-stage forest fire detection** under varied environmental conditions.  
It leverages **multi-modal sensor fusion** (temperature, smoke, and visual data) with a **2-out-of-3 voting mechanism** to ensure robust detection.

---

## 🧠 System Motivation
- **Problem:** Single sensors are prone to false alarms due to environmental interference (sunlight, dust, shadows).
- **Solution:** Combine **three independent modalities**:
  - DHT22 → Temperature & Humidity
  - MQ135 → Smoke/Gas
  - Pi Camera → Visual Fire/Smoke Detection (OpenCV or YOLOv8 Nano)

---

## ⚙️ Hardware Architecture
- **Controller:** Raspberry Pi 4B (Quad-core Cortex-A72, 1.5–1.8 GHz)
- **Sensors:**
  - DHT22 (Temp/Humidity)
  - MQ135 (Smoke/Gas)
  - Pi Camera v1.3 (Visual)
- **ADC:** MCP3008 (10-bit SAR, SPI interface)
- **AI Model:** YOLOv8 Nano (optimized for edge inference)

---

## 💻 Software Design
- **Language:** Python 3.13
- **Concurrency Model:**
  - Camera Thread → ~20 fps capture & detection
  - Sensor Thread → 2s polling interval
- **Key Libraries:** `picamera2`, `ultralytics`, `opencv-python`, `flask`, `adafruit-dht`, `adafruit-mcp3xxx`, `numpy`, `blynk`

---

## 🔄 Dual Use Cases
### Use Case 1 — Baseline (OpenCV)
- Background subtraction for fire detection
- MQ135 digital output (D0)
- ~20 fps, low cost, simple deployment

### Use Case 2 — AI Enhanced (YOLOv8 Nano)
- Deep learning detection (fire/smoke classes)
- MQ135 analog output via MCP3008
- ~5–10 fps, higher accuracy, drone-ready

---

## ☁️ IoT Integration
- **Platform:** Blynk Cloud
- **Features:**
  - Real-time dashboard (Temp, Humidity, Smoke, Alerts)
  - Push notifications on fire detection
  - Automatic dataset collection for retraining
  - Offline resilience (local streaming continues if cloud unavailable)

---

## ✅ Testing & Results
- **Scenarios Tested:** Flame only, Smoke only, Combined, Normal background
- **Outcome:** All 6 scenarios passed with **zero false positives** under single-sensor triggers.
- **Voting Logic:** Requires 2-of-3 sensor agreement with ~6s persistence.

---

## 🚀 Future Recommendations
1. **Drone Integration** → Wide-area monitoring with stabilized gimbal.
2. **Model Fine-Tuning** → Retrain YOLO with collected domain-specific data.
3. **Additional Sensors** → Wind speed, PM2.5/PM10, CO, IR thermometer.
4. **Thermal Camera** → FLIR Lepton/MLX90640 for 24/7 monitoring.

---

## 🛠️ Getting Started
### Prerequisites
- Raspberry Pi 4B (≥2GB RAM recommended)
- Python 3.13
- Blynk account & auth token

### Installation
```bash
git clone https://github.com/yourusername/forest-fire-detection.git
cd forest-fire-detection
pip install -r requirements.txt
