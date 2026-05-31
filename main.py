import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Logging စနစ်
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("မင်္ဂလာပါ အစ်ကို။ SNNTECH AI PC Manager Bot ကို ဗားရှင်းအသစ်နဲ့ အောင်မြင်စွာ ပြင်ဆင်ပြီးပါပြီ၊၊ 'junk ရှင်း' လို့ ခိုင်းကြည့်ပေးပါဦး၊၊")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    
    # ၁။ စကားလုံးကို စစ်ဆေးပြီး အမိန့်ကို အရင်ခွဲခြားခြင်း
    if "junk" in user_text.lower() or "အမှိုက်" in user_text:
        # ဤနေရာတွင် PC အား အမှိုက်ရှင်းရန် အမိန့်ပေးသည့်အပိုင်း လုပ်ဆောင်မည်
        await update.message.reply_text("⚙️ PC စနစ်ထဲက Junk files များကို ရှင်းလင်းရန် အမိန့်ပေးချက် လက်ခံရရှိပါပြီ၊၊")
        return
        
    elif "network" in user_text.lower() or "လိုင်း" in user_text:
        await update.message.reply_text("⚙️ Network DNS ကို Flush လုပ်ရန် အမိန့်ပေးချက် လက်ခံရရှိပါပြီ၊၊")
        return

    # ၂။ သာမန်စကားပြောဆိုမှုများအတွက် Gemini API ကို Standard URL ဖြင့် တိုက်ရိုက်ခေါ်ခြင်း
    # v1beta အစား အငြိမ်ဆုံး v1 ဗားရှင်းကို ပြောင်းသုံးထားပါတယ်
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
        
        # AI ထံမှ ရလာသော စာသားကို ယူခြင်း
        if "candidates" in res_data:
            ai_reply = res_data["candidates"][0]["content"]["parts"][0]["text"]
            await update.message.reply_text(ai_reply)
        else:
            await update.message.reply_text(f"API တုံ့ပြန်မှုပြဿနာရှိပါသည်: {str(res_data)}")
            
    except Exception as e:
        await update.message.reply_text(f"အမှားအယွင်းရှိပါသည်: {str(e)}")

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == '__main__':
    main()
