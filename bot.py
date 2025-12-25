import telebot
import requests
from flask import Flask
from threading import Thread

TOKEN = '8095956559:AAGMeUTSGS9h8ZQTfPpCMHCZ5nwYBWVGTAk'
bot = telebot.TeleBot(TOKEN)
ADMIN_IDS = [8404377559]

# اطلاعات استخراج شده از cURL شما
LOGIN_URL = "https://coe.leme.hk.cn/h5new/login"
SIGNIN_URL = "https://coe.leme.hk.cn/h5new/signin"

# این همان دیتای رمزنگاری شده گوشی شماست که سایت آن را قبول می‌کند
ENCRYPTED_DATA = 'username=aiYiuerPfbYaUAVCseiMUkldAQlY14L1gmLO26c59bFK1Rgi%2FvjtMiGJKfgheBF4Ptx958bKgg6fXl5nscHKZFi%2BjRq1rxnPPA6zew60ObOa6G9%2BixqaiRvI401v1U9I%2F9JQA1DcDJepL3Dx0YIVv8Li%2B0mtTOgM551o4NzwdDI%3D&password=WvvBWS%2Fejem5N9KkLO3wA51P5Rz4x66naBG30cYUM2jz2nnDTxBi%2Bab8Z4QF35hBmvKC%2FmJ9fHUSIdIKogN18Vq4n%2BxJ5VNlFf5QFUfUjzTLqA7FESc54RHB71cBv3zl%2FfDiw4OdFV%2B67cS2cwkZN1GIDRApfalpAMxOWZ1Px4o%3D&webRegion=2'

def run_auto_claim(chat_id):
    try:
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://coe.leme.hk.cn',
            'Referer': 'https://coe.leme.hk.cn/m'
        }

        # ۱. ورود با دیتای رمزنگاری شده (شبیه‌سازی کامل گوشی شما)
        bot.send_message(chat_id, "⌛ در حال شبیه‌سازی ورود ایمن...")
        login_res = session.post(LOGIN_URL, data=ENCRYPTED_DATA, headers=headers)
        
        token = session.cookies.get('token')
        if not token and '"token":"' in login_res.text:
            token = login_res.text.split('"token":"')[1].split('"')[0]

        if token:
            # ۲. کلیک روی دکمه طلایی با توکن جدید
            bot.send_message(chat_id, "🔑 توکن دریافت شد. در حال زدن دکمه طلایی...")
            data_signin = f'token={token}'
            response = session.post(SIGNIN_URL, headers=headers, data=data_signin)
            
            res_json = response.json()
            msg = res_json.get('msg', 'بدون پیام')
            if res_json.get('code') == 1:
                bot.send_message(chat_id, f"✅ **پیروزی!** جایزه دریافت شد: {msg}")
            else:
                bot.send_message(chat_id, f"⚠️ **پیام سایت:** {msg}")
        else:
            bot.send_message(chat_id, "❌ متأسفانه سایت دیتای رمزنگاری شده را منقضی کرده است.")
            
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ خطای فنی: `{str(e)[:50]}`")

@bot.message_handler(commands=['start'])
def start(m):
    if m.from_user.id in ADMIN_IDS:
        bot.reply_to(m, "🚀 ربات با متد جدید (Encrypted) آماده است.\nبرای دریافت جایزه دستور `/claim` را بزنید.")
    else:
        bot.reply_to(m, "⛔ دسترسی محدود.")

@bot.message_handler(commands=['claim'])
def handle_claim(m):
    if m.from_user.id in ADMIN_IDS:
        run_auto_claim(m.chat.id)

app = Flask('')
@app.route('/')
def home(): return "Active"
def run(): app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True, skip_pending=True)
