import telebot
import requests
import re
from flask import Flask
from threading import Thread

# --- تنظیمات ---
TOKEN = '8095956559:AAGMeUTSGS9h8ZQTfPpCMHCZ5nwYBWVGTAk'
ADMIN_ID = '8404377559'
bot = telebot.TeleBot(TOKEN)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://coe.leme.hk.cn/m/',
}

def claim_reward(chat_id, username, password):
    try:
        session = requests.Session()
        # ۱. ورود
        login_url = "https://coe.leme.hk.cn/login/check"
        payload = {'account': username, 'password': password, 'type': '1'}
        res = session.post(login_url, data=payload, headers=HEADERS)
        
        if res.status_code == 200:
            # ۲. دریافت صفحه جوایز برای استخراج لینک فعال (حل مشکل تصویر ۴۹)
            reward_page = session.get("https://coe.leme.hk.cn/m/sign/check_in", headers=HEADERS)
            
            # ۳. ارسال درخواست کلیک به آدرس عملیاتی اصلی
            # آدرس عملیاتی معمولاً sign_in_handler است
            final_url = "https://coe.leme.hk.cn/m/sign/sign_in_handler"
            response = session.post(final_url, headers=HEADERS)
            
            # بررسی دقیق پاسخ سایت
            if response.status_code == 200:
                res_data = response.text.lower()
                if '"code":1' in res_data or "success" in res_data:
                    bot.send_message(chat_id, "✅ تبریک! دکمه طلایی با موفقیت زده شد.")
                elif '"code":0' in res_data or "already" in res_data:
                    bot.send_message(chat_id, "⚠️ شما امروز قبلاً جایزه را دریافت کرده‌اید.")
                else:
                    bot.send_message(chat_id, "✅ عملیات انجام شد. لطفاً ایمیل‌های داخل بازی را چک کنید.")
            else:
                bot.send_message(chat_id, "❌ خطا در مرحله نهایی کلیک.")
        else:
            bot.send_message(chat_id, "❌ یوزرنیم یا پسورد اشتباه است.")
    except:
        bot.send_message(chat_id, "⚠️ خطای فنی در اتصال.")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "✅ ربات آماده است. مشخصات را بفرستید: `user:pass`")

@bot.message_handler(func=lambda message: ":" in message.text)
def handle_message(message):
    u, p = message.text.split(":")[0].strip(), message.text.split(":")[1].strip()
    bot.reply_to(message, f"⌛ در حال زدن دکمه طلایی برای `{u}`...")
    claim_reward(message.chat.id, u, p)

# رفع ارور Port Scan رندر
app = Flask('')
@app.route('/')
def home(): return "Live"
def run(): app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
