import telebot
import requests
from flask import Flask
from threading import Thread

# --- تنظیمات نهایی ---
TOKEN = '8095956559:AAGMeUTSGS9h8ZQTfPpCMHCZ5nwYBWVGTAk'
bot = telebot.TeleBot(TOKEN)

# لیست سفید: فقط شما دسترسی دارید
ADMIN_IDS = [8404377559] 

def claim_reward(chat_id, username, password):
    try:
        session = requests.Session()
        # ۱. ورود به سیستم (بر اساس cURL ضبط شده شما)
        login_url = "https://coe.leme.hk.cn/login/check"
        payload = {'account': username, 'password': password, 'type': '1'}
        headers_base = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*'
        }
        # انجام لاگین برای دریافت کوکی 'token' زنده
        session.post(login_url, data=payload, headers=headers_base, timeout=15)
        
        user_token = session.cookies.get('token')
        
        if user_token:
            # ۲. حرکت مستقیم به آدرس جدید ضبط شده (تصویر ۶۰)
            action_url = "https://coe.leme.hk.cn/h5new/signin"
            action_headers = {
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                'Origin': 'https://coe.leme.hk.cn',
                'Referer': 'https://coe.leme.hk.cn/m',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest'
            }
            # ارسال داده‌های ضبط شده مطابق cURL ارسالی شما
            data_raw = f'token={user_token}'
            response = session.post(action_url, headers=action_headers, data=data_raw)
            
            res_json = response.json()
            msg = res_json.get('msg', 'پاسخی از سرور دریافت نشد')
            
            if res_json.get('code') == 1 or "success" in msg.lower():
                bot.send_message(chat_id, "✅ **عملیات با موفقیت انجام شد!**\nدکمه طلایی با آدرس جدید زده شد. جایزه را در بازی دریافت کنید.")
            elif "already" in msg.lower() or res_json.get('code') == 0:
                bot.send_message(chat_id, f"⚠️ **پیام سایت:** {msg} (احتمالاً قبلاً دریافت شده)")
            else:
                bot.send_message(chat_id, f"❌ **خطا در کلیک نهایی:** {msg}")
        else:
            bot.send_message(chat_id, "❌ **خطا:** توکن امنیتی یافت نشد. یوزر یا پسورد را چک کنید.")
            
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ **خطای غیرمنتظره:** `{str(e)[:50]}`")

# فیلتر کردن تمام پیام‌ها برای افراد غیرمجاز
@bot.message_handler(func=lambda message: message.from_user.id not in ADMIN_IDS)
def unauthorized(message):
    bot.reply_to(message, "⛔ این ربات شخصی است و شما اجازه دسترسی ندارید.")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🚀 **ربات لمه آماده به کار است (نسخه اختصاصی).**\nمشخصات را بفرستید: `user:pass`")

@bot.message_handler(func=lambda message: ":" in message.text and message.from_user.id in ADMIN_IDS)
def handle_message(message):
    try:
        u, p = message.text.split(":")[0].strip(), message.text.split(":")[1].strip()
        bot.reply_to(message, f"⌛ در حال بازسازی حرکت ضبط شده برای `{u}`...")
        claim_reward(message.chat.id, u, p)
    except:
        bot.reply_to(message, "❌ فرمت اشتباه! مثال: `ali:123456`")

# وب‌سرور برای جلوگیری از خاموش شدن در رندر
app = Flask('')
@app.route('/')
def home(): return "Bot is Live and Secure"
def run(): app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run).start()
    # استفاده از skip_pending برای پاکسازی پیام‌های قبلی و رفع تداخل
    bot.polling(none_stop=True, skip_pending=True)
