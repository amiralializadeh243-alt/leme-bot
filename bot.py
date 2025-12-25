import telebot
import requests
import base64
import os
from flask import Flask
from threading import Thread

# --- تنظیمات ---
TOKEN = '8095956559:AAGMeUTSGS9h8ZQTfPpCMHCZ5nwYBWVGTAk'
GITHUB_TOKEN = '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' 
REPO_NAME = 'amiralializadeh243-alt/leme-bot' 
FILE_PATH = 'accounts.txt'

bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home(): return "Bot is running!"

def save_to_github(new_entry):
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    r = requests.get(url, headers=headers)
    sha = r.json().get('sha') if r.status_code == 200 else None
    old_content = base64.b64decode(r.json()['content']).decode() if sha else ""
    updated_content = old_content.strip() + "\n" + new_entry
    encoded = base64.b64encode(updated_content.encode()).decode()
    payload = {"message": "Update via Telegram", "content": encoded}
    if sha: payload["sha"] = sha
    res = requests.put(url, headers=headers, json=payload)
    return res.status_code in [200, 201]

@bot.message_handler(func=lambda m: ":" in m.text)
def handle_account(m):
    if save_to_github(m.text.strip()):
        bot.reply_to(m, f"✅ حساب ثبت شد و هر روز صبح اجرا می‌شود.")
    else:
        bot.reply_to(m, "❌ خطا در ذخیره‌سازی در گیت‌هاب.")

def run():
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.polling(none_stop=True)
