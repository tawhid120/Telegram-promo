import subprocess
import sys
import os
import logging
from flask import Flask, jsonify, render_template_string
from datetime import datetime
import threading
import time

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

bot_process = None
bot_status = {
    "running": False,
    "started_at": None,
    "messages_sent": 0,
    "errors": [],
    "log_lines": []
}

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Promo Bot</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Bengali:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #0d0f1a; --surface: #151828; --card: #1c2035;
            --border: #2a3050; --accent: #4f8ef7; --accent2: #7c5af7;
            --green: #3dd68c; --red: #f75a5a; --yellow: #f7c948;
            --text: #e8eaf6; --muted: #6b7394;
        }
        * { margin:0; padding:0; box-sizing:border-box; }
        body {
            background: var(--bg); color: var(--text);
            font-family: 'Noto Sans Bengali', sans-serif; min-height: 100vh;
            background-image: radial-gradient(ellipse at 20% 20%, rgba(79,142,247,0.07) 0%, transparent 60%),
                              radial-gradient(ellipse at 80% 80%, rgba(124,90,247,0.07) 0%, transparent 60%);
        }
        header {
            background: var(--surface); border-bottom: 1px solid var(--border);
            padding: 20px 40px; display: flex; align-items: center; gap: 16px;
        }
        .logo {
            width:44px; height:44px;
            background: linear-gradient(135deg, var(--accent), var(--accent2));
            border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:22px;
        }
        header h1 { font-size:20px; font-weight:700; }
        header p  { color:var(--muted); font-size:13px; margin-top:2px; }
        .container { max-width:900px; margin:40px auto; padding:0 24px; }
        .status-banner {
            background:var(--card); border:1px solid var(--border); border-radius:16px;
            padding:24px 28px; display:flex; align-items:center; gap:16px; margin-bottom:28px;
        }
        .pulse-dot {
            width:14px; height:14px; border-radius:50%; background:var(--green);
            box-shadow:0 0 0 0 rgba(61,214,140,0.5); animation:pulse 2s infinite; flex-shrink:0;
        }
        .pulse-dot.offline { background:var(--red); animation:none; }
        @keyframes pulse {
            0%   { box-shadow: 0 0 0 0 rgba(61,214,140,0.5); }
            70%  { box-shadow: 0 0 0 10px rgba(61,214,140,0); }
            100% { box-shadow: 0 0 0 0 rgba(61,214,140,0); }
        }
        .status-text h2 { font-size:17px; font-weight:600; }
        .status-text p  { color:var(--muted); font-size:13px; margin-top:4px; font-family:'JetBrains Mono',monospace; }
        .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:16px; margin-bottom:28px; }
        .card { background:var(--card); border:1px solid var(--border); border-radius:14px; padding:22px 24px; }
        .card-label { color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.08em; margin-bottom:10px; }
        .card-value { font-size:28px; font-weight:700; font-family:'JetBrains Mono',monospace; }
        .green{color:var(--green);} .blue{color:var(--accent);} .purple{color:var(--accent2);} .err{color:var(--red);}
        .section-title { font-size:13px; font-weight:600; color:var(--muted); text-transform:uppercase; letter-spacing:.08em; margin-bottom:12px; }
        .log-box {
            background:var(--card); border:1px solid var(--border); border-radius:14px;
            padding:16px 20px; font-family:'JetBrains Mono',monospace; font-size:12px;
            line-height:1.9; color:var(--muted); max-height:260px; overflow-y:auto; margin-bottom:24px;
        }
        .entry { border-bottom:1px solid var(--border); padding:4px 0; }
        .entry:last-child { border-bottom:none; }
        .ok   { color:var(--green); }
        .warn { color:var(--yellow); }
        .bad  { color:var(--red); }
        .refresh { color:var(--muted); font-size:12px; text-align:right; margin-bottom:8px; }
        footer { text-align:center; color:var(--muted); font-size:12px; padding:32px 0 20px; }
    </style>
    <script> setTimeout(() => location.reload(), 20000); </script>
</head>
<body>
<header>
    <div class="logo">📢</div>
    <div>
        <h1>Telegram Promo Bot</h1>
        <p>Automated group message broadcaster</p>
    </div>
