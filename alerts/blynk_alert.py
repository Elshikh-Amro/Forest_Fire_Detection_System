# ─────────────────────────────────────────
# Blynk IoT Alert System
# AI Fire Detection System
# Using Blynk HTTP REST API
# ─────────────────────────────────────────
import requests


BLYNK_URL = "https://blynk.cloud/external/api"


class BlynkAlert:
    def __init__(self, auth_token):
        self.token = auth_token
        print("Blynk REST API initialised.")
        self._test_connection()

    def _test_connection(self):
        try:
            r = requests.get(
                f"{BLYNK_URL}/isHardwareConnected",
                params={"token": self.token},
                timeout=5
            )
            print(f"Blynk connection test: {r.status_code} — {r.text}")
        except Exception as e:
            print(f"Blynk connection test failed: {e}")

    def update(self, temperature, humidity, smoke_raw,
               fire_alert, heat_alert, smoke_alert,
               camera_alert, dataset_count=0):
        """Send all sensor readings to Blynk dashboard"""
        try:
            params = {
                "token": self.token,
                "v0":    round(temperature, 1),
                "v1":    round(humidity, 1),
                "v2":    smoke_raw,
                "v3":    1 if fire_alert   else 0,
                "v4":    1 if heat_alert   else 0,
                "v5":    1 if smoke_alert  else 0,
                "v6":    1 if camera_alert else 0,
                "v7":    dataset_count,
            }
            r = requests.get(
                f"{BLYNK_URL}/batch/update",
                params=params,
                timeout=3
            )
            if r.status_code != 200:
                print(f"Blynk update error: {r.status_code} {r.text}")
        except Exception as e:
            print(f"Blynk update error: {e}")

    def send_alert(self, message, token=None):
        """Send fire alert event to Blynk timeline"""
        try:
            r = requests.get(
                f"{BLYNK_URL}/logEvent",
                params={
                    "token":       self.token,
                    "code":        "Fire-Detected",
                    "description": message
                },
                timeout=5
            )
            print(f"Blynk event logged: {r.status_code} — {r.text}")
        except Exception as e:
            print(f"Blynk alert error: {e}")

    def run(self):
        pass
