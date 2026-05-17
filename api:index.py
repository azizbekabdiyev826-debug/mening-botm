from http.server import BaseHTTPRequestHandler
import json, os, urllib.request
import anthropic

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
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(length))
            if "message" in data:
                msg = data["message"]
                uid = msg["from"]["id"]
                chat_id = msg["chat"]["id"]
                name = msg["from"].get("first_name", "")
                if "text" in msg:
                    text = msg["text"]
                    if text == "/start":
                        send(chat_id, f"Salom, {name}! 👋 Men Claude AI botman!\n\n/start - Boshlash\n/clear - Tarixni tozalash\n/help - Yordam")
                    elif text == "/clear":
                        histories[uid] = []
                        send(chat_id, "✅ Suhbat tarixi tozalandi!")
                    elif text == "/help":
                        send(chat_id, "💡 Men Claude AI asosidagi botman!\n\nQuyidagilarni qila olaman:\n- Savollarga javob berish\n- Kod yozish\n- Tarjima qilish\n- Matn yozish\n- Matematik masalalar\n- Va boshqa ko'p narsalar!")
                    else:
                        reply = ask(uid, text)
                        send(chat_id, reply)
        except Exception as e:
            print(f"Xato: {e}")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot ishlayapti!")
