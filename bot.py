import telebot
import requests
from flask import Flask
from threading import Thread

# --- تنظیمات ---
TOKEN = '8095956559:AAGMeUTSGS9h8ZQTfPpCMHCZ5nwYBWVGTAk'
bot = telebot.TeleBot(TOKEN)

# هدرهای دقیق برای شبیه‌سازی مرورگر موبایل (حل ارور تصویر ۵۴)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://coe.leme.hk.cn/m/sign/check_in',
    'Origin': 'https://coe.leme.hk.cn',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
}

def claim_reward(chat_id, username, password):
    try:
        session = requests.Session()
        
        # ۱. ورود به سیستم
        login_url = "https://coe.leme.hk.cn/login/check"
        payload = {'account': username, 'password': password, 'type': '1'}
        login_res = session.post(login_url, data=payload, headers=HEADERS, timeout=15)
        
        if login_res.status_code == 200:
            # ۲. ارسال درخواست به دکمه طلایی (آدرس اصلاح شده برای ثبت جایزه)
            # بر اساس تصویر ۴۷، اکشن اصلی بر روی check_in یا sign_in_handler است
            action_url = "https://coe.leme.hk.cn/m/sign/sign_in_handler"
            response = session.post(action_url, headers=HEADERS)
            
            # ۳. بررسی پاسخ هوشمند
            res_text = response.text.lower()
            if '"code":1' in res_text or "success" in res_text:
                bot.send_message(chat_id, "✅ **عملیات با موفقیت انجام شد!**\nدکمه طلایی زده شد. لطفاً جایزه را در بخش ایمیل‌های بازی دریافت کنید.")
            elif '"code":0' in res_text or "already" in res_text:
                bot.send_message(chat_id, "⚠️ **تکراری:** جایزه امروز این اکانت قبلاً دریافت شده است.")
            else:
                # اگر پاسخ نامشخص بود، یک تلاش مجدد روی آدرس دوم انجام می‌دهیم
                alt_url = "https://coe.leme.hk.cn/m/sign/check_in"
                alt_res = session.post(alt_url, headers=HEADERS)
                if "success" in alt_res.text.lower():
                    bot.send_message(chat_id, "✅ عملیات با آدرس جایگزین موفقیت‌آمیز بود.")
                else:
                    bot.send_message(chat_id, "❌ سایت وارد شد اما دکمه طلایی پاسخ نداد. لطفاً یک‌بار دستی در سایت تست کنید.")
        else:
            bot.send_message(chat_id, "❌ ورود ناموفق! نام کاربری یا رمز عبور اشتباه است.")
            
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ خطای فنی: `{str(e)[:40]}`")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "✅ **ربات آماده کلیک آنی است.**\nمشخصات را بفرستید: `user:pass`", parse_mode="Markdown")

@bot.message_handler(func=lambda message: ":" in message.text)
def handle_message(message):
    try:
        u, p = message.text.split(":")[0].strip(), message.text.split(":")[1].strip()
        bot.reply_to(message, f"⌛ در حال کلیک روی دکمه طلایی برای `{u}`...")
        claim_reward(message.chat.id, u, p)
    except:
        bot.reply_to(message, "❌ فرمت اشتباه! مثال: `ali:123456`")

# --- رفع ارور پورت در Render (تصویر ۴۴) ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online"
def run(): app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run).start()
    # استفاده از skip_pending=True برای نادیده گرفتن ارور ۴۰۹ (تصویر ۵۲)
    bot.polling(none_stop=True, skip_pending=True)
