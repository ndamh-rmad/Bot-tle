import os
import random
import asyncio
import datetime
from flask import Flask
from threading import Thread
from collections import defaultdict

from telegram.ext import Application, CommandHandler, ContextTypes

# إعداد المتغيرات البيئية
TOKEN = os.getenv("BOT_TOKEN", "")
CHANNEL_ID = os.getenv("CHANNEL_ID", "")

# بيانات السور والمقرئين
surahs = {
    112: "الإخلاص", 113: "الفلق", 114: "الناس", 18: "الكهف"
}
reciters = [
    ("السديس", "https://server6.mp3quran.net/sds"),
    ("الشرميم", "https://server10.mp3quran.net/shur"),
    ("العجمي", "https://server7.mp3quran.net/ajm")
]
azkar_list = [
    "سبحان الله", "الحمد لله", "لا إله إلا الله", "الله أكبر",
    "لا حول ولا قوة إلا بالله", "اللهم صل وسلم على نبينا محمد"
]

# إحصائيات
stats = defaultdict(int)

# Flask app لتشغيل الويب
app_web = Flask(__name__)
@app_web.route('/')
def home():
    return "✅ البوت شغال بإذن الله"

def run():
    app_web.run(host="0.0.0.0", port=8080)

def keep_alive():
    Thread(target=run).start()

# دوال الإرسال
async def send_surah(app):
    surah_num = random.choice(list(surahs.keys()))
    reciter_name, reciter_url = random.choice(reciters)
    name = surahs[surah_num]
    audio = f"{reciter_url}/{str(surah_num).zfill(3)}001.mp3"
    image = f"https://quran-images-api.vercel.app/surah/{surah_num}"

    await app.bot.send_message(chat_id=CHANNEL_ID, text=f"📖 سورة {name}\n🎙️ القارئ: {reciter_name}")
    await app.bot.send_photo(chat_id=CHANNEL_ID, photo=image)
    await app.bot.send_audio(chat_id=CHANNEL_ID, audio=audio, title=name)
    stats["السور"] += 1

async def send_zekr(app):
    text = random.choice(azkar_list)
    await app.bot.send_message(chat_id=CHANNEL_ID, text=f"🕊️ {text}")
    stats["الأذكار"] += 1

async def send_friday_package(app):
    await app.bot.send_message(chat_id=CHANNEL_ID, text="🌸 جمعة مباركة! لا تنس قراءة سورة الكهف.")
    await send_surah(app)
    await app.bot.send_message(chat_id=CHANNEL_ID, text="🤲 اللهم اجعل هذا اليوم فرجًا لكل مهموم")

# أوامر المستخدم
async def start(update, context):
    await update.message.reply_text("👋 مرحبًا، البوت شغال! استخدم /help لرؤية الأوامر.")

async def help_command(update, context):
    await update.message.reply_text(
        "/start - بدء التشغيل\n"
        "/help - المساعدة\n"
        "/stats - عرض الإحصائيات\n"
        "/now - إرسال سورة وذكر الآن"
    )

async def stats_command(update, context):
    report = "\n".join([f"{k}: {v}" for k, v in stats.items()]) or "لا توجد بيانات بعد."
    await update.message.reply_text(f"📊 الإحصائيات:\n{report}")

async def now_command(update, context):
    await update.message.reply_text("⏱️ يتم الإرسال الآن...")
    await send_surah(context.application)
    await send_zekr(context.application)

# المهام المجدولة
async def scheduler(app):
    while True:
        now = datetime.datetime.now()
        if now.hour % 6 == 0 and now.minute == 0:
            await send_surah(app)
        if now.hour % 3 == 0 and now.minute == 0:
            await send_zekr(app)
        if now.weekday() == 4 and now.hour == 8 and now.minute == 0:
            await send_friday_package(app)
        await asyncio.sleep(60)

# تشغيل البوت
async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("now", now_command))

    keep_alive()

    asyncio.create_task(scheduler(app))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
