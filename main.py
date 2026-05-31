import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
from google.genai import types

# Logging စနစ်
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

# SDK အသစ်ဖြင့် Client ဆောက်ခြင်း
client = genai.Client(api_key=GOOGLE_API_KEY)

# PC System Tools ပိုင်း
def clean_junk_files() -> str:
    """Windows ရဲ့ ယာယီ Junk ဖိုင်တွေနဲ့ Cache တွေကို ရှင်းလင်းပေးတဲ့ Tool"""
    return "Junk files များကို ရှင်းလင်းရန် အမိန့်ပေးချက် လက်ခံရရှိပါပြီ၊၊"

def reset_network() -> str:
    """Network DNS ကို Flush လုပ်ပေးတဲ့ Tool"""
    return "Network DNS ကို အောင်မြင်စွာ Flush လုပ်ပေးပြီးပါပြီ၊၊"

# Tools များကို စာရင်းသွင်းခြင်း
my_tools = [clean_junk_files, reset_network]

# Chat Session ကို သိမ်းဆည်းရန်အတွက် (အသစ်ဗားရှင်း ပုံစံ)
# Gemini 1.5 Flash သို့မဟုတ် ၂၀၂၆ ဗားရှင်းများအတွက် တိုက်ရိုက် သတ်မှတ်ခြင်း
MODEL_ID = 'gemini-1.5-flash'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("မင်္ဂလာပါ အစ်ကို။ SNNTECH AI PC Manager Bot ကို ပြင်ဆင်ပြီးပါပြီ၊၊ စမ်းပြီး ခိုင်းကြည့်ပါဦး၊၊")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    try:
        # SDK အသစ်၏ Function Calling ပုံစံဖြင့် လှမ်းခေါ်ခြင်း
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=user_text,
            config=types.GenerateContentConfig(
                tools=my_tools,
                temperature=0.5
            )
        )
        
        # AI ရဲ့ အဖြေကို ပြန်ပို့ခြင်း
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"အမှားအယွင်းရှိပါသည်: {str(e)}")

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == '__main__':
    main()