</header>
<div class="container">
    <div class="status-banner">
        <div class="pulse-dot {{ '' if status.running else 'offline' }}"></div>
        <div class="status-text">
            <h2>বট {{ '✅ সক্রিয় আছে' if status.running else '🔄 চালু হচ্ছে...' }}</h2>
            <p>শুরু হয়েছে: {{ status.started_at or 'N/A' }}</p>
        </div>
    </div>
    <div class="grid">
        <div class="card">
            <div class="card-label">প্রসেস স্ট্যাটাস</div>
            <div class="card-value {{ 'green' if status.running else 'err' }}">{{ 'LIVE' if status.running else 'DOWN' }}</div>
        </div>
        <div class="card">
            <div class="card-label">মেসেজ পাঠানো</div>
            <div class="card-value purple">{{ status.messages_sent }}</div>
        </div>
        <div class="card">
            <div class="card-label">শুরুর সময়</div>
            <div class="card-value blue" style="font-size:18px;">{{ status.started_at.split(' ')[1] if status.started_at else '--' }}</div>
        </div>
        <div class="card">
            <div class="card-label">এরর সংখ্যা</div>
            <div class="card-value {{ 'err' if status.errors else 'green' }}">{{ status.errors|length }}</div>
        </div>
    </div>
    <div class="refresh">⟳ প্রতি ২০ সেকেন্ডে স্বয়ংক্রিয় আপডেট</div>
    <div class="section-title">লাইভ লগ (সর্বশেষ ৩০ লাইন)</div>
    <div class="log-box" id="logbox">
        {% for line in status.log_lines[-30:] %}
        <div class="entry">
            {% if '✅' in line or 'রেডি' in line or '🚀' in line %}
                <span class="ok">{{ line }}</span>
            {% elif '❌' in line or 'error' in line.lower() or 'ERROR' in line %}
                <span class="bad">{{ line }}</span>
            {% elif '⏳' in line or '⚠️' in line %}
                <span class="warn">{{ line }}</span>
            {% else %}
                {{ line }}
            {% endif %}
        </div>
        {% else %}
        <div class="entry"><span style="color:var(--accent)">[INFO]</span> লগ লোড হচ্ছে... কয়েক সেকেন্ড অপেক্ষা করুন।</div>
        {% endfor %}
    </div>
    {% if status.errors %}
    <div class="section-title">সর্বশেষ এরর</div>
    <div class="log-box">
        {% for e in status.errors[-5:] %}
        <div class="entry bad">⚠️ {{ e }}</div>
        {% endfor %}
    </div>
    {% endif %}
</div>
<footer>Telegram Promo Bot — Pyrogram + Flask on Render</footer>
<script>
    // লগ বক্স নিচে স্ক্রোল করা
    const lb = document.getElementById('logbox');
    if(lb) lb.scrollTop = lb.scrollHeight;
</script>
</body>
</html>
"""

# ---- লগ স্ট্রিমার ----
def stream_logs(process):
    for line in iter(process.stdout.readline, ''):
        line = line.strip()
        if not line:
            continue
        bot_status["log_lines"].append(line)
        if len(bot_status["log_lines"]) > 300:
            bot_status["log_lines"] = bot_status["log_lines"][-300:]
        if "🚀" in line or "মেসেজ পাঠানো হয়েছে" in line:
            bot_status["messages_sent"] += 1
        if "❌" in line or "ERROR" in line:
            bot_status["errors"].append(line)
            if len(bot_status["errors"]) > 100:
                bot_status["errors"] = bot_status["errors"][-100:]

# ---- প্রসেস ওয়াচার (অটো-রিস্টার্ট) ----
def watch_process():
    global bot_process
    while True:
        if bot_process is None or bot_process.poll() is not None:
            # পুরনো প্রসেস মরে গেলে বা প্রথমবার
            exit_code = bot_process.poll() if bot_process else None
            if exit_code is not None:
                msg = f"⚠️ main.py বন্ধ হয়ে গেছে (exit={exit_code}), রিস্টার্ট হচ্ছে..."
                logging.warning(msg)
                bot_status["log_lines"].append(msg)
                bot_status["running"] = False
                time.sleep(5)  # রিস্টার্টের আগে একটু অপেক্ষা

            logging.info("🔄 main.py চালু করা হচ্ছে subprocess হিসেবে...")
            bot_status["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            bot_process = subprocess.Popen(
                [sys.executable, "-u", "main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            bot_status["running"] = True
            bot_status["log_lines"].append(f"✅ main.py চালু হয়েছে। PID: {bot_process.pid}")
            logging.info(f"✅ main.py PID={bot_process.pid}")

            # লগ রিডার থ্রেড
            t = threading.Thread(target=stream_logs, args=(bot_process,), daemon=True)
            t.start()

        time.sleep(10)

# ---- Flask রুট ----
@app.route("/")
def dashboard():
    return render_template_string(DASHBOARD_HTML, status=bot_status)

@app.route("/health")
def health():
    return jsonify({"status": "ok", "bot_running": bot_status["running"]}), 200

@app.route("/status")
def status_api():
    return jsonify({
        "running": bot_status["running"],
        "started_at": bot_status["started_at"],
        "messages_sent": bot_status["messages_sent"],
        "error_count": len(bot_status["errors"]),
        "last_log": bot_status["log_lines"][-1] if bot_status["log_lines"] else ""
    })

# ---- এন্ট্রি পয়েন্ট ----
if __name__ == "__main__":
    watcher = threading.Thread(target=watch_process, daemon=True)
    watcher.start()

    port = int(os.environ.get("PORT", 5000))
    logging.info(f"🌐 Flask চালু হচ্ছে port {port}")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
