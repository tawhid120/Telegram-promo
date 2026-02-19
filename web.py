import threading
import asyncio
import logging
import os
import sys
from flask import Flask, jsonify, render_template_string
from datetime import datetime

# Flask অ্যাপ
app = Flask(__name__)

# বট স্ট্যাটাস ট্র্যাক করার জন্য
bot_status = {
    "running": False,
    "started_at": None,
    "accounts_connected": 0,
    "templates_loaded": 0,
    "messages_sent": 0,
    "errors": []
}

# ---- HTML ড্যাশবোর্ড ----
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
            --bg: #0d0f1a;
            --surface: #151828;
            --card: #1c2035;
            --border: #2a3050;
            --accent: #4f8ef7;
            --accent2: #7c5af7;
            --green: #3dd68c;
            --red: #f75a5a;
            --yellow: #f7c948;
            --text: #e8eaf6;
            --muted: #6b7394;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: var(--bg);
            color: var(--text);
            font-family: 'Noto Sans Bengali', sans-serif;
            min-height: 100vh;
            background-image: radial-gradient(ellipse at 20% 20%, rgba(79,142,247,0.07) 0%, transparent 60%),
                              radial-gradient(ellipse at 80% 80%, rgba(124,90,247,0.07) 0%, transparent 60%);
        }
        header {
            background: var(--surface);
            border-bottom: 1px solid var(--border);
            padding: 20px 40px;
            display: flex;
            align-items: center;
            gap: 16px;
        }
        .logo {
            width: 44px; height: 44px;
            background: linear-gradient(135deg, var(--accent), var(--accent2));
            border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            font-size: 22px;
        }
        header h1 { font-size: 20px; font-weight: 700; }
        header p { color: var(--muted); font-size: 13px; margin-top: 2px; }
        .container { max-width: 900px; margin: 40px auto; padding: 0 24px; }
        .status-banner {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 24px 28px;
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 28px;
        }
        .pulse-dot {
            width: 14px; height: 14px;
            border-radius: 50%;
            background: var(--green);
            box-shadow: 0 0 0 0 rgba(61,214,140,0.5);
            animation: pulse 2s infinite;
            flex-shrink: 0;
        }
        .pulse-dot.offline { background: var(--red); box-shadow: 0 0 0 0 rgba(247,90,90,0.5); }
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(61,214,140,0.5); }
            70% { box-shadow: 0 0 0 10px rgba(61,214,140,0); }
            100% { box-shadow: 0 0 0 0 rgba(61,214,140,0); }
        }
        .status-text h2 { font-size: 17px; font-weight: 600; }
        .status-text p { color: var(--muted); font-size: 13px; margin-top: 4px; font-family: 'JetBrains Mono', monospace; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 28px; }
        .card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 22px 24px;
        }
        .card-label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 10px; }
        .card-value { font-size: 30px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
        .card-value.green { color: var(--green); }
        .card-value.blue { color: var(--accent); }
        .card-value.purple { color: var(--accent2); }
        .card-value.yellow { color: var(--yellow); }
        .section-title { font-size: 14px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 14px; }
        .log-box {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 20px 24px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            line-height: 1.8;
            color: var(--muted);
            max-height: 200px;
            overflow-y: auto;
        }
        .log-box .log-entry { border-bottom: 1px solid var(--border); padding: 6px 0; }
        .log-box .log-entry:last-child { border-bottom: none; }
        .log-box .ts { color: var(--accent); margin-right: 10px; }
        footer { text-align: center; color: var(--muted); font-size: 12px; padding: 40px 0 24px; }
        .refresh-note { color: var(--muted); font-size: 12px; text-align: right; margin-bottom: 8px; }
    </style>
    <script>
        // প্রতি ৩০ সেকেন্ডে পেজ রিফ্রেশ
        setTimeout(() => location.reload(), 30000);
    </script>
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
            <div class="pulse-dot {{ 'online' if status.running else 'offline' }}"></div>
            <div class="status-text">
                <h2>বট {{ 'সক্রিয় আছে ✓' if status.running else 'চালু হচ্ছে...' }}</h2>
                <p>শুরু হয়েছে: {{ status.started_at or 'N/A' }}</p>
            </div>
        </div>
        <div class="grid">
            <div class="card">
                <div class="card-label">অ্যাকাউন্ট</div>
                <div class="card-value green">{{ status.accounts_connected }}</div>
            </div>
            <div class="card">
                <div class="card-label">টেমপ্লেট</div>
                <div class="card-value blue">{{ status.templates_loaded }}</div>
            </div>
            <div class="card">
                <div class="card-label">মেসেজ পাঠানো</div>
                <div class="card-value purple">{{ status.messages_sent }}</div>
            </div>
            <div class="card">
                <div class="card-label">গ্রুপ টার্গেট</div>
                <div class="card-value yellow">{{ status.target_groups }}</div>
            </div>
        </div>
        {% if status.errors %}
        <div class="section-title">সাম্প্রতিক সমস্যা</div>
        <div class="log-box" style="margin-bottom: 20px;">
            {% for err in status.errors[-5:] %}
            <div class="log-entry"><span class="ts">⚠️</span>{{ err }}</div>
            {% endfor %}
        </div>
        {% endif %}
        <div class="refresh-note">⟳ প্রতি ৩০ সেকেন্ডে স্বয়ংক্রিয় আপডেট</div>
        <div class="section-title">সিস্টেম লগ</div>
        <div class="log-box">
            <div class="log-entry"><span class="ts">[INFO]</span> Web server চালু আছে — Render Free Tier</div>
            <div class="log-entry"><span class="ts">[INFO]</span> Background bot thread {{ 'সক্রিয়' if status.running else 'চালু হচ্ছে' }}</div>
            <div class="log-entry"><span class="ts">[INFO]</span> Target groups: {{ status.target_groups }}</div>
        </div>
    </div>
    <footer>Telegram Promo Bot &mdash; Powered by Pyrogram + Flask</footer>
</body>
</html>
"""

# ---- রুটস ----
@app.route("/")
def dashboard():
    return render_template_string(DASHBOARD_HTML, status=bot_status)

@app.route("/health")
def health():
    """Render health check endpoint"""
    return jsonify({"status": "ok", "bot_running": bot_status["running"]}), 200

@app.route("/status")
def status():
    return jsonify(bot_status)

# ---- ব্যাকগ্রাউন্ড বট রানার ----
def run_bot_in_background():
    """আলাদা থ্রেডে বটের asyncio event loop চালাবে"""
    try:
        # main.py থেকে ইম্পোর্ট করা হচ্ছে
        import main as bot_main
        import asyncio

        # স্ট্যাটাস আপডেট করার জন্য main এর ফাংশনগুলো প্যাচ করা হচ্ছে
        original_start_clients = bot_main.start_clients
        original_send_ad = bot_main.send_ad_message
        original_load_templates = bot_main.load_templates

        async def patched_start_clients():
            await original_start_clients()
            bot_status["accounts_connected"] = len(bot_main.clients)
            bot_status["running"] = True

        async def patched_send_ad(chat_id):
            await original_send_ad(chat_id)
            bot_status["messages_sent"] += 1

        def patched_load_templates():
            original_load_templates()
            bot_status["templates_loaded"] = len(bot_main.templates)

        # প্যাচ করা ফাংশন সেট
        bot_main.start_clients = patched_start_clients
        bot_main.send_ad_message = patched_send_ad
        bot_main.load_templates = patched_load_templates
        bot_status["target_groups"] = len(bot_main.TARGET_GROUPS)
        bot_status["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(bot_main.main())

    except Exception as e:
        logging.error(f"Bot thread error: {e}")
        bot_status["running"] = False
        bot_status["errors"].append(str(e))


# ---- এন্ট্রি পয়েন্ট ----
if __name__ == "__main__":
    # বটকে ব্যাকগ্রাউন্ড থ্রেডে শুরু করা
    bot_thread = threading.Thread(target=run_bot_in_background, daemon=True)
    bot_thread.start()
    logging.info("🤖 Bot thread started in background")

    # Flask সার্ভার চালু করা (Render PORT env variable ব্যবহার করে)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
