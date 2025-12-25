import requests
import os

def run():
    token = "8095956559:AAGMeUTSGS9h8ZQTfPpCMHCZ5nwYBWVGTAk"
    chat_id = "8404377559"
    if not os.path.exists('accounts.txt'): return
    with open('accounts.txt', 'r') as f:
        accounts = f.readlines()
    session = requests.Session()
    for acc in accounts:
        if ':' not in acc: continue
        u, p = acc.strip().split(':')
        try:
            # عملیات ورود و دریافت جایزه
            res = session.post("https://coe.leme.hk.cn/h5new/login", data={'username': u, 'password': p, 'webRegion': '2'})
            leme_token = session.cookies.get('token')
            if leme_token:
                session.post("https://coe.leme.hk.cn/h5new/signin", data=f'token={leme_token}')
                requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text=🤖 اکانت {u}: ✅ انجام شد.")
            else:
                requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text=❌ اکانت {u}: شکست در ورود")
        except: pass
if __name__ == "__main__":
    run()
