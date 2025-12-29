import telebot
import requests
import base64
from flask import Flask
from threading import Thread

# --- تنظیمات نهایی ---
# توکن تلگرام جدید شما
TOKEN = '8286464872:AAH_OQucZjTly3CRg71vWxjdpVLUkuKCCvA' 

# توکن گیت‌هاب جدیدی که ساختی را اینجا قرار بده
GITHUB_TOKEN = 'توکن_جدید_گیت_هاب_را_اینجا_بگذار' 

REPO_NAME = 'amiralializadeh243-alt/leme-bot'
FILE_PATH = 'accounts.txt'

bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Bot is Running and Safe!"

def save_to_github(new_entry):
    try:
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # ۱. دریافت وضعیت فعلی فایل
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            content_data = r.json()
            sha = content_data['sha']
            old_content = base64.b64decode(content_data['content']).decode()
        else:
            sha = None
            old_content = ""

        # ۲. اضافه کردن اکانت جدید به انتهای فایل
        new_content = old_content.strip() + "\n" + new_entry + "\n"
        encoded = base64.b64encode(new_content.encode()).decode()

        # ۳. ارسال و آپدیت در گیت‌هاب
        payload = {
            "message": "Update via Bot",
            "content": encoded
        }
        if sha:
            payload["sha"] = sha

        res = requests.put(url, headers=headers, json=payload)
        return res.status_code in [200, 201]
    except Exception as e:
        print(f"Error: {e}")
        return False

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "ربات بیدار شد! اکانت‌ها را با فرمت user:pass بفرست.")

@bot.message_handler(func=lambda m: ":" in m.text)
def handle_account(m):
    if save_to_github(m.text.strip()):
        bot.reply_to(m, "✅ با موفقیت در لیست گیت‌هاب ذخیره شد.")
    else:
        bot.reply_to(m, "❌ خطا! احتمالاً توکن مسدود شده است. بخش Security را در گیت‌هاب چک کنید.")

def run():
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
