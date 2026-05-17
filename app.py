from flask import Flask, request
import json, os, urllib.request
import anthropic

app_flask = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_TOKEN")
API_KEY = os.environ.get("ANTHROPIC_API_KEY")
histories = {}
client = anthropic.Anthropic(api_key=API_KEY)

def ask(uid, text):
    histories.setdefault(uid, []).append({"role": "user", "content": text})
    if len(histories[uid]) > 20:
        histories[uid] = histories[uid][-20:]
    r = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system="Siz foydali AI yordamchisiz. Foydalanuvchi tilida gaplashing.",
        messages=histories[uid]
    )
    reply = r.content[0].text
    histories[uid].append({"role": "assistant", "content": reply})
    return reply

def send(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = json.dumps({"chat_id": chat_id, "text": text}).encode()
    urllib.request.urlopen(urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}))

@app_flask.route("/", methods=["GET"])
def index():
    return "Bot ishlayapti!"

@app_flask.route("/", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        if "message" in data:
            msg = data["message"]
            uid = msg["from"]["id"]
            chat_id = msg["chat"]["id"]
            name = msg["from"].get("first_name", "")
            text = msg.get("text", "")
            if text == "/start":
                send(chat_id, f"Salom, {name}! 👋 Men Claude AI botman!\n/clear - Tarixni tozalash")
            elif text == "/clear":
                histories[uid] = []
                send(chat_id, "✅ Tozalandi!")
            else:
                send(chat_id, ask(uid, text))
    except Exception as e:
        print(e)
    return "ok"
