import random
import asyncio
import aiohttp
import schedule
import time
from flask import Flask
from threading import Thread
from telegram.ext import Application

TOKEN = "7805033056:AAFMHN1uZLY0wl3Tqnj4KxgHoW04bYBrZV0"
CHANNEL_ID = "@dzmmm"

surahs = {1: 7, 2: 286, 3: 200, 114: 6}
surah_names = {1: "الفاتحة", 2: "البقرة", 3: "آل عمران", 114: "الناس"}

def get_audio_url(surah, ayah):
    return f"http://www.everyayah.com/data/Husary_128kbps/{str(surah).zfill(3)}{str(ayah).zfill(3)}.mp3"

async def get_ayah_text(surah, ayah):
    url = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/ar"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return data["data"]["text"]

async def send_random_ayah_with_audio(app):
    surah_num = random.choice(list(surahs.keys()))
    ayah_num = random.randint(1, surahs[surah_num])
    text = await get_ayah_text(surah_num, ayah_num)
    audio = get_audio_url(surah_num, ayah_num)
    caption = f"📖 سورة {surah_names[surah_num]} - الآية {ayah_num}

{text}"
    await app.bot.send_audio(chat_id=CHANNEL_ID, audio=audio, caption=caption)

app_web = Flask('')
@app_web.route('/')
def home():
    return "✅ البوت شغال بإذن الله"

def run():
    app_web.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

async def job_scheduler(app):
    schedule.every(60).seconds.do(lambda: asyncio.create_task(send_random_ayah_with_audio(app)))
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

async def main():
    app = Application.builder().token(TOKEN).build()
    keep_alive()
    await job_scheduler(app)

if __name__ == "__main__":
    t = Thread(target=lambda: asyncio.run(main()))
    t.start()
    while True:
        time.sleep(10)
