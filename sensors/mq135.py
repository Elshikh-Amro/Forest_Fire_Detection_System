# ─────────────────────────────────────────
# MQ135 Smoke / Gas Sensor
# Keeps last valid reading on error
# ─────────────────────────────────────────
import board
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn


class MQ135Sensor:
    def __init__(self):
        spi            = busio.SPI(clock=board.SCK,
                                   MISO=board.MISO,
                                   MOSI=board.MOSI)
        cs             = digitalio.DigitalInOut(board.CE0)
        mcp            = MCP.MCP3008(spi, cs)
        self.channel   = AnalogIn(mcp, MCP.P0)
        self.raw_value = 0
        self.voltage   = 0.0
        self.error     = None
        self._valid_raw = None   # last known good raw value
        self._valid_vol = None   # last known good voltage

    def read(self):
        try:
            raw = self.channel.value
            vol = self.channel.voltage

            if raw is not None and raw > 0:
                # Valid reading
                self.raw_value  = raw
                self.voltage    = vol
                self._valid_raw = raw
                self._valid_vol = vol
                self.error      = None
            else:
                # Keep last valid
                if self._valid_raw is not None:
                    self.raw_value = self._valid_raw
                    self.voltage   = self._valid_vol
                self.error = "Sensor returned zero"

        except Exception as e:
            # Keep last valid reading on exception
            if self._valid_raw is not None:
                self.raw_value = self._valid_raw
                self.voltage   = self._valid_vol
            self.error = str(e)

        return self.raw_value, self.voltage, self.error

    def is_smoke_alert(self, threshold):
        return self.raw_value > threshold
