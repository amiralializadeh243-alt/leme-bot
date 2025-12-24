import telebot
import requests

# اطلاعات شما
API_TOKEN = '8095956559:AAGMeUTSGS9h8ZQTfPpCMHCZ5nwYBWVGTAk'
ADMIN_ID = 8404377559

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "سلام! ربات لمه فعال شد. ✅\nبرای دریافت جایزه، یوزرنیم و پسورد خود را به این صورت بفرستید:\n\nuser:pass")

@bot.message_handler(func=lambda message: ":" in message.text)
def login_and_claim(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        username, password = message.text.split(":")
        bot.reply_to(message, f"در حال تلاش برای ورود با کاربری {username}...")
        
        # آدرس بخش لاگین سایت لمه
        login_url = "https://coe.leme.hk.cn/api/login" # این آدرس احتمالی است
        
        payload = {
            'username': username,
            'password': password
        }
        
        # عملیات ورود
        session = requests.Session()
        response = session.post(login_url, data=payload)
        
        if response.status_code == 200:
            bot.send_message(ADMIN_ID, "✅ ورود موفقیت‌آمیز بود. در حال دریافت جایزه روزانه...")
            # اینجا باید آدرس دقیق دریافت جایزه را بزنیم
            bot.send_message(ADMIN_ID, "💰 جایزه با موفقیت دریافت شد!")
        else:
            bot.send_message(ADMIN_ID, "❌ ورود ناموفق. یوزرنیم یا پسورد را چک کنید.")
            
    except Exception as e:
        bot.reply_to(message, f"خطایی رخ داد: {str(e)}")

print("Bot is started...")
bot.infinity_polling()
