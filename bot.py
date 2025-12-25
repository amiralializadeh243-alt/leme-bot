import telebot
import requests
from flask import Flask
from threading import Thread
import time

# تنظیمات
TOKEN = '8095956559:AAGMeUTSGS9h8ZQTfPpCMHCZ5nwYBWVGTAk'
bot = telebot.TeleBot(TOKEN)
ADMIN_IDS = [8404377559]

def claim_reward(chat_id, username, password):
    try:
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'Origin': 'https://coe.leme.hk.cn',
            'Referer': 'https://coe.leme.hk.cn/m/login'
        }

        # مرحله ۱: ورود (تلاش برای دریافت توکن)
        login_url = "https://coe.leme.hk.cn/h5new/login/check"
        payload = f'account={username}&password={password}&type=1'
        
        response = session.post(login_url, data=payload, headers=headers, timeout=15)
        
        # استخراج توکن (بررسی کوکی و بدنه پاسخ)
        token = session.cookies.get('token')
        if not token and '"token":"' in response.text:
            token = response.text.split('"token":"')[1].split('"')[0]

        if token:
            # مرحله ۲: کلیک روی دکمه طلایی (تصویر ۶۰)
            action_url = "https://coe.leme.hk.cn/h5new/signin"
            headers['Referer'] = 'https://coe.leme.hk.cn/m'
            data_raw = f'token={token}'
            
            reward_res = session.post(action_url, headers=headers, data=data_raw)
            res_data = reward_res.json()
            
            msg = res_data.get('msg', 'پاسخ نامشخص')
            if res_data.get('code') == 1:
                bot.send_message(chat_id, f"✅ **عملیات موفق!**\nپاسخ سایت: {msg}")
            else:
                bot.send_message(chat_id, f"⚠️ **پیام سایت:** {msg}")
        else:
            bot.send_message(chat_id, "❌ **خطای توکن:** سایت اجازه ورود نداد. یوزرنیم و پسورد را دقیقاً مثل سایت وارد کنید.")
            
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ **خطای سیستمی:** `{str(e)[:50]}`")

@bot.message_handler(func=lambda m: m.from_user.id not in ADMIN_IDS)
def unauthorized(m):
    bot.reply_to(m, "⛔ دسترسی غیرمجاز.")

@bot.message_handler(commands=['start'])
def send_welcome(m):
    bot.reply_to(m, "🚀 **ربات لمه آماده است.**\nارسال مشخصات: `user:pass`")

@bot.message_handler(func=lambda m: ":" in m.text and m.from_user.id in ADMIN_IDS)
def handle_message(m):
    try:
        u, p = m.text.split(":")[0].strip(), m.text.split(":")[1].strip()
        bot.reply_to(m, "⌛ در حال پردازش...")
        claim_reward(m.chat.id, u, p)
    except:
        bot.reply_to(m, "❌ فرمت اشتباه است.")

# وب‌سرور رندر
app = Flask('')
@app.route('/')
def home(): return "Active"
def run(): app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True, skip_pending=True)
