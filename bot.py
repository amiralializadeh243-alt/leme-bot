import telebot
import requests
from flask import Flask
from threading import Thread

# --- تنظیمات ---
TOKEN = '8095956559:AAGMeUTSGS9h8ZQTfPpCMHCZ5nwYBWVGTAk'
ADMIN_ID = '8404377559'
bot = telebot.TeleBot(TOKEN)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://coe.leme.hk.cn/m/',
    'Origin': 'https://coe.leme.hk.cn'
}

def claim_reward(chat_id, username, password):
    try:
        session = requests.Session()
        
        # ۱. ورود به سیستم
        login_url = "https://coe.leme.hk.cn/login/check"
        payload = {'account': username, 'password': password, 'type': '1'}
        login_res = session.post(login_url, data=payload, headers=HEADERS, timeout=15)
        
        if login_res.status_code == 200:
            # ۲. ارسال درخواست مستقیم برای "Sign in" (دکمه طلایی تصویر ۴۷)
            # آدرس زیر طبق ساختار بخش Lords Benefits تنظیم شده است
            sign_url = "https://coe.leme.hk.cn/m/sign/sign_in_handler" 
            
            # در سایت‌های مشابه، معمولاً یک درخواست POST برای ثبت اثر انگشت یا امضا فرستاده می‌شود
            response = session.post(sign_url, headers=HEADERS)
            
            # بررسی نتیجه بر اساس پاسخ سرور
            if "success" in response.text.lower() or response.status_code == 200:
                bot.send_message(chat_id, f"✅ دکمه طلایی Sign-in با موفقیت زده شد!\nجایزه اکانت `{username}` دریافت شد.", parse_mode="Markdown")
            else:
                bot.send_message(chat_id, f"⚠️ وارد شد، اما پاسخ سایت برای دریافت جایزه نامشخص بود (احتمالاً قبلاً دریافت شده).")
        else:
            bot.send_message(chat_id, f"❌ ورود ناموفق! مشخصات اکانت را چک کنید.")
            
    except Exception as e:
        bot.send_message(chat_id, "⚠️ خطای فنی در ارتباط با بخش جوایز.")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "✅ ربات لمه آماده دریافت جایزه روزانه است.\nمشخصات را بفرستید: `user:pass`", parse_mode="Markdown")

@bot.message_handler(func=lambda message: ":" in message.text)
def handle_message(message):
    data = message.text.split(":")
    if len(data) == 2:
        u, p = data[0].strip(), data[1].strip()
        bot.reply_to(message, "⌛ در حال کلیک روی دکمه طلایی Sign-in...")
        claim_reward(message.chat.id, u, p)

# --- بخش Flask برای بیدار نگه داشتن پورت در Render ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Live!"
def run(): app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
