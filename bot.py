import telebot
import requests
import os

# --- تنظیمات اختصاصی ---
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
    """تابع اصلی برای ورود و دریافت آنی جایزه"""
    try:
        session = requests.Session()
        login_url = "https://coe.leme.hk.cn/login/check"
        payload = {'account': username, 'password': password, 'type': '1'}
        
        # ۱. تلاش برای ورود
        login_res = session.post(login_url, data=payload, headers=HEADERS, timeout=15)
        
        if login_res.status_code == 200:
            # ۲. تلاش برای کلیک روی دکمه دریافت جایزه
            reward_url = "https://coe.leme.hk.cn/m/sign/check_in" 
            reward_res = session.get(reward_url, headers=HEADERS)
            
            if "success" in reward_res.text.lower() or reward_res.status_code == 200:
                bot.send_message(chat_id, f"✅ تبریک! جایزه روزانه برای اکانت `{username}` با موفقیت دریافت شد.", parse_mode="Markdown")
                bot.send_message(ADMIN_ID, f"🤖 عملیات موفق برای: `{username}`")
            else:
                bot.send_message(chat_id, f"⚠️ وارد اکانت شد، اما دکمه جایزه در دسترس نبود (احتمالاً قبلاً دریافت شده).")
        else:
            bot.send_message(chat_id, f"❌ ورود ناموفق! مشخصات اکانت `{username}` را چک کنید.")
    except Exception as e:
        bot.send_message(chat_id, "⚠️ خطای فنی در ارتباط با سایت لمه.")
        print(f"Error: {e}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "✅ ربات لمه آماده است.\nلطفاً مشخصات را به صورت زیر بفرستید:\n\n`user:pass`", parse_mode="Markdown")

@bot.message_handler(func=lambda message: ":" in message.text)
def handle_message(message):
    try:
        data = message.text.split(":")
        username = data[0].strip()
        password = data[1].strip()

        bot.reply_to(message, f"⌛ در حال بررسی و دریافت جایزه برای `{username}`...")
        
        # اجرای آنی عملیات
        claim_reward(message.chat.id, username, password)
        
    except Exception as e:
        bot.reply_to(message, "❌ فرمت ارسالی اشتباه است. مثال: `ali:123456`")

if __name__ == "__main__":
    # اضافه کردن یک سرور مجازی کوچک برای جلوگیری از ارور Port Scan در Render
    from flask import Flask
    from threading import Thread

    app = Flask('')

    @app.route('/')
    def home():
        return "Bot is alive!"

    def run():
        app.run(host='0.0.0.0', port=10000)

    # اجرای وب‌سرور در پس‌زمینه برای راضی نگه داشتن Render
    Thread(target=run).start()
    
    print("Bot is starting...")
    bot.polling(none_stop=True)
