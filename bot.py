import telebot
import requests
import base64
from flask import Flask
from threading import Thread

# --- تنظیمات شما ---
TOKEN = '8286464872:AAE1E1FQt5A52mOKFo5Sewq48vhG1ubJlN8'
GITHUB_TOKEN = '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' # توکن ghp خود را اینجا بگذارید
REPO_NAME = 'amiralializadeh243-alt/leme-bot'
FILE_PATH = 'accounts.txt'

bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home(): return "Manager is Online"

def save_to_github(new_entry):
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    r = requests.get(url, headers=headers)
    sha = r.json().get('sha') if r.status_code == 200 else None
    old_content = base64.b64decode(r.json()['content']).decode() if sha else ""
    updated_content = old_content.strip() + "\n" + new_entry
    encoded = base64.b64encode(updated_content.encode()).decode()
    payload = {"message": "Add account via Bot", "content": encoded}
    if sha: payload["sha"] = sha
    res = requests.put(url, headers=headers, json=payload)
    return res.status_code in [200, 201]

@bot.message_handler(func=lambda m: ":" in m.text)
def handle_account(m):
    if save_to_github(m.text.strip()):
        bot.reply_to(m, "✅ اکانت در لیست ذخیره شد.")
    else:
        bot.reply_to(m, "❌ خطا در اتصال به گیت‌هاب. دسترسی ghp را چک کنید.")

def run(): app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
