import telebot
import requests
from flask import Flask
from threading import Thread

TOKEN = '8095956559:AAGMeUTSGS9h8ZQTfPpCMHCZ5nwYBWVGTAk'
bot = telebot.TeleBot(TOKEN)

# هدرهای کاملاً مشابه مرورگر کروم موبایل برای دور زدن سیستم تشخیص ربات
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.9',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'https://coe.leme.hk.cn',
    'Referer': 'https://coe.leme.hk.cn/m/sign/check_in',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin'
}

def claim_reward(chat_id, username, password):
    try:
        session = requests.Session()
        
        # ۱. ورود به سیستم
        login_url = "https://coe.leme.hk.cn/login/check"
        login_data = {'account': username, 'password': password, 'type': '1'}
        # ابتدا یک بازدید از صفحه اول برای گرفتن کوکی اولیه
        session.get("https://coe.leme.hk.cn/login/index", headers=HEADERS)
        login_res = session.post(login_url, data=login_data, headers=HEADERS)
        
        if login_res.status_code == 200:
            # ۲. شبیه‌سازی ورود به صفحه جوایز (تصویر ۴۷)
            session.get("https://coe.leme.hk.cn/m/sign/check_in", headers=HEADERS)
            
            # ۳. ارسال درخواست کلیک روی دکمه طلایی
            # طبق ساختار سایت، درخواست باید به این آدرس ارسال شود
            action_url = "https://coe.leme.hk.cn/m/sign/sign_in_handler"
            response = session.post(action_url, headers=HEADERS)
            
            # بررسی پاسخ نهایی
            try:
                data = response.json()
                code = data.get('code')
                msg = data.get('msg', '')

                if code == 1 or "success" in msg.lower():
                    bot.send_message(chat_id, "✅ **با موفقیت انجام شد!**\nدکمه طلایی زده شد و جایزه به ایمیل بازی ارسال گشت.")
                elif code == 0 or "already" in msg.lower():
                    bot.send_message(chat_id, "⚠️ **تکراری:** جایزه امروز قبلاً دریافت شده است.")
                else:
                    bot.send_message(chat_id, f"❌ **پاسخ سایت:** {msg}")
            except:
                # اگر باز هم HTML برگرداند (مثل تصویر ۴۹)
                if response.status_code == 200:
                    bot.send_message(chat_id, "✅ عملیات به پایان رسید. اگر جایزه در بازی نیامده، یعنی پاسخ سایت تغییر کرده است.")
                else:
                    bot.send_message(chat_id, "❌ خطا در برقراری ارتباط با بخش دکمه طلایی.")
        else:
            bot.send_message(chat_id, "❌ مشخصات اکانت اشتباه است.")
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ خطای غیرمنتظره: `{str(e)[:40]}`")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "✅ ربات آماده کلیک آنی است.\nمشخصات را بفرستید: `user:pass`")

@bot.message_handler(func=lambda message: ":" in message.text)
def handle_message(message):
    u, p = message.text.split(":")[0].strip(), message.text.split(":")[1].strip()
    bot.reply_to(message, f"⌛ در حال کلیک روی دکمه طلایی برای `{u}`...")
    claim_reward(message.chat.id, u, p)

# جلوگیری از ارور Port Scan در رندر (تصویر ۴۴)
app = Flask('')
@app.route('/')
def home(): return "Bot is Online"
def run(): app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
