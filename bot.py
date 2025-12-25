import telebot
import requests
from flask import Flask
from threading import Thread
import urllib.parse

TOKEN = '8095956559:AAGMeUTSGS9h8ZQTfPpCMHCZ5nwYBWVGTAk'
bot = telebot.TeleBot(TOKEN)
ADMIN_IDS = [8404377559]

def claim_reward(chat_id, username, password):
    try:
        session = requests.Session()
        # هدرهای کاملاً مطابق با گوشی شما در لحظه موفقیت
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://coe.leme.hk.cn',
            'Referer': 'https://coe.leme.hk.cn/m'
        }

        # مرحله ۱: ورود با متد جدید پارامتریک (هماهنگ با h5new)
        login_url = "https://coe.leme.hk.cn/h5new/login"
        
        # کدگذاری یوزرنیم و پسورد برای جلوگیری از ارور منقضی شدن
        payload = {
            'username': username,
            'password': password,
            'webRegion': '2'
        }
        
        bot.send_message(chat_id, "⌛ در حال برقراری ارتباط با سرور h5new...")
        response = session.post(login_url, data=payload, headers=headers, timeout=15)
        
        # استخراج توکن تازه
        token = session.cookies.get('token')
        
        if token:
            # مرحله ۲: کلیک روی دکمه طلایی با توکن اختصاصی شما
            bot.send_message(chat_id, "🔑 ورود موفقیت‌آمیز بود. در حال دریافت جایزه...")
            signin_url = "https://coe.leme.hk.cn/h5new/signin"
            data_signin = f'token={token}'
            
            res = session.post(signin_url, headers=headers, data=data_signin)
            res_json = res.json()
            
            msg = res_json.get('msg', 'پاسخی دریافت نشد')
            if res_json.get('code') == 1:
                bot.send_message(chat_id, f"✅ **عملیات با موفقیت انجام شد!**\n{msg}")
            else:
                bot.send_message(chat_id, f"⚠️ **وضعیت:** {msg}")
        else:
            bot.send_message(chat_id, "❌ **خطا:** سایت اجازه ورود نداد. احتمالاً سایت برای امنیت بیشتر، اجازه ورود خودکار از آی‌پی سرور را مسدود کرده است.")

    except Exception as e:
        bot.send_message(chat_id, f"⚠️ خطای فنی: `{str(e)[:50]}`")

@bot.message_handler(commands=['start'])
def start(m):
    if m.from_user.id in ADMIN_IDS:
        bot.reply_to(m, "🚀 ربات اختصاصی شما آماده است.\nفرمت ارسال: `user:pass`")

@bot.message_handler(func=lambda m: ":" in m.text and m.from_user.id in ADMIN_IDS)
def handle_message(m):
    u, p = m.text.split(":")[0].strip(), m.text.split(":")[1].strip()
    claim_reward(m.chat.id, u, p)

app = Flask('')
@app.route('/')
def home(): return "Bot is Online"
def run(): app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True, skip_pending=True)
