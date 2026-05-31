import os
import logging
import requests
import asyncio
import uvicorn
from fastapi import FastAPI
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Logging စနစ်
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# FastAPI ဆာဗာ တည်ဆောက်ခြင်း (Koyeb Health Check ကို ကျော်ဖြတ်ရန်)
app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "SNNTECH AI PC Manager Bot is Running Successfully!"}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("မင်္ဂလာပါ အစ်ကို။ SNNTECH AI PC Manager Bot ကို Web Server စနစ်နဲ့ အပြီးသတ် ပြင်ဆင်ပြီးပါပြီ၊၊ 'junk ရှင်း' လို့ စိတ်ကြိုက်ခိုင်းနိုင်ပါပြီဗျာ၊၊")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    
    if "junk" in user_text.lower() or "အမှိုက်" in user_text:
        await update.message.reply_text("⚙️ PC စနစ်ထဲက Junk files များကို ရှင်းလင်းရန် အမိန့်ပေးချက် လက်ခံရရှိပါပြီ၊၊")
        return
        
    elif "network" in user_text.lower() or "လိုင်း" in user_text:
        await update.message.reply_text("⚙️ Network DNS ကို Flush လုပ်ရန် အမိန့်ပေးချက် လက်ခံရရှိပါပြီ၊၊")
        return

    # Gemini API ခေါ်ခြင်း
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": user_text + " (Please reply in Myanmar language consistently.)"}]
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

# Telegram နှင့် Web Server ကို တွဲဖက် Run ပေးမည့် အပိုင်း
async def run_bot_and_server():
    # Telegram Bot တည်ဆောက်ခြင်း
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Bot ကို စတင်ခြင်း (Async ဗားရှင်းဖြင့်)
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    # Uvicorn Web Server ကို Port 8000 တွင် ချိတ်ဆက်ပွင့်စေခြင်း
    config = uvicorn.Config(app=app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == '__main__':
    # Async စနစ်ကို စတင်မောင်းနှင်ခြင်း
    asyncio.run(run_bot_and_server())
