import telebot
import requests
from flask import Flask
from threading import Thread

# --- تنظیمات اختصاصی شما ---
TOKEN = '8095956559:AAGMeUTSGS9h8ZQTfPpCMHCZ5nwYBWVGTAk'
bot = telebot.TeleBot(TOKEN)

# هدرهای پیشرفته برای شبیه‌سازی دقیق موبایل
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'https://coe.leme.hk.cn',
    'Referer': 'https://coe.leme.hk.cn/m/sign/check_in'
}

def claim_reward(chat_id, username, password):
    try:
        session = requests.Session()
        
        # ۱. ورود به سیستم
        login_url = "https://coe.leme.hk.cn/login/check"
        login_data = {'account': username, 'password': password, 'type': '1'}
        login_res = session.post(login_url, data=login_data, headers=HEADERS, timeout=15)
        
        if login_res.status_code == 200:
            # ۲. زدن دکمه طلایی (ارسال مستقیم اکشن به سرور)
            # آدرس اصلی عملیاتی برای دکمه Sign-in در تصویر ۴۷
            action_url = "https://coe.leme.hk.cn/m/sign/sign_in_handler"
            
            # ارسال درخواست کلیک
            reward_res = session.post(action_url, headers=HEADERS)
            
            # تحلیل پاسخ (JSON)
            try:
                data = reward_res.json()
                msg = data.get('msg', '').lower()
                code = data.get('code', -1)
                
                if code == 1 or "success" in msg:
                    bot.send_message(chat_id, "✅ **عملیات موفق!**\nدکمه طلایی با موفقیت زده شد. لطفاً ایمیل‌های داخل بازی را چک کنید.")
                elif code == 0 or "already" in msg:
                    bot.send_message(chat_id, "⚠️ **تکراری:** شما امروز قبلاً جایزه را دریافت کرده‌اید.")
                else:
                    bot.send_message(chat_id, f"❌ **پاسخ سایت:** {data.get('msg', 'خطای ناشناخته')}")
            except:
                # اگر پاسخ JSON نبود (مثل تصویر ۴۹)، یعنی عملیات با خطا مواجه شده
                if "success" in reward_res.text.lower():
                    bot.send_message(chat_id, "✅ عملیات احتمالاً موفق بود (پاسخ متنی).")
                else:
                    bot.send_message(chat_id, "❌ خطا: سایت اجازه کلیک نهایی را نداد. احتمالاً نیاز به سطح (Level) بالاتر در بازی دارد.")
        else:
            bot.send_message(chat_id, "❌ ورود ناموفق! مشخصات را چک کنید.")
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ خطای فنی: `{str(e)[:50]}`")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "✅ ربات لمه آماده است.\nمشخصات را بفرستید: `user:pass`")

@bot.message_handler(func=lambda message: ":" in message.text)
def handle_message(message):
    try:
        u, p = message.text.split(":")[0].strip(), message.text.split(":")[1].strip()
        bot.reply_to(message, f"⌛ در حال تلاش برای کلیک روی دکمه طلایی برای `{u}`...")
        claim_reward(message.chat.id, u, p)
    except:
        bot.reply_to(message, "❌ فرمت اشتباه! مثال: `ali:123456`")

# --- تنظیمات پورت برای Render ---
app = Flask('')
@app.route('/')
def home(): return "OK"
def run(): app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
