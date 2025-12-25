import telebot
import requests
from flask import Flask
from threading import Thread

# --- تنظیمات امنیتی ---
TOKEN = '8095956559:AAGMeUTSGS9h8ZQTfPpCMHCZ5nwYBWVGTAk'
bot = telebot.TeleBot(TOKEN)

# لیست سفید: فقط آی‌دی شما مجاز است
ADMIN_IDS = [8404377559] 

def claim_reward(chat_id, username, password):
    try:
        session = requests.Session()
        # ۱. ورود و دریافت توکن زنده
        login_url = "https://coe.leme.hk.cn/login/check"
        payload = {'account': username, 'password': password, 'type': '1'}
        headers_base = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*'
        }
        session.post(login_url, data=payload, headers=headers_base, timeout=15)
        
        user_token = session.cookies.get('token')
        
        if user_token:
            # ۲. بازسازی حرکت ضبط شده (بر اساس cURL شما)
            action_url = "https://coe.leme.hk.cn/h5new/signin"
            action_headers = {
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                'Origin': 'https://coe.leme.hk.cn',
                'Referer': 'https://coe.leme.hk.cn/m',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest'
            }
            data_raw = f'token={user_token}'
            response = session.post(action_url, headers=action_headers, data=data_raw)
            
            res_json = response.json()
            msg = res_json.get('msg', 'پاسخی دریافت نشد')
            
            if res_json.get('code') == 1 or "success" in msg.lower():
                bot.send_message(chat_id, "✅ **عملیات موفق!** دکمه طلایی با آی‌دی شما زده شد.")
            else:
                bot.send_message(chat_id, f"⚠️ **پیام سایت:** {msg}")
        else:
            bot.send_message(chat_id, "❌ خطای ورود: توکن یافت نشد.")
            
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ خطای فنی: `{str(e)[:40]}`")

# مسدود کردن افراد غیرمجاز
@bot.message_handler(func=lambda message: message.from_user.id not in ADMIN_IDS)
def unauthorized_access(message):
    bot.reply_to(message, "⛔ شما مجاز به استفاده از این ربات نیستید.")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🚀 **ربات اختصاصی شما فعال است.**\nمشخصات را بفرستید: `user:pass`")

@bot.message_handler(func=lambda message: ":" in message.text and message.from_user.id in ADMIN_IDS)
def handle_message(message):
    u, p = message.text.split(":")[0].strip(), message.text.split(":")[1].strip()
    bot.reply_to(message, "⌛ در حال اجرای عملیات اختصاصی...")
    claim_reward(message.chat.id, u, p)

# وب‌سرور رندر
app = Flask('')
@app.route('/')
def home(): return "Private Bot Active"
def run(): app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True, skip_pending=True)
