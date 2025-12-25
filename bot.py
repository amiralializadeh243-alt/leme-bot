import telebot
import requests
from flask import Flask
from threading import Thread
import random

TOKEN = '8095956559:AAGMeUTSGS9h8ZQTfPpCMHCZ5nwYBWVGTAk'
bot = telebot.TeleBot(TOKEN)
ADMIN_IDS = [8404377559]

def claim_reward_pro(chat_id, username, password):
    try:
        session = requests.Session()
        
        # لیست User-Agent های مختلف برای فریب سایت
        user_agents = [
            'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        ]

        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://coe.leme.hk.cn',
            'Referer': 'https://coe.leme.hk.cn/m/login'
        }

        # مرحله ۱: تلاش برای ورود به h5new
        login_url = "https://coe.leme.hk.cn/h5new/login"
        payload = {'username': username, 'password': password, 'webRegion': '2'}
        
        bot.send_message(chat_id, "📡 در حال تغییر هویت و دور زدن فایروال سایت...")
        
        # استفاده از یک تایم‌اوت طولانی‌تر برای عبور از تاخیرهای شبکه
        response = session.post(login_url, data=payload, headers=headers, timeout=20)
        
        token = session.cookies.get('token')
        if not token and '"token":"' in response.text:
            token = response.text.split('"token":"')[1].split('"')[0]

        if token:
            # مرحله ۲: کلیک طلایی
            signin_url = "https://coe.leme.hk.cn/h5new/signin"
            headers['Referer'] = 'https://coe.leme.hk.cn/m'
            res = session.post(signin_url, data=f'token={token}', headers=headers)
            
            msg = res.json().get('msg', 'انجام شد')
            bot.send_message(chat_id, f"✅ **عملیات موفقیت‌آمیز!**\nپاسخ نهایی: {msg}")
        else:
            bot.send_message(chat_id, "❌ **سد امنیتی:** سایت لمه هنوز متوجه ربات می‌شود. تنها راه باقی‌مانده استفاده از «پروکسی شخصی» یا «GitHub Actions» است.")

    except Exception as e:
        bot.send_message(chat_id, f"⚠️ خطای شبکه: `{str(e)[:50]}`")

@bot.message_handler(commands=['start'])
def start(m):
    if m.from_user.id in ADMIN_IDS:
        bot.reply_to(m, "🤖 ربات ضد-فایروال فعال شد.\nارسال: `user:pass`")

@bot.message_handler(func=lambda m: ":" in m.text and m.from_user.id in ADMIN_IDS)
def handle(m):
    u, p = m.text.split(":")[0].strip(), m.text.split(":")[1].strip()
    claim_reward_pro(m.chat.id, u, p)

app = Flask('')
@app.route('/')
def home(): return "Proxy Mode Active"
def run(): app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True, skip_pending=True)
