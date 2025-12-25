import telebot
import requests
from flask import Flask
from threading import Thread

# --- تنظیمات اختصاصی ---
# توکن و آیدی ادمین طبق اطلاعات قبلی شما
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
    """تابع ورود و کلیک روی دکمه طلایی Sign-in"""
    try:
        session = requests.Session()
        
        # ۱. مرحله ورود به سایت
        login_url = "https://coe.leme.hk.cn/login/check"
        payload = {'account': username, 'password': password, 'type': '1'}
        login_res = session.post(login_url, data=payload, headers=HEADERS, timeout=15)
        
        if login_res.status_code == 200:
            # ۲. ارسال درخواست مستقیم برای ثبت جایزه (دکمه طلایی تصویر ۴۷)
            # از متد POST برای ارسال دستور Sign-in استفاده می‌کنیم
            sign_url = "https://coe.leme.hk.cn/m/sign/check_in" 
            response = session.post(sign_url, headers=HEADERS)
            
            # تحلیل پاسخ سرور برای رفع مشکل "پاسخ نامشخص" در تصویر ۴۸
            res_text = response.text.lower()
            
            if '"code":1' in res_text or "success" in res_text:
                bot.send_message(chat_id, f"✅ **تبریک!**\nدکمه طلایی Sign-in با موفقیت زده شد و جایزه اکانت `{username}` دریافت گشت.", parse_mode="Markdown")
                bot.send_message(ADMIN_ID, f"🤖 موفقیت برای: `{username}`")
            elif '"code":0' in res_text or "already" in res_text:
                bot.send_message(chat_id, f"⚠️ اکانت `{username}` امروز قبلاً جایزه را دریافت کرده است.", parse_mode="Markdown")
            else:
                bot.send_message(chat_id, f"❌ وارد شد، اما دکمه عمل نکرد.\nپاسخ سایت: `{response.text[:50]}`", parse_mode="Markdown")
        else:
            bot.send_message(chat_id, f"❌ ورود ناموفق! نام کاربری یا رمز عبور اکانت `{username}` اشتباه است.", parse_mode="Markdown")
            
    except Exception as e:
        bot.send_message(chat_id, "⚠️ خطای فنی در ارتباط با سرور سایت لمه.")
        print(f"Error: {e}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "✅ **ربات لمه آماده است.**\nلطفاً مشخصات خود را به صورت زیر بفرستید:\n\n`user:pass`", parse_mode="Markdown")

@bot.message_handler(func=lambda message: ":" in message.text)
def handle_message(message):
    try:
        data = message.text.split(":")
        if len(data) == 2:
            u, p = data[0].strip(), data[1].strip()
            bot.reply_to(message, f"⌛ در حال کلیک روی دکمه طلایی Sign-in برای `{u}`...")
            claim_reward(message.chat.id, u, p)
    except:
        bot.reply_to(message, "❌ فرمت اشتباه! مثال: `ali:123456`")

# --- بخش رفع ارور Port Scan در Render ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    # پورت ۱۰۰۰۰ برای راضی نگه داشتن سرور رندر
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    # اجرای وب‌سرور در یک رشته جداگانه
    Thread(target=run).start()
    print("Bot is starting...")
    bot.polling(none_stop=True)
