import os
import re
import asyncio
from datetime import datetime
import jdatetime
from telethon import TelegramClient, events
from telethon.tl.functions.account import UpdateProfileRequest

# ---------------- تنظیمات ----------------

api_id = int(os.getenv("14992695"))
api_hash = os.getenv("a64a4b3fa559c59861d91a8860cebfb2")
allowed_user_id = int(os.getenv("+989302353247", "0"))

client = TelegramClient("session", api_id, api_hash)

enemies = {}
friends = {}
user_response_queue = {}

enemy_responses = [
    "پیامت ثبت شد.",
    "لطفاً محترمانه‌تر بنویس.",
    "این نوع پیام‌ها پذیرفته نمی‌شود.",
    "قوانین احترام را رعایت کن."
]

friend_responses = [
    "دمت گرم رفیق ❤️",
    "ارادت، پیامت رسید.",
    "رفاقتت قابل احترامه.",
    "مرسی که هستی."
]

# ---------------- پیام تایم ۰۰:۰۰ ----------------
daily_message = "روز جدید مبارک 🌙✨"

# ---------------- تاریخ ----------------

days_fa = {
    "Saturday": "شنبه",
    "Sunday": "یکشنبه",
    "Monday": "دوشنبه",
    "Tuesday": "سه‌شنبه",
    "Wednesday": "چهارشنبه",
    "Thursday": "پنج‌شنبه",
    "Friday": "جمعه"
}

months_fa = {
    1: "فروردین", 2: "اردیبهشت", 3: "خرداد", 4: "تیر",
    5: "مرداد", 6: "شهریور", 7: "مهر", 8: "آبان",
    9: "آذر", 10: "دی", 11: "بهمن", 12: "اسفند"
}

def get_info():
    now = jdatetime.datetime.now()
    g = now.togregorian()

    return {
        "time": now.strftime("%H:%M:%S"),
        "jalali": now.strftime("%Y/%m/%d"),
        "gregorian": g.strftime("%Y/%m/%d"),
        "day_fa": days_fa[g.strftime("%A")],
        "day_en": g.strftime("%A"),
        "month_fa": months_fa[now.month],
        "month_en": g.strftime("%B"),
        "utc": g.strftime("%Y-%m-%d %H:%M:%S")
    }

# ---------------- پاسخ ترتیبی ----------------

async def send_reply(event, lst):
    uid = event.sender_id
    if uid not in user_response_queue:
        user_response_queue[uid] = 0

    i = user_response_queue[uid]
    if i < len(lst):
        await event.reply(lst[i])
        user_response_queue[uid] += 1

# ---------------- سیو ----------------

async def save_media(event):
    if event.is_reply:
        rep = await event.get_reply_message()
        if event.raw_text == "سیو" and rep.media:
            await event.message.delete()
            media = await client.download_media(rep.media)
            await client.send_file("me", media)
            await client.send_message("me", "مدیا ذخیره شد ✓")

# ---------------- تغییر اسم ----------------

async def change_name(event):
    m = re.match(r"اسم عوض بشه به (.+)", event.raw_text)
    if m:
        new = m.group(1)
        await client(UpdateProfileRequest(first_name=new))
        await event.message.edit("اسم تغییر کرد ✓")

# ---------------- مدیریت لیست‌ها ----------------

async def manage_lists(event):
    if not event.is_reply:
        return

    rep = await event.get_reply_message()
    uid = rep.sender_id

    if "تنظیم بدخا" in event.raw_text:
        enemies[uid] = True
        await event.message.edit("به لیست بدخا اضافه شد.")
    elif "حذف بدخا" in event.raw_text:
        enemies.pop(uid, None)
        await event.message.edit("از لیست بدخا حذف شد.")
    elif "تنظیم مشتی" in event.raw_text:
        friends[uid] = True
        await event.message.edit("به لیست مشتی اضافه شد.")
    elif "حذف مشتی" in event.raw_text:
        friends.pop(uid, None)
        await event.message.edit("از لیست مشتی حذف شد.")

