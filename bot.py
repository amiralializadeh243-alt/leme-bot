import telebot
import requests
from flask import Flask
from threading import Thread

# --- تنظیمات اختصاصی ---
TOKEN = '8095956559:AAGMeUTSGS9h8ZQTfPpCMHCZ5nwYBWVGTAk'
bot = telebot.TeleBot(TOKEN)

# هدرهای پیشرفته برای دسترسی مستقیم و بدون واسطه به دکمه (تصویر ۴۷)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://coe.leme.hk.cn/m/sign/check_in',
    'Origin': 'https://coe.leme.hk.cn',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
}

def claim_reward(chat_id, username, password):
    try:
        session = requests.Session()
        
        # ۱. ورود مستقیم به اکانت (Login)
        login_url = "https://coe.leme.hk.cn/login/check"
        payload = {'account': username, 'password': password, 'type': '1'}
        login_res = session.post(login_url, data=payload, headers=HEADERS, timeout=15)
        
        if login_res.status_code == 200:
            # ۲. شبیه‌سازی حضور در صفحه برای ست شدن کوکی امنیتی (تصویر ۴۷)
            session.get("https://coe.leme.hk.cn/m/sign/check_in", headers=HEADERS)
            
            # ۳. حمله مستقیم به آدرس دکمه طلایی (Direct Action)
            # این همان مسیری است که دکمه طلایی در پشت صحنه طی می‌کند
            action_url = "https://coe.leme.hk.cn/m/sign/sign_in_handler"
            response = session.post(action_url, headers=HEADERS)
            
            # تحلیل پاسخ سرور (حل مشکل تصاویر ۴۹ و ۵۴)
            try:
                data = response.json()
                msg = data.get('msg', '').lower()
                code = data.get('code', -1)
                
                if code == 1 or "success" in msg:
                    bot.send_message(chat_id, "✅ **عملیات مستقیم موفقیت‌آمیز بود!**\nدکمه طلایی زده شد و جایزه به ایمیل بازی ارسال گشت.")
                elif code == 0 or "already" in msg:
                    bot.send_message(chat_id, "⚠️ **تکراری:** جایزه امروز قبلاً دریافت شده است.")
                else:
                    bot.send_message(chat_id, f"❌ **پاسخ سایت:** {data.get('msg', 'نامشخص')}")
            except:
                # اگر سایت پاسخ غیر JSON داد
                if "success" in response.text.lower():
                    bot.send_message(chat_id, "✅ عملیات احتمالاً موفق بود (تایید متنی دریافت شد).")
                else:
                    bot.send_message(chat_id, "❌ خطا: سایت اجازه کلیک مستقیم را نداد.")
        else:
            bot.send_message(chat_id, "❌ ورود ناموفق! نام کاربری یا رمز عبور اشتباه است.")
            
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ خطای فنی: `{str(e)[:40]}`")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🤖 **ربات لمه آنلاین شد.**\nمشخصات را بفرستید: `user:pass`")

@bot.message_handler(func=lambda message: ":" in message.text)
def handle_message(message):
    try:
        u, p = message.text.split(":")[0].strip(), message.text.split(":")[1].strip()
        bot.reply_to(message, f"⌛ در حال حرکت مستقیم به سمت دکمه طلایی برای `{u}`...")
        claim_reward(message.chat.id, u, p)
    except:
        bot.reply_to(message, "❌ فرمت اشتباه! مثال: `ali:123456`")

# --- بخش حیاتی برای Render (حل ارور Port Scan) ---
app = Flask('')
@app.route('/')
def home(): return "Bot is running!"
def run(): app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run).start()
    # حل ارور تداخل ۴۰۹ با نادیده گرفتن پیام‌های قدیمی (تصویر ۵۲)
    bot.polling(none_stop=True, skip_pending=True)
