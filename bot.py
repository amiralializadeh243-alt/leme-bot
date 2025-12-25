def claim_reward(chat_id, username, password):
    try:
        session = requests.Session()
        # استفاده از هدرهای دقیق cURL شما برای لاگین
        login_headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'Referer': 'https://coe.leme.hk.cn/m/login'
        }
        
        # تست دو مسیر احتمالی برای لاگین
        login_urls = [
            "https://coe.leme.hk.cn/login/check",
            "https://coe.leme.hk.cn/h5new/login/check" # مسیر احتمالی جدید
        ]
        
        logged_in = False
        for url in login_urls:
            payload = f'account={username}&password={password}&type=1'
            res = session.post(url, data=payload, headers=login_headers, timeout=15)
            if session.cookies.get('token'):
                logged_in = True
                break
        
        user_token = session.cookies.get('token')
        
        if logged_in and user_token:
            # ادامه عملیات کلیک روی دکمه طلایی
            action_url = "https://coe.leme.hk.cn/h5new/signin"
            data_raw = f'token={user_token}'
            # ... بقیه کد مشابه قبل ...
            response = session.post(action_url, headers=login_headers, data=data_raw)
            bot.send_message(chat_id, f"✅ عملیات انجام شد: {response.json().get('msg')}")
        else:
            bot.send_message(chat_id, "❌ خطای ورود: توکن یافت نشد. لطفاً یک بار دستی در سایت لاگین کنید و برگردید.")
