# ─────────────────────────────────────────
# Email Alert System
# AI Fire Detection System
# ─────────────────────────────────────────
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime


class EmailAlert:
    def __init__(self, sender, password, receiver):
        self.sender   = sender
        self.password = password
        self.receiver = receiver

    def send(self, reason, status, snapshot_path=None):
        try:
            msg            = MIMEMultipart()
            msg['From']    = self.sender
            msg['To']      = self.receiver
            msg['Subject'] = (
                f"FIRE ALERT (AI) — "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

            body = f"""
FIRE DETECTED — AI Forest Fire Detection System
===============================================

Time         : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Detected by  : {reason}

Sensor Readings
---------------
Temperature  : {status['temperature']:.1f} C
Humidity     : {status['humidity']:.1f} %
Smoke Level  : {status['smoke_raw']} raw

Sensor Status
-------------
Heat Sensor  : {'ALERT' if status['heat']   else 'Normal'}
Smoke Sensor : {'ALERT' if status['smoke']  else 'Normal'}
AI Camera    : {'ALERT' if status['camera'] else 'Normal'}

Detection System : YOLOv8 Nano AI Model
Dataset Images   : {status.get('dataset_count', 0)} collected

-- Forest Fire Detection System (AI Enhanced)
   Graduation Project
            """
            msg.attach(MIMEText(body, 'plain'))

            if snapshot_path and os.path.exists(snapshot_path):
                with open(snapshot_path, 'rb') as f:
                    img = MIMEImage(f.read())
                    img.add_header('Content-Disposition', 'attachment',
                                   filename=os.path.basename(snapshot_path))
                    msg.attach(img)

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(self.sender, self.password)
                smtp.send_message(msg)

            print(f"Alert email sent — {reason}")
            return True

        except Exception as e:
            print(f"Email error: {e}")
            return False
