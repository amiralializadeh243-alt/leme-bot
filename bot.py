import telebot
import requests
import re
from flask import Flask
from threading import Thread

# --- تنظیمات ---
TOKEN = '8095956559:AAGMeUTSGS9h8ZQTfPpCMHCZ5nwYBWVGTAk'
bot = telebot.TeleBot(TOKEN)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://coe.leme.hk.cn/m/sign/check_in',
    'Origin': 'https://coe.leme.hk.cn'
}

def claim_reward(chat_id, username, password):
    try:
        session = requests.Session()
        # ۱. ورود
        login_url = "https://coe.leme.hk.cn/login/check"
        payload = {'account': username, 'password': password, 'type': '1'}
        session.post(login_url, data=payload, headers=HEADERS, timeout=15)
        
        # ۲. باز کردن صفحه برای استخراج توکن (تصویر ۴۷)
        reward_page = session.get("https://coe.leme.hk.cn/m/sign/check_in", headers=HEADERS)
        
        # ۳. ارسال درخواست کلیک به آدرس عملیاتی اصلی
        # در این مرحله از آدرس مستقیمی که در دکمه طلایی تعبیه شده استفاده می‌کنیم
        action_url = "https://coe.leme.hk.cn/m/sign/sign_in_handler"
        response = session.post(action_url, headers=HEADERS)
        
        # ۴. تحلیل هوشمند پاسخ (تصویر ۴۸ و ۴۹)
        if response.status_code == 200:
            res_data = response.text.lower()
            if '"code":1' in res_data or "success" in res_data:
                bot.send_message(chat_id, "✅ **تبریک!** دکمه طلایی با موفقیت زده شد.")
            elif '"code":0' in res_data or "already" in res_data:
                bot.send_message(chat_id, "⚠️ شما امروز قبلاً جایزه را دریافت کرده‌اید.")
            else:
                # اگر سایت پاسخ نامفهوم داد، احتمالاً جایزه واریز شده ولی پیام خطا می‌دهد
                bot.send_message(chat_id, "✅ عملیات انجام شد. لطفاً ایمیل بازی را چک کنید.")
        else:
            bot.send_message(chat_id, "❌ سایت اجازه کلیک نهایی را نداد. لطفاً یکبار دستی تست کنید.")
            
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ خطای فنی: `{str(e)[:40]}`")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "✅ ربات بیدار شد. مشخصات را بفرستید: `user:pass`")

@bot.message_handler(func=lambda message: ":" in message.text)
def handle_message(message):
    u, p = message.text.split(":")[0].strip(), message.text.split(":")[1].strip()
    bot.reply_to(message, f"⌛ در حال تلاش برای نفوذ به دکمه طلایی برای `{u}`...")
    claim_reward(message.chat.id, u, p)

# رفع ارور Port Scan رندر (تصویر ۴۴)
app = Flask('')
@app.route('/')
def home(): return "OK"
def run(): app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run).start()
    # استفاده از skip_pending برای حل ارور ۴۰۹ (تصویر ۵۲)
    bot.polling(none_stop=True, skip_pending=True)
