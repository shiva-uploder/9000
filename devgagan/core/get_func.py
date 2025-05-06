# ---------------------------------------------------
# File Name: get_func_optimized.py
# Description: Optimized Pyrogram bot for Telegram file handling with Heroku memory fixes
# Author: Gagan
# Improved Memory Handling for Heroku
# ---------------------------------------------------

import asyncio
import time
import gc
import os
import re
from typing import Callable, Dict, Set
from devgagan import app
import aiofiles
from devgagan import sex as gf
from telethon.tl.types import DocumentAttributeVideo, Message
from telethon.sessions import StringSession
import pymongo
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import ChannelBanned, ChannelInvalid, ChannelPrivate, ChatIdInvalid, ChatInvalid
from pyrogram.enums import MessageMediaType, ParseMode
from devgagan.core.func import *
from pyrogram.errors import RPCError
from pyrogram.types import Message
from config import MONGO_DB as MONGODB_CONNECTION_STRING, LOG_GROUP, OWNER_ID, STRING, API_ID, API_HASH
from devgagan.core.mongo import db as odb
from telethon import TelegramClient, events, Button
from devgagantools import fast_upload

# Memory Optimization Functions
async def memory_cleanup():
    """Force garbage collection with delay"""
    for _ in range(3):
        gc.collect()
        await asyncio.sleep(0.5)

async def remove_file_safe(file_path: str, max_retries: int = 3) -> bool:
    """Safely remove file with retries and memory cleanup"""
    for attempt in range(max_retries):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                await memory_cleanup()
                return True
        except Exception as e:
            print(f"File removal failed (attempt {attempt+1}): {str(e)}")
            await asyncio.sleep(1)
            await memory_cleanup()
    return False

def check_memory_usage():
    """Check if memory usage is critical"""
    try:
        import psutil
        return psutil.virtual_memory().percent > 85
    except:
        return False

# Core Functions
async def upload_media(sender, target_chat_id, file, caption, edit, topic_id):
    try:
        await memory_cleanup()
        if check_memory_usage():
            await edit.edit("⚠️ Optimizing memory usage...")
            await asyncio.sleep(2)

        upload_method = await fetch_upload_method(sender)
        metadata = video_metadata(file)
        width, height, duration = metadata['width'], metadata['height'], metadata['duration']
        
        try:
            thumb_path = await screenshot(file, duration, sender)
        except Exception:
            thumb_path = None

        video_formats = {'mp4', 'mkv', 'avi', 'mov'}
        document_formats = {'pdf', 'docx', 'txt', 'epub'}
        image_formats = {'jpg', 'png', 'jpeg'}

        if upload_method == "Pyrogram":
            if file.split('.')[-1].lower() in video_formats:
                dm = await app.send_video(
                    chat_id=target_chat_id,
                    video=file,
                    caption=caption,
                    height=height,
                    width=width,
                    duration=duration,
                    thumb=thumb_path,
                    reply_to_message_id=topic_id,
                    parse_mode=ParseMode.MARKDOWN,
                    progress=progress_bar,
                    progress_args=("╭─────────────────────╮\n│      **__Uploading__**\n├─────────────────────", edit, time.time())
                )
                await dm.copy(LOG_GROUP)
                
            elif file.split('.')[-1].lower() in image_formats:
                dm = await app.send_photo(
                    chat_id=target_chat_id,
                    photo=file,
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN,
                    progress=progress_bar,
                    reply_to_message_id=topic_id,
                    progress_args=("╭─────────────────────╮\n│      **__Uploading__**\n├─────────────────────", edit, time.time())
                )
                await dm.copy(LOG_GROUP)
            else:
                dm = await app.send_document(
                    chat_id=target_chat_id,
                    document=file,
                    caption=caption,
                    thumb=thumb_path,
                    reply_to_message_id=topic_id,
                    progress=progress_bar,
                    parse_mode=ParseMode.MARKDOWN,
                    progress_args=("╭─────────────────────╮\n│      **__Uploading__**\n├─────────────────────", edit, time.time())
                )
                await asyncio.sleep(2)
                await dm.copy(LOG_GROUP)

        elif upload_method == "Telethon":
            await edit.delete()
            progress_message = await gf.send_message(sender, "**__Uploading...__**")
            caption = await format_caption_to_html(caption)
            uploaded = await fast_upload(
                gf, file,
                reply=progress_message,
                name=None,
                progress_bar_function=lambda done, total: progress_callback(done, total, sender),
                user_id=sender
            )
            await progress_message.delete()

            attributes = [
                DocumentAttributeVideo(
                    duration=duration,
                    w=width,
                    h=height,
                    supports_streaming=True
                )
            ] if file.split('.')[-1].lower() in video_formats else []

            await gf.send_file(
                target_chat_id,
                uploaded,
                caption=caption,
                attributes=attributes,
                reply_to=topic_id,
                parse_mode='html',
                thumb=thumb_path
            )
            await gf.send_file(
                LOG_GROUP,
                uploaded,
                caption=caption,
                attributes=attributes,
                parse_mode='html',
                thumb=thumb_path
            )

    except Exception as e:
        await app.send_message(LOG_GROUP, f"**Upload Failed:** {str(e)}")
        print(f"Upload error: {e}")

    finally:
        if thumb_path:
            await remove_file_safe(thumb_path)
        await remove_file_safe(file)
        await memory_cleanup()

