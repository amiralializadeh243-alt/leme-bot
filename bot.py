import telebot
import requests
from flask import Flask
from threading import Thread

# --- تنظیمات ---
TOKEN = '8095956559:AAGMeUTSGS9h8ZQTfPpCMHCZ5nwYBWVGTAk'
bot = telebot.TeleBot(TOKEN)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://coe.leme.hk.cn/m/sign/check_in',
    'Origin': 'https://coe.leme.hk.cn',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
}

def claim_reward(chat_id, username, password):
    try:
        session = requests.Session()
        # ۱. ورود و دریافت کوکی‌ها
        login_url = "https://coe.leme.hk.cn/login/check"
        payload = {'account': username, 'password': password, 'type': '1'}
        session.post(login_url, data=payload, headers=HEADERS, timeout=15)
        
        # ۲. حرکت مستقیم به سمت دکمه طلایی (Sign-in Handler)
        action_url = "https://coe.leme.hk.cn/m/sign/sign_in_handler"
        response = session.post(action_url, headers=HEADERS)
        
        # ۳. تحلیل پاسخ (بر اساس تصاویر ۴۸ و ۴۹)
        res_text = response.text.lower()
        if '"code":1' in res_text or "success" in res_text:
            bot.send_message(chat_id, "✅ **عملیات موفقیت‌آمیز!**\nدکمه طلایی زده شد. جایزه را در ایمیل بازی چک کنید.")
        elif '"code":0' in res_text or "already" in res_text:
            bot.send_message(chat_id, "⚠️ **تکراری:** جایزه امروز قبلاً دریافت شده است.")
        else:
            bot.send_message(chat_id, "❌ سایت وارد شد اما دکمه عمل نکرد. احتمالاً پاسخ سایت تغییر کرده است.")
            
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ خطای فنی: `{str(e)[:40]}`")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "✅ **ربات آنلاین شد.**\nمشخصات را بفرستید: `user:pass`")

@bot.message_handler(func=lambda message: ":" in message.text)
def handle_message(message):
    u, p = message.text.split(":")[0].strip(), message.text.split(":")[1].strip()
    bot.reply_to(message, "⌛ در حال تلاش برای کلیک روی دکمه طلایی...")
    claim_reward(message.chat.id, u, p)

# وب‌سرور برای زنده نگه داشتن سرویس در رندر (تصویر ۴۴)
app = Flask('')
@app.route('/')
def home(): return "Active"
def run(): app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run).start()
    # استفاده از skip_pending برای حل قطعی ارور ۴۰۹ (تصویر ۵۲)
    bot.polling(none_stop=True, skip_pending=True)
