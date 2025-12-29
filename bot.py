import telebot
import requests
import base64
from flask import Flask
from threading import Thread

# --- تنظیمات جدید شما ---
TOKEN = '8286464872:AAEO0JHlqMpi3vDTMxGHdUKFPfSXYVBj6Uc'
GITHUB_TOKEN = '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' 
REPO_NAME = 'amiralializadeh243-alt/leme-bot'
FILE_PATH = 'accounts.txt'

bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Manager is Online and Active!"

def save_to_github(new_entry):
    try:
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # ۱. گرفتن اطلاعات فعلی فایل
        r = requests.get(url, headers=headers)
        sha = r.json().get('sha') if r.status_code == 200 else None
        
        if sha:
            old_content = base64.b64decode(r.json()['content']).decode()
        else:
            old_content = ""

        # ۲. اضافه کردن اکانت جدید به خط بعدی
        updated_content = old_content.strip() + "\n" + new_entry
        encoded = base64.b64encode(updated_content.encode()).decode()

        # ۳. آپدیت فایل در گیت‌هاب
        payload = {
            "message": "Add new account via Telegram",
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
def send_welcome(m):
    bot.reply_to(m, "سلام! اکانت را به صورت `user:pass` بفرست تا ذخیره شود.")

@bot.message_handler(func=lambda m: ":" in m.text)
def handle_account(m):
    if save_to_github(m.text.strip()):
        bot.reply_to(m, "✅ اکانت با موفقیت در لیست گیت‌هاب ذخیره شد.")
    else:
        bot.reply_to(m, "❌ خطا در ذخیره‌سازی. دسترسی ghp گیت‌هاب را چک کنید.")

def run():
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    # اجرای وب‌سرور در یک ترد جداگانه برای زنده نگه داشتن رندر
    Thread(target=run).start()
    # اجرای ربات تلگرام
    bot.polling(none_stop=True)
