
import random
import asyncio
import aiohttp
import os
from telegram import Update, InputMediaAudio
from telegram.ext import Application, CommandHandler, ContextTypes
from flask import Flask
from threading import Thread

TOKEN = "7805033056:AAFMHN1uZLY0wl3Tqnj4KxgHoW04bYBrZV0"
CHANNEL_ID = "@dzmmm"

# السور وأسماءها
surahs = {
    1: "الفاتحة", 2: "البقرة", 3: "آل عمران", 4: "النساء", 5: "المائدة", 6: "الأنعام", 7: "الأعراف",
    8: "الأنفال", 9: "التوبة", 10: "يونس", 11: "هود", 12: "يوسف", 13: "الرعد", 14: "إبراهيم", 15: "الحجر",
    16: "النحل", 17: "الإسراء", 18: "الكهف", 19: "مريم", 20: "طه", 21: "الأنبياء", 22: "الحج", 23: "المؤمنون",
    24: "النور", 25: "الفرقان", 26: "الشعراء", 27: "النمل", 28: "القصص", 29: "العنكبوت", 30: "الروم",
    31: "لقمان", 32: "السجدة", 33: "الأحزاب", 34: "سبإ", 35: "فاطر", 36: "يس", 37: "الصافات", 38: "ص",
    39: "الزمر", 40: "غافر", 41: "فصلت", 42: "الشورى", 43: "الزخرف", 44: "الدخان", 45: "الجاثية",
    46: "الأحقاف", 47: "محمد", 48: "الفتح", 49: "الحجرات", 50: "ق", 51: "الذاريات", 52: "الطور",
    53: "النجم", 54: "القمر", 55: "الرحمن", 56: "الواقعة", 57: "الحديد", 58: "المجادلة", 59: "الحشر",
    60: "الممتحنة", 61: "الصف", 62: "الجمعة", 63: "المنافقون", 64: "التغابن", 65: "الطلاق", 66: "التحريم",
    67: "الملك", 68: "القلم", 69: "الحاقة", 70: "المعارج", 71: "نوح", 72: "الجن", 73: "المزمل", 74: "المدثر",
    75: "القيامة", 76: "الإنسان", 77: "المرسلات", 78: "النبأ", 79: "النازعات", 80: "عبس", 81: "التكوير",
    82: "الانفطار", 83: "المطففين", 84: "الانشقاق", 85: "البروج", 86: "الطارق", 87: "الأعلى", 88: "الغاشية",
    89: "الفجر", 90: "البلد", 91: "الشمس", 92: "الليل", 93: "الضحى", 94: "الشرح", 95: "التين", 96: "العلق",
    97: "القدر", 98: "البينة", 99: "الزلزلة", 100: "العاديات", 101: "القارعة", 102: "التكاثر", 103: "العصر",
    104: "الهمزة", 105: "الفيل", 106: "قريش", 107: "الماعون", 108: "الكوثر", 109: "الكافرون", 110: "النصر",
    111: "المسد", 112: "الإخلاص", 113: "الفلق", 114: "الناس"
}

quraa = {
    "Sudais": "عبد الرحمن السديس",
    "Shuraym": "سعود الشريم",
    "Ajmi": "أحمد العجمي",
    "Hudhaify": "علي الحذيفي",
    "Minshawi": "المنشاوي"
}

qari_links = {
    "Sudais": "Abdurrahmaan_As-Sudais_64kbps",
    "Shuraym": "Saood_ash-Shuraym_64kbps",
    "Ajmi": "Ahmad_Ajamy_64kbps",
    "Hudhaify": "Ali_Hudhaify_64kbps",
    "Minshawi": "Minshawy_Mujawwad_64kbps"
}

bot_active = True



async def send_full_surah(app: Application):
    global bot_active
    if not bot_active:
        return

    surah_num = random.randint(1, 114)
    surah_name = surahs[surah_num]
    qari_key = random.choice(list(qari_links.keys()))
    qari_folder = qari_links[qari_key]
    qari_name = quraa[qari_key]

    audio_url = f"http://www.everyayah.com/data/{qari_folder}/{str(surah_num).zfill(3)}.mp3"
    caption = f"📖 *سورة {surah_name}*\n🎙️ *القارئ:* {qari_name}\n\n🔊 تلاوة كاملة\n🕓 السورة القادمة خلال 6 ساعات بإذن الله."

    # 1. أرسل الرسالة النصية مع الصوت
    await app.bot.send_audio(chat_id=CHANNEL_ID, audio=audio_url, caption=caption, parse_mode='Markdown')

    # 2. أرسل صور السورة من موقع موثوق (كل صفحة صورة)
    img_base = f"https://www.quranflash.com/images/pages/"
    start_page = (surah_num - 1) * 2 + 1
    media = []
    for i in range(3):  # أرسل أول 3 صفحات فقط للتجربة
        page_num = start_page + i
        img_url = f"{img_base}{str(page_num).zfill(3)}.jpg"
        await app.bot.send_photo(chat_id=CHANNEL_ID, photo=img_url)

# أوامر التحكم
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ البوت يعمل الآن." if bot_active else "⛔️ البوت متوقف مؤقتًا.")

async def start_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bot_active
    bot_active = True
    await update.message.reply_text("✅ تم تشغيل البوت.")

async def stop_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bot_active
    bot_active = False
    await update.message.reply_text("⛔️ تم إيقاف البوت مؤقتًا.")

async def next_surah(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_full_surah(context.application)

# Flask للتشغيل المستمر
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "✅ Bot is running"

def run():
    flask_app.run(host="0.0.0.0", port=8080)

def keep_alive():
    Thread(target=run).start()

# جدولة كل 6 ساعات
async def scheduler(app: Application):
    while True:
        await send_full_surah(app)
        await asyncio.sleep(6 * 60 * 60)

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("start", start_bot))
    app.add_handler(CommandHandler("stop", stop_bot))
    app.add_handler(CommandHandler("next", next_surah))
    keep_alive()
    asyncio.create_task(scheduler(app))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
