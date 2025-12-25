import requests
import os

def run():
    # خواندن اطلاعات امنیتی از Secrets گیت‌هاب
    username = os.getenv('LEME_USER')
    password = os.getenv('LEME_PASS')
    bot_token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
    }

    # ۱. ورود به سایت h5new
    login_url = "https://coe.leme.hk.cn/h5new/login"
    payload = f'username={username}&password={password}&webRegion=2'
    
    try:
        res = session.post(login_url, data=payload, headers=headers, timeout=20)
        token = session.cookies.get('token')
        
        # اگر توکن در کوکی نبود، در متن پاسخ جستجو کن
        if not token and '"token":"' in res.text:
            token = res.text.split('"token":"')[1].split('"')[0]

        if token:
            # ۲. کلیک روی دکمه طلایی
            signin_url = "https://coe.leme.hk.cn/h5new/signin"
            response = session.post(signin_url, data=f'token={token}', headers=headers)
            msg = response.json().get('msg', 'عملیات انجام شد')
            requests.get(f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text=🤖 گیت‌هاب گزارش می‌دهد:\n✅ {msg}")
        else:
            requests.get(f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text=❌ گیت‌هاب: لاگین ناموفق بود.")
    except Exception as e:
        requests.get(f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text=⚠️ خطای گیت‌هاب: {str(e)[:50]}")

if __name__ == "__main__":
    run()
