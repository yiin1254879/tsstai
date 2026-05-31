import os
import logging
import requests
import threading
import http.server
import socketserver
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Logging စနစ်
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ၁။ Koyeb ရဲ့ Health Check ကို ကျေနပ်စေရန် Port 8000 တွင် Server အတု ဖွင့်ခြင်း
def run_dummy_server():
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    # Port သုံးထားပါက တစ်ခါတည်း Release လုပ်ရန် သတ်မှတ်ခြင်း
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        logging.info(f"Koyeb Health Check Server started on port {PORT}")
        httpd.serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("မင်္ဂလာပါ အစ်ကို။ SNNTECH AI PC Manager Bot ကို နောက်ဆုံးဗားရှင်းနဲ့ အပြီးသတ် ပြင်ဆင်ပြီးပါပြီ၊၊ 'junk ရှင်း' လို့ စိတ်ကြိုက်ခိုင်းနိုင်ပါပြီဗျာ၊၊")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    
    # စကားလုံးကို စစ်ဆေးပြီး အမိန့်ကို ခွဲခြားခြင်း
    if "junk" in user_text.lower() or "အမှိုက်" in user_text:
        await update.message.reply_text("⚙️ PC စနစ်ထဲက Junk files များကို ရှင်းလင်းရန် အမိန့်ပေးချက် လက်ခံရရှိပါပြီ၊၊")
        return
        
    elif "network" in user_text.lower() or "လိုင်း" in user_text:
        await update.message.reply_text("⚙️ Network DNS ကို Flush လုပ်ရန် အမိန့်ပေးချက် လက်ခံရရှိပါပြီ၊၊")
        return

    # သာမန်စကားပြောဆိုမှုများအတွက် Gemini API ခေါ်ခြင်း
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": user_text + " (Please reply in Myanmar language consistently as a helpful assistant.)"}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        res_data = response.json()
        
        if "candidates" in res_data:
            ai_reply = res_data["candidates"][0]["content"]["parts"][0]["text"]
            await update.message.reply_text(ai_reply)
        else:
            await update.message.reply_text(f"API တုံ့ပြန်မှုပြဿနာရှိပါသည်: {str(res_data)}")
            
    except Exception as e:
        await update.message.reply_text(f"အမှားအယွင်းရှိပါသည်: {str(e)}")

def main():
    # Server အတုကို Background Thread တွင် သီးသန့် အရင် Run ထားခြင်း
    threading.Thread(target=run_dummy_server, daemon=True).start()

    # Telegram Bot စတင်ခြင်း
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == '__main__':
    main()
