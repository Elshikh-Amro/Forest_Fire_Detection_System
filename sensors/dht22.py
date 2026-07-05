# ─────────────────────────────────────────
# DHT22 Temperature & Humidity Sensor
# Keeps last valid reading on error
# ─────────────────────────────────────────
import board
import adafruit_dht
import time


class DHT22Sensor:
    def __init__(self):
        self.sensor        = adafruit_dht.DHT22(board.D4)
        self.temperature   = 0.0
        self.humidity      = 0.0
        self.last_humidity = None
        self.error         = None
        self._valid_temp   = None   # last known good temperature
        self._valid_hum    = None   # last known good humidity

    def read(self):
        try:
            temp = self.sensor.temperature
            hum  = self.sensor.humidity

            if temp is not None and hum is not None:
                # Valid reading — update everything
                self.temperature   = temp
                self.humidity      = hum
                self._valid_temp   = temp
                self._valid_hum    = hum
                self.error         = None
            else:
                # None returned — keep last valid reading
                if self._valid_temp is not None:
                    self.temperature = self._valid_temp
                    self.humidity    = self._valid_hum
                self.error = "Sensor returned None"

        except Exception as e:
            # Exception — keep last valid reading, don't reset to 0
            if self._valid_temp is not None:
                self.temperature = self._valid_temp
                self.humidity    = self._valid_hum
            self.error = str(e)

        return self.temperature, self.humidity, self.error

    def is_heat_alert(self, threshold):
        return self.temperature > threshold

    def is_humidity_drop(self, drop_threshold):
        if self.last_humidity is None:
            self.last_humidity = self.humidity
            return False
        drop = self.last_humidity - self.humidity
        self.last_humidity = self.humidity
        return drop > drop_threshold