async def get_msg(userbot, sender, edit_id, msg_link, i, message):
    file = ''
    edit = ''
    try:
        msg_link = msg_link.split("?single")[0]
        chat, msg_id = None, None
        saved_channel_ids = load_saved_channel_ids()
        size_limit = 2 * 1024 * 1024 * 1024  # 2GB size limit

        if 't.me/c/' in msg_link or 't.me/b/' in msg_link:
            parts = msg_link.split("/")
            if 't.me/b/' in msg_link:
                chat = parts[-2]
                msg_id = int(parts[-1]) + i
            else:
                chat = int('-100' + parts[parts.index('c') + 1])
                msg_id = int(parts[-1]) + i

            if chat in saved_channel_ids:
                await app.edit_message_text(
                    message.chat.id, edit_id,
                    "Sorry! This channel is protected."
                )
                return
            
        elif '/s/' in msg_link:
            edit = await app.edit_message_text(sender, edit_id, "Processing story...")
            if userbot is None:
                await edit.edit("Login required for stories")
                return
            parts = msg_link.split("/")
            chat = parts[3]
            chat = f"-100{chat}" if chat.isdigit() else chat
            msg_id = int(parts[-1])
            await download_user_stories(userbot, chat, msg_id, edit, sender)
            await edit.delete()
            return
        
        else:
            edit = await app.edit_message_text(sender, edit_id, "Processing public link...")
            chat = msg_link.split("t.me/")[1].split("/")[0]
            msg_id = int(msg_link.split("/")[-1])
            await copy_message_with_chat_id(app, userbot, sender, chat, msg_id, edit)
            await edit.delete()
            return
            
        msg = await userbot.get_messages(chat, msg_id)
        if msg.service or msg.empty:
            await app.delete_messages(sender, edit_id)
            return

        target_chat_id = user_chat_ids.get(message.chat.id, message.chat.id)
        topic_id = None
        if '/' in str(target_chat_id):
            target_chat_id, topic_id = map(int, target_chat_id.split('/', 1))

        if msg.media == MessageMediaType.WEB_PAGE_PREVIEW:
            await clone_message(app, msg, target_chat_id, topic_id, edit_id, LOG_GROUP)
            return

        if msg.text:
            await clone_text_message(app, msg, target_chat_id, topic_id, edit_id, LOG_GROUP)
            return

        if msg.sticker:
            await handle_sticker(app, msg, target_chat_id, topic_id, edit_id, LOG_GROUP)
            return

        file_size = get_message_file_size(msg)
        file_name = await get_media_filename(msg)
        edit = await app.edit_message_text(sender, edit_id, "**Downloading...**")

        file = await userbot.download_media(
            msg,
            file_name=file_name,
            progress=progress_bar,
            progress_args=("╭─────────────────────╮\n│      **__Downloading__**\n├─────────────────────", edit, time.time())
        )
        
        caption = await get_final_caption(msg, sender)
        file = await rename_file(file, sender)

        if msg.audio:
            result = await app.send_audio(target_chat_id, file, caption=caption, reply_to_message_id=topic_id)
            await result.copy(LOG_GROUP)
            await edit.delete()
        try:
    await remove_file()
except Exception as e:
    print(f"File hataate waqt error: {e}")
