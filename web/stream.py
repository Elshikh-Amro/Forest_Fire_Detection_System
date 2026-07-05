# ─────────────────────────────────────────
# Flask Live Stream and Web Dashboard
# AI Fire Detection System
# ─────────────────────────────────────────
from flask import Flask, Response, render_template_string
from datetime import datetime

app = Flask(__name__)

PAGE = """
<!DOCTYPE html>
<html>
<head>
  <title>Fire Detection — AI System</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="3">
  <style>
    * { box-sizing:border-box; margin:0; padding:0; }
    body   { background:#111; color:#fff; font-family:sans-serif; }
    h1     { text-align:center; padding:14px 0 4px;
             font-size:1.1em; color:#ccc; letter-spacing:1px; }
    .badge { display:block; text-align:center; margin:0 auto 6px;
             font-size:0.7em; color:#555; letter-spacing:2px; }
    img    { width:100%; max-width:640px; display:block;
             margin:0 auto; border:2px solid #333; }
    #status { padding:12px; font-size:1.15em; font-weight:bold;
              text-align:center; margin:8px 16px; border-radius:8px; }
    .fire  { background:#c0392b; }
    .clear { background:#27ae60; }
    .grid  { display:grid; grid-template-columns:1fr 1fr 1fr;
             gap:8px; padding:8px 16px; max-width:640px; margin:0 auto; }
    .card  { background:#1e1e1e; border-radius:8px;
             padding:10px; text-align:center; }
    .card h3 { font-size:0.7em; color:#777; margin-bottom:4px;
               text-transform:uppercase; letter-spacing:1px; }
    .card p  { font-size:1.1em; font-weight:bold; }
    .alert { color:#e74c3c; }
    .ok    { color:#2ecc71; }
    #ai_box { max-width:640px; margin:6px auto;
              background:#0d1a0d; border:1px solid #1e3a1e;
              border-radius:8px; padding:10px 14px; }
    #ai_box h3 { font-size:0.75em; color:#4caf50;
                 text-transform:uppercase; letter-spacing:1px;
                 margin-bottom:6px; }
    .det_item { display:inline-block; background:#1a2e1a;
                border:1px solid #2e5e2e; border-radius:4px;
                padding:3px 10px; margin:2px; font-size:0.85em;
                color:#81c784; }
    #dataset  { max-width:640px; margin:4px auto;
                background:#0d1a2d; border:1px solid #1e3a5e;
                border-radius:8px; padding:8px 14px;
                text-align:center; font-size:0.8em; color:#64b5f6; }
    footer { text-align:center; color:#333;
             font-size:0.7em; padding:10px; }
  </style>
</head>
<body>
  <h1>Forest Fire Detection System</h1>
  <span class="badge">AI ENHANCED — YOLOv8 NANO</span>

  <img src="/stream" />

  <div id="status" class="{{ 'fire' if s.fire else 'clear' }}">
    {{ '*** FIRE DETECTED — ALERT SENT ***' if s.fire else 'All Clear — Monitoring' }}
  </div>

  <div class="grid">
    <div class="card">
      <h3>Temperature</h3>
      <p class="{{ 'alert' if s.heat else 'ok' }}">
        {{ '%.1f'|format(s.temperature) }}°C</p>
    </div>
    <div class="card">
      <h3>Humidity</h3>
      <p>{{ '%.1f'|format(s.humidity) }}%</p>
    </div>
    <div class="card">
      <h3>Smoke</h3>
      <p class="{{ 'alert' if s.smoke else 'ok' }}">
        {{ s.smoke_raw }}</p>
    </div>
    <div class="card">
      <h3>Heat Sensor</h3>
      <p class="{{ 'alert' if s.heat else 'ok' }}">
        {{ 'ALERT' if s.heat else 'Normal' }}</p>
    </div>
    <div class="card">
      <h3>Smoke Sensor</h3>
      <p class="{{ 'alert' if s.smoke else 'ok' }}">
        {{ 'ALERT' if s.smoke else 'Normal' }}</p>
    </div>
    <div class="card">
      <h3>AI Camera</h3>
      <p class="{{ 'alert' if s.camera else 'ok' }}">
        {{ 'ALERT' if s.camera else 'Normal' }}</p>
    </div>
  </div>

  <div id="ai_box">
    <h3>AI Detections</h3>
    {% if s.detections %}
      {% for d in s.detections %}
        <span class="det_item">{{ d }}</span>
      {% endfor %}
    {% else %}
      <span style="color:#555">No fire or smoke detected</span>
    {% endif %}
  </div>

  <div id="dataset">
    Dataset collected: <strong>{{ s.dataset_count }}</strong> training images
    &nbsp;|&nbsp; Alert level: {{ s.alert_count }}/20
  </div>

  <footer>{{ now }}</footer>
</body>
</html>
"""

def create_stream(get_frame_func, get_status_func):
    @app.route('/')
    def index():
        s = get_status_func()
        return render_template_string(
            PAGE,
            s=type('S', (), s)(),
            now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

    @app.route('/stream')
    def stream():
        return Response(
            get_frame_func(),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )

    return app
