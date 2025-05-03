# ---------------------------------------------------
# File Name: start.py
# Description: A Pyrogram bot for downloading files
# Author: Gagan | Refactored by Ankit
# ---------------------------------------------------

from pyrogram import filters
from pyrogram.types import (
    CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    BotCommand, Message
)
from devgagan import app
from config import OWNER_ID
from devgagan.core.func import subscribe

# ----------------- SET COMMAND -----------------
@app.on_message(filters.command("set"))
async def set_commands(_, message: Message):
    if message.from_user.id not in OWNER_ID:
        return await message.reply("**❌ You are not authorized to use this command.**")

    await app.set_bot_commands([
        BotCommand("start", "🚀 Start the bot"),
        BotCommand("batch", "🫠 Extract in bulk"),
        BotCommand("login", "🔑 Login to the bot"),
        BotCommand("logout", "🚪 Logout from the bot"),
        BotCommand("token", "🎲 Get 3 hours free access"),
        BotCommand("adl", "👻 Download audio from 30+ sites"),
        BotCommand("dl", "💀 Download videos from 30+ sites"),
        BotCommand("freez", "🧊 Remove all expired users"),
        BotCommand("pay", "💳 Pay now to get a subscription"),
        BotCommand("status", "⟳ Refresh payment status"),
        BotCommand("transfer", "💝 Gift premium to others"),
        BotCommand("myplan", "📋 Get your plan details"),
        BotCommand("add", "➕ Add user to premium"),
        BotCommand("rem", "➖ Remove from premium"),
        BotCommand("session", "🧵 Generate Pyrogramv2 session"),
        BotCommand("settings", "⚙️ Personalize your bot"),
        BotCommand("stats", "📊 Get stats of the bot"),
        BotCommand("plan", "🗓️ Check our premium plans"),
        BotCommand("terms", "📜 Terms and Conditions"),
        BotCommand("speedtest", "🚅 Test server speed"),
        BotCommand("lock", "🔒 Protect channel from extraction"),
        BotCommand("gcast", "⚡ Broadcast a message to all users"),
        BotCommand("help", "❓ Need help?"),
        BotCommand("cancel", "🚫 Cancel batch process")
    ])
    await message.reply("✅ **Commands configured successfully!**")


# ----------------- HELP COMMAND -----------------
help_pages = [
    "...(Page 1 content as-is)...",
    "...(Page 2 content as-is)..."
]

async def send_or_edit_help_page(client, message, page_number):
    if page_number < 0 or page_number >= len(help_pages):
        return

    buttons = []
    if page_number > 0:
        buttons.append(InlineKeyboardButton("◀️ Previous", callback_data=f"help_prev_{page_number}"))
    if page_number < len(help_pages) - 1:
        buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"help_next_{page_number}"))

    await message.delete()
    await message.reply(help_pages[page_number], reply_markup=InlineKeyboardMarkup([buttons]))


@app.on_message(filters.command("help"))
async def help_command(client, message: Message):
    if await subscribe(client, message) == 1:
        return
    await send_or_edit_help_page(client, message, 0)


@app.on_callback_query(filters.regex(r"help_(prev|next)_(\d+)"))
async def help_navigation(client, query: CallbackQuery):
    action, page = query.data.split("_")[1], int(query.data.split("_")[2])
    page += -1 if action == "prev" else 1
    await send_or_edit_help_page(client, query.message, page)
    await query.answer()


# ----------------- TERMS -----------------
@app.on_message(filters.command("terms") & filters.private)
async def terms(client, message: Message):
    text = (
        "📜 **Terms and Conditions** 📜\n\n"
        "✨ We are not responsible for user actions.\n"
        "✨ Payment does not guarantee permanent access...\n"
        "🔒 Only premium members can enjoy certain benefits...\n"
    )
    buttons = [
        [InlineKeyboardButton("📋 See Premium Plans", callback_data="see_plan")],
        [InlineKeyboardButton("💬 Contact Now", url="https://t.me/SRC_SOLUTION_BOT")],
    ]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))


# ----------------- PLAN -----------------
@app.on_message(filters.command("plan") & filters.private)
async def plan(client, message: Message):
    text = (
        "💰 **Premium Plans** 💰\n\n"
        "Starting from $2 or 200 INR via Amazon Gift Card...\n"
        "For more details on premium plans, check below! 🎯\n"
    )
    buttons = [
        [InlineKeyboardButton("📜 See Terms", callback_data="see_terms")],
        [InlineKeyboardButton("💬 Contact Now", url="https://t.me/SRC_SOLUTION_BOT")],
    ]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@app.on_callback_query(filters.regex("see_plan"))
async def see_plan(client, query: CallbackQuery):
    await query.message.edit_text(
        "💰 **Premium Plans** 💰\n\n"
        "Starting from $2 or 200 INR...\n"
        "For more details, contact us or check our Terms below! 🎯",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📜 See Terms", callback_data="see_terms")],
            [InlineKeyboardButton("💬 Contact Now", url="https://t.me/SRC_SOLUTION_BOT")],
        ])
    )
    await query.answer()


@app.on_callback_query(filters.regex("see_terms"))
async def see_terms(client, query: CallbackQuery):
    await query.message.edit_text(
        "📜 **Terms and Conditions** 📜\n\n✨ We are not responsible for users' actions...\n"
        "✨ Payments do not guarantee authorization...\n"
        "🔒 Premium access is required for some features...\n",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 See Plans", callback_data="see_plan")],
            [InlineKeyboardButton("💬 Contact Now", url="https://t.me/SRC_SOLUTION_BOT")],
        ])
    )
    await query.answer()