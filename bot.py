import telebot
import requests
from flask import Flask
from threading import Thread
import time

TOKEN = '8095956559:AAGMeUTSGS9h8ZQTfPpCMHCZ5nwYBWVGTAk'
bot = telebot.TeleBot(TOKEN)
ADMIN_IDS = [8404377559]

def auto_login_and_claim(chat_id, username, password):
    try:
        session = requests.Session()
        # هدرهای کاملاً شبیه‌سازی شده مرورگر برای عبور از تشخیص ربات
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'Origin': 'https://coe.leme.hk.cn',
            'Referer': 'https://coe.leme.hk.cn/m/login'
        }

        # ۱. تلاش برای ورود مستقیم به سیستم جدید
        login_url = "https://coe.leme.hk.cn/h5new/login"
        # ارسال یوزرنیم و پسورد به شکلی که سایت در نسخه جدید h5new می‌پذیرد
        login_payload = {
            'username': username,
            'password': password,
            'webRegion': '2'
        }
        
        bot.send_message(chat_id, f"⌛ شروع عملیات اتوماتیک برای اکانت `{username}`...")
        login_res = session.post(login_url, data=login_payload, headers=headers, timeout=15)
        
        # ۲. استخراج توکن از کوکی‌های ایجاد شده توسط سایت
        token = session.cookies.get('token')
        
        if token:
            # ۳. زدن دکمه طلایی بلافاصله بعد از لاگین
            signin_url = "https://coe.leme.hk.cn/h5new/signin"
            signin_payload = f'token={token}'
            headers['Referer'] = 'https://coe.leme.hk.cn/m'
            
            response = session.post(signin_url, data=signin_payload, headers=headers)
            res_json = response.json()
            
            msg = res_json.get('msg', 'پاسخی دریافت نشد')
            if res_json.get('code') == 1:
                bot.send_message(chat_id, f"✅ **موفقیت‌آمیز!**\nجایزه دریافت شد: {msg}")
            else:
                bot.send_message(chat_id, f"⚠️ **وضعیت:** {msg}")
        else:
            # اگر لاگین مستقیم شکست خورد، از متد "حساب کاربری مستقیم" استفاده می‌کنیم
            bot.send_message(chat_id, "❌ سایت اجازه ورود مستقیم به ربات را نمی‌دهد (امنیت بالا).")

    except Exception as e:
        bot.send_message(chat_id, f"⚠️ خطای غیرمنتظره: `{str(e)[:50]}`")

@bot.message_handler(commands=['start'])
def start(m):
    if m.from_user.id in ADMIN_IDS:
        bot.reply_to(m, "🤖 ربات اتوماتیک لمه فعال است.\nبرای اجرای خودکار، یوزرنیم و پسورد را بفرستید:\n`user:pass`")

@bot.message_handler(func=lambda m: ":" in m.text and m.from_user.id in ADMIN_IDS)
def handle_auto(m):
    u, p = m.text.split(":")[0].strip(), m.text.split(":")[1].strip()
    auto_login_and_claim(m.chat.id, u, p)

app = Flask('')
@app.route('/')
def home(): return "Bot is Running"
def run(): app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True, skip_pending=True)
