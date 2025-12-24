import telebot

# اطلاعات اختصاصی شما که جایگذاری شد
API_TOKEN = '8095956559:AAGMeUTSGS9h8ZQTfPpCMHCZ5nwYBWVGTAk'
ADMIN_ID = 8404377559

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ دسترسی غیرمجاز. این ربات خصوصی است.")
        return
    bot.reply_to(message, "سلام قربان! ربات لمه (Leme) آماده خدمت است.\nلطفاً نام کاربری سایت را ارسال کنید.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    # پاسخ موقت برای تست سالم بودن ربات
    bot.reply_to(message, f"پیام شما دریافت شد: {message.text}\nدر حال آماده‌سازی بخش ورود به سایت Leme هستیم...")

print("Bot is running...")
bot.infinity_polling()