# ---------------- تایم کنار اسم ----------------

time_enabled = False

def fancy(t):
    return t.translate(str.maketrans("0123456789", "𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿"))

async def time_loop():
    global time_enabled
    while True:
        if time_enabled:
            now = datetime.now()
            t = fancy(f"{now.hour}:{now.minute:02d}")

            me = await client.get_me()
            name = re.sub(r"\s*[𝟶-𝟿]{1,2}:[𝟶-𝟿]{2}", "", me.first_name or "")
            await client(UpdateProfileRequest(first_name=f"{name.strip()} {t}"))

        await asyncio.sleep(35)

# ---------------- تایم ۰۰:۰۰ ----------------

async def midnight_sender():
    global daily_message
    sent_today = False

    while True:
        now = datetime.now()

        if now.hour == 0 and now.minute == 0:
            if not sent_today:
                await client.send_message("me", daily_message)
                sent_today = True
        else:
            sent_today = False

        await asyncio.sleep(30)

# ---------------- دستورات ----------------

async def commands(event):
    if event.sender_id != allowed_user_id:
        return

    t = event.raw_text

    if t == "راهنما":
        await event.message.edit(
            "📌 **لیست دستورات سلف**\n\n"
            "🕒 تایم کنار اسم:\n"
            "• تایم روشن\n"
            "• تایم خاموش\n\n"
            "📅 تاریخ:\n"
            "• تاریخ و ساعت\n\n"
            "🌙 پیام ۰۰:۰۰:\n"
            "• پیام ۰۰:۰۰ متن دلخواه\n\n"
            "👤 مدیریت اسم:\n"
            "• اسم عوض بشه به <اسم جدید>\n\n"
            "📥 ذخیره مدیا:\n"
            "• ریپلای → سیو\n\n"
            "⚔️ لیست بدخا:\n"
            "• ریپلای → تنظیم بدخا\n"
            "• ریپلای → حذف بدخا\n\n"
            "🤝 لیست مشتی:\n"
            "• ریپلای → تنظیم مشتی\n"
            "• ریپلای → حذف مشتی\n"
        )

    elif t == "تاریخ و ساعت":
        i = get_info()
        await event.message.edit(
            f"ساعت: {i['time']}\n"
            f"تاریخ: {i['jalali']} - {i['gregorian']}\n"
            f"روز: {i['day_fa']} - {i['day_en']}\n"
            f"ماه: {i['month_fa']} - {i['month_en']}\n"
            f"UTC: {i['utc']}"
        )

    elif t == "تایم روشن":
        global time_enabled
        time_enabled = True
        await event.message.edit("تایم روشن شد ✓")

    elif t == "تایم خاموش":
        time_enabled = False
        me = await client.get_me()
        name = re.sub(r"\s*[𝟶-𝟿]{1,2}:[𝟶-𝟿]{2}", "", me.first_name or "")
        await client(UpdateProfileRequest(first_name=name.strip()))
        await event.message.edit("تایم خاموش شد ✓")

    elif t.startswith("پیام ۰۰:۰۰ "):
        global daily_message
        daily_message = t.replace("پیام ۰۰:۰۰ ", "")
        await event.message.edit("پیام ۰۰:۰۰ تغییر کرد ✓")

    await manage_lists(event)
    await save_media(event)
    await change_name(event)

# ---------------- هندل پیام‌ها ----------------

@client.on(events.NewMessage)
async def handler(event):
    if event.sender_id == allowed_user_id:
        await commands(event)
        return

    uid = event.sender_id

    if uid in enemies:
        await send_reply(event, enemy_responses)
    elif uid in friends:
        await send_reply(event, friend_responses)

# ---------------- اجرا ----------------

async def main():
    await client.start()
    asyncio.create_task(time_loop())
    asyncio.create_task(midnight_sender())
    print("Bot is running...")
    await client.run_until_disconnected()

asyncio.run(main())
