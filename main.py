import os, random, asyncio, datetime
import aiohttp
import schedule
from flask import Flask
from threading import Thread
from telegram.ext import Application, CommandHandler
from collections import defaultdict

# إعدادات البوت
TOKEN = os.getenv("BOT_TOKEN", "توكن_البوت")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@dzmmm")

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

stats = defaultdict(int)
last_sent = None

# Web server (لبقاء البوت حي)
app_web = Flask('')
@app_web.route('/')
def home():
    return "✅ البوت شغال بإذن الله"
def run():
    app_web.run(host='0.0.0.0', port=8080)
def keep_alive():
    Thread(target=run).start()

# إرسال سورة
async def send_surah(app):
    global last_sent
    surah_num = random.choice(list(surahs.keys()))
    reciter_name, reciter_url = random.choice(reciters)
    name = surahs[surah_num]
    audio = f"{reciter_url}/{str(surah_num).zfill(3)}001.mp3"
    image = f"https://quran-images-api.vercel.app/surah/{surah_num}"

    try:
        await app.bot.send_message(chat_id=CHANNEL_ID, text=f"📖 سورة {name}\n🎙️ القارئ: {reciter_name}")
        await app.bot.send_photo(chat_id=CHANNEL_ID, photo=image)
        await app.bot.send_audio(chat_id=CHANNEL_ID, audio=audio, title=name)
        stats["السور"] += 1
        last_sent = datetime.datetime.now()
    except Exception as e:
        print("❌ خطأ أثناء الإرسال:", e)

# إرسال أذكار
async def send_zekr(app):
    text = random.choice(azkar_list)
    await app.bot.send_message(chat_id=CHANNEL_ID, text=f"🕊️ {text}")
    stats["الأذكار"] += 1

# حزمة الجمعة
async def send_friday_package(app):
    await app.bot.send_message(chat_id=CHANNEL_ID, text="🌸 جمعة مباركة! لا تنس قراءة سورة الكهف.")
    await send_surah(app)
    await app.bot.send_message(chat_id=CHANNEL_ID, text="🤲 اللهم اجعل هذا اليوم فرجًا لكل مهموم")

# جدولة المهام
async def job_scheduler(app):
    schedule.every(6).hours.do(lambda: asyncio.create_task(send_surah(app)))
    schedule.every(3).hours.do(lambda: asyncio.create_task(send_zekr(app)))
    schedule.every().friday.at("08:00").do(lambda: asyncio.create_task(send_friday_package(app)))

    while True:
        schedule.run_pending()
        await asyncio.sleep(30)

# أوامر التليجرام
async def start(update, context):
    await update.message.reply_text("👋 أهلاً بك، البوت يعمل الآن.")

async def help_command(update, context):
    await update.message.reply_text(
        "/start - بدء التشغيل\n"
        "/help - الأوامر المتاحة\n"
        "/stats - عرض الإحصائيات\n"
        "/next - وقت الإرسال القادم\n"
        "/now - إرسال سورة الآن يدويًا"
    )

async def stats_command(update, context):
    report = "\n".join([f"{k}: {v}" for k, v in stats.items()]) or "لا توجد بيانات بعد."
    await update.message.reply_text(f"📊 الإحصائيات:\n{report}")

async def next_command(update, context):
    now = datetime.datetime.now()
    next_time = now + datetime.timedelta(hours=6)
    await update.message.reply_text(f"⏰ الإرسال القادم: {next_time.strftime('%H:%M:%S')}")

async def now_command(update, context):
    await update.message.reply_text("📤 إرسال سورة الآن...")
    await send_surah(context.application)

# بدء التشغيل
async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("next", next_command))
    app.add_handler(CommandHandler("now", now_command))

    keep_alive()
    asyncio.create_task(job_scheduler(app))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
