import telebot
import requests
import base64
from flask import Flask
from threading import Thread

# --- تنظیمات نهایی شما ---
TOKEN = '8286464872:AAEO0JHlqMpi3vDTMxGHdUKFPfSXYVBj6Uc'
GITHUB_TOKEN = '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' 
REPO_NAME = 'amiralializadeh243-alt/leme-bot'
FILE_PATH = 'accounts.txt'

bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Manager is Online and Active!"

def save_to_github(new_entry):
    try:
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # ۱. تلاش برای خواندن فایل موجود
        r = requests.get(url, headers=headers)
        sha = r.json().get('sha') if r.status_code == 200 else None
        
        if sha:
            old_content = base64.b64decode(r.json()['content']).decode()
        else:
            old_content = ""

        # ۲. اضافه کردن اکانت جدید (هر اکانت در یک خط)
        # اگر فایل خالی نیست، اول یک اینتر می‌زنیم
        if old_content and not old_content.endswith('\n'):
            updated_content = old_content + "\n" + new_entry
        else:
            updated_content = old_content + new_entry
            
        updated_content = updated_content.strip() + "\n"
        encoded = base64.b64encode(updated_content.encode()).decode()

        # ۳. ارسال محتوای جدید به گیت‌هاب
        payload = {
            "message": "Add new account via Telegram Bot
