import telebot
import requests
import base64
from flask import Flask
from threading import Thread

# --- تنظیمات نهایی ---
TOKEN = '8286464872:AAEO0JHlqMpi3vDTMxGHdUKFPfSXYVBj6Uc'
GITHUB_TOKEN = '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'
REPO_NAME = 'amiralializadeh243-alt/leme-bot'
FILE_PATH = 'accounts.txt'

bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Bot is Live and Ready!"

def save_to_github(new_entry):
    try:
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            content_data = r.json()
            sha = content_data['sha']
            old_content = base64.b64decode(content_data['content']).decode()
        else:
            sha = None
            old_content = ""

        updated_content = old_content.strip() + "\n" + new_entry + "\n"
        encoded = base64.b64encode(updated_content.encode()).decode()

        payload = {
            "message": "Add account via Bot",
            "content": encoded
        }
        if sha:
            payload["sha"] = sha

        res = requests.put(url, headers=headers, json=payload)
        return res.status_code in [200, 201]
    except:
        return False

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "ربات بیدار است! اکانت را به صورت user:pass بفرستید.")

@bot.message_handler(func=lambda m: ":" in m.text)
def handle(m):
    if save_to_github(m.text.strip()):
        bot.reply_to(m, "✅ با موفقیت در گیت‌هاب ذخیره شد.")
    else:
        bot.reply_to(m, "❌ خطا در ذخیره‌سازی! دسترسی توکن را چک کنید.")

def run():
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
