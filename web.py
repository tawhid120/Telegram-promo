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
    <link href="https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700;800&family=Noto+Sans+Bengali:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg:      #07080f;
            --surface: #0e1018;
            --card:    #12151f;
            --card2:   #161a26;
            --border:  rgba(255,255,255,0.06);
            --border2: rgba(255,255,255,0.11);
            --teal:    #00e5c3;
            --blue:    #3b82f6;
            --purple:  #a855f7;
            --rose:    #f43f5e;
            --amber:   #f59e0b;
            --text:    #f0f2ff;
            --muted:   #525878;
            --muted2:  #7b82a8;
        }

        *, *::before, *::after { margin:0; padding:0; box-sizing:border-box; }

        body {
            background: var(--bg);
            color: var(--text);
            font-family: 'Sora', 'Noto Sans Bengali', sans-serif;
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* Animated background glow */
        body::before {
            content: '';
            position: fixed; inset: 0; z-index: 0;
            background:
                radial-gradient(ellipse 80% 60% at 10% 0%,   rgba(0,229,195,0.055) 0%, transparent 55%),
                radial-gradient(ellipse 60% 50% at 90% 100%, rgba(168,85,247,0.065) 0%, transparent 55%),
                radial-gradient(ellipse 50% 40% at 50% 50%,  rgba(59,130,246,0.035) 0%, transparent 60%);
            pointer-events: none;
        }

        /* Subtle scanline texture */
        body::after {
            content: '';
            position: fixed; inset: 0; z-index: 0;
            background-image: repeating-linear-gradient(
                0deg, transparent, transparent 2px,
                rgba(0,0,0,0.12) 2px, rgba(0,0,0,0.12) 4px
            );
            pointer-events: none;
            opacity: 0.25;
        }

        /* ── HEADER ── */
        header {
            position: relative; z-index: 10;
            display: flex; align-items: center; justify-content: space-between;
            padding: 16px 36px;
            background: rgba(14,16,24,0.85);
            backdrop-filter: blur(24px);
            border-bottom: 1px solid var(--border2);
        }

        .header-left { display: flex; align-items: center; gap: 14px; }

        .logo-wrap {
            position: relative;
            width: 48px; height: 48px; flex-shrink: 0;
        }
        .logo-ring {
            position: absolute; inset: 0;
            border-radius: 50%;
            border: 1px dashed rgba(0,229,195,0.3);
            animation: spin 10s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .logo-inner {
            position: absolute; inset: 8px;
            background: linear-gradient(135deg, rgba(0,229,195,0.2), rgba(59,130,246,0.2));
            border: 1px solid rgba(0,229,195,0.3);
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-size: 17px;
        }

        .brand h1 {
            font-size: 16px; font-weight: 700; letter-spacing: -0.02em;
            background: linear-gradient(90deg, #fff 30%, var(--teal) 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .brand p { color: var(--muted); font-size: 10.5px; margin-top: 3px; letter-spacing: 0.07em; text-transform: uppercase; }

        .status-pill {
            display: flex; align-items: center; gap: 7px;
            padding: 7px 16px; border-radius: 999px;
            font-size: 12px; font-weight: 600;
            border: 1px solid rgba(0,229,195,0.25);
            background: rgba(0,229,195,0.07);
            color: var(--teal);
            transition: all 0.3s;
        }
        .status-pill.down {
            border-color: rgba(244,63,94,0.25);
            background: rgba(244,63,94,0.07);
            color: var(--rose);
        }
        .blink-dot {
            width: 7px; height: 7px; border-radius: 50%;
            background: var(--teal);
            box-shadow: 0 0 8px var(--teal);
            animation: blink 1.4s ease-in-out infinite;
        }
        .blink-dot.down { background: var(--rose); box-shadow: 0 0 8px var(--rose); animation: none; }
        @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.25} }

        /* ── LAYOUT ── */
        .container {
            position: relative; z-index: 5;
            max-width: 980px; margin: 32px auto; padding: 0 24px;
        }

        /* ── HERO CARD ── */
        .hero {
            background: var(--card);
            border: 1px solid var(--border2);
            border-radius: 20px;
            padding: 28px 30px;
            margin-bottom: 20px;
            display: flex; align-items: center; justify-content: space-between;
            gap: 20px; overflow: hidden; position: relative;
        }
        .hero::before {
            content: '';
            position: absolute; top: -60px; right: -60px;
            width: 220px; height: 220px;
            background: radial-gradient(circle, rgba(0,229,195,0.09) 0%, transparent 70%);
            border-radius: 50%; pointer-events: none;
        }
        .hero-left { display: flex; align-items: center; gap: 18px; }
        .hero-avatar {
            width: 58px; height: 58px; border-radius: 16px; flex-shrink: 0;
            background: linear-gradient(135deg, rgba(0,229,195,0.12), rgba(59,130,246,0.12));
            border: 1px solid rgba(0,229,195,0.2);
            display: flex; align-items: center; justify-content: center;
            font-size: 28px;
        }
        .hero-text h2 { font-size: 19px; font-weight: 700; letter-spacing: -0.02em; }
        .hero-text p {
            color: var(--muted2); font-size: 12px; margin-top: 6px;
            font-family: 'JetBrains Mono', monospace; letter-spacing: 0.01em;
        }
        .hero-right { text-align: right; flex-shrink: 0; }
        .hero-right .lbl { font-size: 10px; text-transform: uppercase; letter-spacing: 0.1em; color: var(--muted); }
        .hero-right .val {
            font-family: 'JetBrains Mono', monospace;
            font-size: 24px; font-weight: 700; color: var(--teal);
            letter-spacing: -0.02em; margin-top: 4px;
        }

        /* ── STATS GRID ── */
        .grid4 {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 14px; margin-bottom: 20px;
        }
        @media(max-width:680px){ .grid4{ grid-template-columns: repeat(2,1fr); } }

        .scard {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 20px 18px 16px;
            position: relative; overflow: hidden;
            transition: border-color 0.2s, transform 0.2s;
        }
        .scard:hover { border-color: var(--border2); transform: translateY(-2px); }
        .scard::after {
            content: '';
            position: absolute; top: 0; left: 0; right: 0;
            height: 2px; border-radius: 16px 16px 0 0;
        }
        .scard.t-teal::after   { background: linear-gradient(90deg, var(--teal),   transparent 80%); }
        .scard.t-purple::after { background: linear-gradient(90deg, var(--purple), transparent 80%); }
        .scard.t-rose::after   { background: linear-gradient(90deg, var(--rose),   transparent 80%); }
        .scard.t-blue::after   { background: linear-gradient(90deg, var(--blue),   transparent 80%); }

        .scard-icon { font-size: 20px; margin-bottom: 12px; }
        .scard-lbl  { color: var(--muted2); font-size: 10px; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 6px; }
        .scard-val  { font-family: 'JetBrains Mono', monospace; font-size: 28px; font-weight: 700; line-height: 1; }
        .c-teal   { color: var(--teal); }
        .c-purple { color: var(--purple); }
        .c-rose   { color: var(--rose); }
        .c-blue   { color: var(--blue); }
        .c-green  { color: #22c55e; }

        /* ── LOG PANEL ── */
        .panel {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 18px;
            overflow: hidden;
            margin-bottom: 16px;
        }
        .panel-top {
            display: flex; align-items: center; justify-content: space-between;
            padding: 13px 20px;
            background: var(--card2);
            border-bottom: 1px solid var(--border);
        }
        .panel-label {
            display: flex; align-items: center; gap: 8px;
            font-size: 11.5px; font-weight: 600; letter-spacing: 0.07em;
            text-transform: uppercase; color: var(--muted2);
        }
        .panel-dot {
            width: 6px; height: 6px; border-radius: 50%;
            background: var(--teal);
            animation: blink 1.4s ease-in-out infinite;
        }
        .badge-refresh {
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px; color: var(--muted);
            background: rgba(255,255,255,0.03);
            border: 1px solid var(--border);
            border-radius: 999px; padding: 3px 10px;
        }

        .log-body {
            padding: 10px 0;
            font-family: 'JetBrains Mono', monospace;
            font-size: 11.5px; line-height: 1.85;
            max-height: 290px; overflow-y: auto;
        }
        .log-body::-webkit-scrollbar { width: 3px; }
        .log-body::-webkit-scrollbar-track { background: transparent; }
        .log-body::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }

        .log-row {
            display: block; padding: 2px 20px;
            border-left: 2px solid transparent;
            color: var(--muted2);
            transition: background 0.12s;
        }
        .log-row:hover { background: rgba(255,255,255,0.022); }
        .log-row.ok  { border-left-color: var(--teal);   color: rgba(0,229,195,0.82); }
        .log-row.err { border-left-color: var(--rose);   color: rgba(244,63,94,0.82); }
        .log-row.wrn { border-left-color: var(--amber);  color: rgba(245,158,11,0.82); }

        /* ── FOOTER ── */
        footer {
            position: relative; z-index: 5;
            text-align: center; padding: 20px 0 28px;
            color: var(--muted); font-size: 11px; letter-spacing: 0.05em;
        }
        footer span { color: var(--muted2); }

        /* ── FADE-IN ANIMATION ── */
        @keyframes fadeUp {
            from { opacity:0; transform:translateY(14px); }
            to   { opacity:1; transform:translateY(0); }
        }
        .container > * { animation: fadeUp 0.45s ease both; }
        .container > *:nth-child(1){ animation-delay:0.04s; }
        .container > *:nth-child(2){ animation-delay:0.10s; }
        .container > *:nth-child(3){ animation-delay:0.17s; }
        .container > *:nth-child(4){ animation-delay:0.24s; }
    </style>
    <script>setTimeout(() => location.reload(), 20000);</script>
</head>
<body>

<!-- HEADER -->
<header>
    <div class="header-left">
        <div class="logo-wrap">
            <div class="logo-ring"></div>
            <div class="logo-inner">📢</div>
        </div>
        <div class="brand">
            <h1>Telegram Promo Bot</h1>
            <p>Automated Broadcast System</p>
        </div>
    </div>
    <div class="status-pill {{ '' if status.running else 'down' }}">
        <div class="blink-dot {{ '' if status.running else 'down' }}"></div>
        {{ 'LIVE' if status.running else 'OFFLINE' }}
    </div>
</header>

<!-- MAIN -->
<div class="container">

    <!-- Hero -->
    <div class="hero">
        <div class="hero-left">
            <div class="hero-avatar">🤖</div>
            <div class="hero-text">
                <h2>{{ 'বট সক্রিয় আছে ✓' if status.running else 'বট চালু হচ্ছে…' }}</h2>
                <p>
                    process: {{ 'RUNNING' if status.running else 'STARTING' }}
                    &nbsp;·&nbsp; auto-restart: ON
                    &nbsp;·&nbsp; render free tier
                </p>
            </div>
        </div>
        <div class="hero-right">
            <div class="lbl">শুরুর সময়</div>
            <div class="val">{{ status.started_at.split(' ')[1] if status.started_at else '--:--:--' }}</div>
        </div>
    </div>

    <!-- Stats -->
    <div class="grid4">
        <div class="scard t-teal">
            <div class="scard-icon">⚡</div>
            <div class="scard-lbl">স্ট্যাটাস</div>
            <div class="scard-val {{ 'c-teal' if status.running else 'c-rose' }}">{{ 'ON' if status.running else 'OFF' }}</div>
        </div>
        <div class="scard t-purple">
            <div class="scard-icon">🚀</div>
            <div class="scard-lbl">মেসেজ পাঠানো</div>
            <div class="scard-val c-purple">{{ status.messages_sent }}</div>
        </div>
        <div class="scard t-rose">
            <div class="scard-icon">⚠️</div>
            <div class="scard-lbl">এরর সংখ্যা</div>
            <div class="scard-val {{ 'c-rose' if status.errors else 'c-green' }}">{{ status.errors|length }}</div>
        </div>
        <div class="scard t-blue">
            <div class="scard-icon">📋</div>
            <div class="scard-lbl">লগ লাইন</div>
            <div class="scard-val c-blue">{{ status.log_lines|length }}</div>
        </div>
    </div>

    <!-- Live Log -->
    <div class="panel">
        <div class="panel-top">
            <div class="panel-label">
                <div class="panel-dot"></div>
                লাইভ লগ — সর্বশেষ ৩০ লাইন
            </div>
            <div class="badge-refresh">⟳ 20s auto-refresh</div>
        </div>
        <div class="log-body" id="logbox">
            {% for line in status.log_lines[-30:] %}
            <div class="log-row {% if '✅' in line or '🚀' in line or 'রেডি' in line %}ok{% elif '❌' in line or 'ERROR' in line %}err{% elif '⚠️' in line or '⏳' in line %}wrn{% endif %}">{{ line }}</div>
            {% else %}
            <div class="log-row">[INFO] লগ লোড হচ্ছে… কয়েক সেকেন্ড অপেক্ষা করুন।</div>
            {% endfor %}
        </div>
    </div>

    <!-- Error panel -->
    {% if status.errors %}
    <div class="panel">
        <div class="panel-top">
            <div class="panel-label" style="color:var(--rose);">
                <div class="panel-dot" style="background:var(--rose);animation:none;box-shadow:0 0 6px var(--rose);"></div>
                সর্বশেষ এরর
            </div>
        </div>
        <div class="log-body">
            {% for e in status.errors[-5:] %}
            <div class="log-row err">{{ e }}</div>
            {% endfor %}
        </div>
    </div>
    {% endif %}

</div>

<footer>
    Telegram Promo Bot &nbsp;·&nbsp; <span>Pyrogram</span> + <span>Flask</span> &nbsp;·&nbsp; Deployed on <span>Render</span>
</footer>

<script>
    const lb = document.getElementById('logbox');
    if (lb) lb.scrollTop = lb.scrollHeight;
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
            exit_code = bot_process.poll() if bot_process else None
            if exit_code is not None:
                msg = f"⚠️ main.py বন্ধ হয়ে গেছে (exit={exit_code}), রিস্টার্ট হচ্ছে..."
                logging.warning(msg)
                bot_status["log_lines"].append(msg)
                bot_status["running"] = False
                time.sleep(5)

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
