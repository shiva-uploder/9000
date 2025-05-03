from time import time
from speedtest import Speedtest
import math
from telethon import events
from devgagan import botStartTime
from devgagan import sex as gagan

SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

# Convert seconds into a readable time format
def get_readable_time(seconds: int) -> str:
    result = ''
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)
    if days != 0:
        result += f'{days}d'
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)
    if hours != 0:
        result += f'{hours}h'
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)
    if minutes != 0:
        result += f'{minutes}m'
    seconds = int(seconds)
    result += f'{seconds}s'
    return result

# Convert bytes to human-readable format (e.g., KB, MB)
def get_readable_file_size(size_in_bytes) -> str:
    if size_in_bytes is None:
        return '0B'
    index = 0
    while size_in_bytes >= 1024:
        size_in_bytes /= 1024
        index += 1
    try:
        return f'{round(size_in_bytes, 2)}{SIZE_UNITS[index]}'
    except IndexError:
        return 'File too large'

# Speed test handler
@gagan.on(events.NewMessage(incoming=True, pattern='/speedtest'))
async def speedtest(event):
    status = await event.reply("**Running Speed Test... Please wait.**")
    
    # Run Speedtest
    test = Speedtest()
    test.get_best_server()
    test.download()
    test.upload()
    test.results.share()
    result = test.results.dict()
    image_path = result['share']
    
    # Calculate bot uptime
    currentTime = get_readable_time(time() - botStartTime)
    
    # Prepare the reply text with the new UI format
    reply_text = f"""
🟢 **Speed Test Completed!** 🟢

📶 **💡 Test Information:**
- **📥 Download Speed:** <code>{speed_convert(result['download'], False)}</code>
- **📤 Upload Speed:** <code>{speed_convert(result['upload'], False)}</code>
- **🕰️ Ping:** <code>{result['ping']} ms</code>
- **🗓️ Test Time:** <code>{result['timestamp']}</code>

⚡ **📊 Data Information:**
- **📤 Data Sent:** <code>{get_readable_file_size(int(result['bytes_sent']))}</code>
- **📥 Data Received:** <code>{get_readable_file_size(int(result['bytes_received']))}</code>

🌍 **Server Details:**
- **🏢 Server Name:** <code>{result['server']['name']}</code>
- **🌎 Country:** <code>{result['server']['country']}</code> | **Code:** <code>{result['server']['cc']}</code>
- **💨 Sponsor:** <code>{result['server']['sponsor']}</code>
- **📍 Location:** Lat: <code>{result['server']['lat']}</code>, Lon: <code>{result['server']['lon']}</code>
- **🕹️ Latency:** <code>{result['server']['latency']} ms</code>

🖥️ **Client Information:**
- **📶 IP Address:** <code>{result['client']['ip']}</code>
- **🌍 Country:** <code>{result['client']['country']}</code>
- **🌐 ISP:** <code>{result['client']['isp']}</code>
- **📈 ISP Rating:** <code>{result['client']['isprating']}</code>
- **📍 Location:** Lat: <code>{result['client']['lat']}</code>, Lon: <code>{result['client']['lon']}</code>

🔋 **Bot Uptime:** <code>{currentTime}</code>

🔒 **Powered by Team Nothing** 🔒
"""
    try:
        # Send the speed test result as a photo with the new UI
        await event.reply_photo(image_path, caption=reply_text, parse_mode="html")
    except Exception as e:
        # If there is an error, send the result as text
        await event.reply_text(reply_text, parse_mode="html")
    
    # Delete the "Running Speed Test..." status message
    await status.delete()

# Function to convert speed to a readable format
def speed_convert(size, byte=True):
    if not byte: size = size / 8
    power = 2 ** 10
    zero = 0
    units = {0: "B/s", 1: "KB/s", 2: "MB/s", 3: "GB/s", 4: "TB/s"}
    while size > power:
        size /= power
        zero += 1
    return f"{round(size, 2)} {units[zero]}"