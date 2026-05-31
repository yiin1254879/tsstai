import os
import logging
import subprocess
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# Logging သတ်မှတ်ခြင်း (Error စစ်ရန်)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Environment Variables မှ API Keys များယူခြင်း (Koyeb တွင် ထည့်ရမည်)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

# PC System Tools များ
def clean_junk_files() -> str:
    """Windows ရဲ့ ယာယီ Junk ဖိုင်တွေနဲ့ Cache တွေကို ရှင်းလင်းပေးတဲ့ Tool"""
    try:
        # မှတ်ချက် - Koyeb သည် Linux ဖြစ်သဖြင့် local PC ကို တိုက်ရိုက်မဖျက်နိုင်ပါ။ 
        # PC နှင့် ချိတ်ဆက်ရန် နောက်ပိုင်းတွင် SSH/Agent ထပ်ထည့်ရပါမည်။ လက်ရှိတွင် အလုပ်လုပ်ပုံကို စမ်းသပ်ခြင်း ဖြစ်သည်။
        return "Junk files များကို ရှင်းလင်းရန် အမိန့်ပေးချက် လက်ခံရရှိပါပြီ၊၊"
    except Exception as e:
        return f"Error: {str(e)}"

# Gemini Agent ပြင်ဆင်ခြင်း
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    tools=[clean_junk_files]
)
chat = model.start_chat(enable_automatic_function_calling=True)

# Bot Commands များ
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("မင်္ဂလာပါ အစ်ကို။ SNNTECH AI PC Manager Bot မှ ကြိုဆိုပါတယ်၊၊ ကျွန်တော့်ကို စာရိုက်ပြီး ခိုင်းနိုင်ပါပြီ၊၊")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    try:
        # Gemini ထံ စာသားပို့ပြီး အဖြေတောင်းခြင်း
        response = chat.send_message(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"အမှားအယွင်းရှိပါသည်: {str(e)}")

def main():
    # Telegram Bot ကို စတင်ခြင်း
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Koyeb တွင် ၂၄ နာရီပတ်လုံး Run နေစေရန် ပုံစံပြောင်းခြင်း
    application.run_polling()

if __name__ == '__main__':
    main()