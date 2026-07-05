# ─────────────────────────────────────────
# Forest Fire Detection System
# Configuration File
# ─────────────────────────────────────────

# Email settings
EMAIL_SENDER   = "amro.moe98@gmail.com"
EMAIL_PASSWORD = "rkglsvhpmhwpnfwt"
EMAIL_RECEIVER = "amro.moe98@gmail.com"

# Smoke sensor thresholds
SMOKE_BASELINE  = 2500   # clean air reading
SMOKE_THRESHOLD = 4500  # alert at 2x baseline

# Temperature threshold (degrees C)
TEMP_THRESHOLD  = 32

# Humidity drop threshold (%)
HUMIDITY_DROP   = 37

# Camera detection
DIFF_THRESH     = 180     # brightness diff from background
MIN_FIRE_AREA   = 70    # minimum pixel area
CAM_HIT_THRESH  = 8      # hits in window to confirm fire

# Alert settings
ALERT_CONFIRM   = 4      # sensor agreements before alert
EMAIL_COOLDOWN  = 60     # seconds between emails

# Paths
SNAPSHOT_DIR    = "/home/bigee/fire_project/snapshots"

BLYNK_TOKEN = "RnWPMIOX8pl2xWxY3Cm3kGtwf-yowhj5"
