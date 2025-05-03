# ---------------------------------------------------
# File Name: stats.py
# Description: Show total users, premium users, uptime & system info
# Author: Gagan | Modified by Ankit
# ---------------------------------------------------

import time
import sys
import motor
from pyrogram import filters
from config import OWNER_ID
from devgagan import app
from devgagan.core.mongo.users_db import get_users, add_user, get_user
from devgagan.core.mongo.plans_db import premium_users

# Store bot start time
BOT_START_TIME = time.time()

# Auto-user registration
@app.on_message(group=10)
async def chat_watcher_func(_, message):
    try:
        user_id = message.from_user.id
        if not await get_user(user_id):
            await add_user(user_id)
    except:
        pass  # Ignore failures silently


# Format uptime nicely
def get_uptime():
    seconds = int(time.time() - BOT_START_TIME)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    parts = []
    if days: parts.append(f"{days}d")
    if hours: parts.append(f"{hours}h")
    if minutes: parts.append(f"{minutes}m")
    if seconds: parts.append(f"{seconds}s")
    return ":".join(parts) or "0s"


# Show bot stats
@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def show_stats(client, message):
    start = time.time()

    try:
        all_users = await get_users()
        all_premium = await premium_users()
    except Exception as e:
        return await message.reply_text(f"**Error fetching stats:** `{e}`")

    uptime = get_uptime()
    ping = round((time.time() - start) * 1000)
    bot = await client.get_me()

    stats_text = f"""
**Bot Stats for {bot.mention}**

🟢 **Uptime:** `{uptime}`
📶 **Ping:** `{ping} ms`

👤 **Total Users:** `{len(all_users)}`
⭐ **Premium Users:** `{len(all_premium)}`

⚙️ **Python:** `{sys.version.split()[0]}`
🧬 **Motor/Mongo:** `{motor.version}`
"""

    await message.reply_text(stats_text)