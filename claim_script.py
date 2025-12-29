import requests
import os

def run_claim():
    # تنظیمات برای اطلاع‌رسانی به تلگرام شما
    TELEGRAM_TOKEN = '8286464872:AAE1E1FQt5A52mOKFo5Sewq48vhG1ubJlN8'
    CHAT_ID = '8404377559'
    
    # بررسی وجود فایل لیست اکانت‌ها
    if not os.path.exists('accounts.txt'):
        print("فایل accounts.txt پیدا نشد.")
        return

    with open('accounts.txt', 'r') as f:
        accounts = f.readlines()

    session = requests.Session()
    
    for acc in accounts:
        acc = acc.strip()
        if ':' not in acc:
            continue
            
        username, password = acc.split(':')
        print(f"در حال بررسی اکانت: {username}")
        
        try:
            # ۱. ورود به سایت (Login)
            login_url = "https://coe.leme.hk.cn/h5new/login"
            login_data = {
                'username': username,
                'password': password,
                'webRegion': '2'
            }
            res = session.post(login_url, data=login_data)
            
            # دریافت توکن مخصوص سایت لمه از کوکی‌ها
            leme_token = session.cookies.get('token')
            
            if leme_token:
                # ۲. زدن دکمه دریافت جایزه یا حضور (Signin/Claim)
                claim_url = "https://coe.leme.hk.cn/h5new/signin"
                claim_res = session.post(claim_url, data={'token': leme_token})
                
                # ارسال پیام موفقیت به تلگرام شما
                msg = f"🤖 حساب `{username}`: ✅ عملیات با موفقیت انجام شد."
                requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}&parse_mode=Markdown")
            else:
                # ارسال پیام خطا در ورود
                msg = f"❌ حساب `{username}`: خطا در ورود (نام کاربری یا رمز اشتباه)."
                requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}&parse_mode=Markdown")
        
        except Exception as e:
            print(f"خطای غیرمنتظره برای {username}: {e}")

if __name__ == "__main__":
    run_claim()
