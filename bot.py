import telebot
import requests
import base64
import os
from flask import Flask
from threading import Thread

# --- تنظیمات ---
# ابتدا توکن‌ها را در پنل Render تعریف کنید، سپس کد زیر آن‌ها را می‌خواند
TOKEN = os.getenv('TELEGRAM_TOKEN', '8286464872:AAH_OQucZjTly3CRg71vWxjdpVLUkuKCCvA')
GITHUB_TOKEN = os.getenv('G_TOKEN') # توکن گیت‌هاب را در Render وارد کنید

REPO_NAME = 'amiralializadeh243-alt/leme-bot'
FILE_PATH = 'accounts.txt'

bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Bot is Running Securely!"

def save_to_github(new_entry):
    if not GITHUB_TOKEN:
        print("Error: GITHUB_TOKEN is not set in Environment Variables")
        return False
    try:
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        
        r = requests.get(url, headers=headers)
        sha = r.json().get('sha') if r.status_code == 200 else None
        old_content = base64.b64decode(r.json()['content']).decode() if sha else ""

        new_content = old_content.strip() + "\n" + new_entry + "\n"
        payload = {
            "message": "Secure Update",
            "content": base64.b64encode(new_content.encode()).decode(),
            "sha": sha
        } if sha else {
            "message": "Initial Entry",
            "content": base64.b64encode(new_content.encode()).decode()
        }

        res = requests.put(url, headers=headers, json=payload)
        return res.status_code in [200, 201]
    except:
        return False

@bot.message_handler(func=lambda m: ":" in m.text)
def handle_account(m):
    if save_to_github(m.text.strip()):
        bot.reply_to(m, "✅ در گیت‌هاب ذخیره شد.")
    else:
        bot.reply_to(m, "❌ خطا در دسترسی! تنظیمات Environment را چک کنید.")

def run():
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
