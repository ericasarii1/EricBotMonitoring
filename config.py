import asyncio
import psutil
from telegram import Bot
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder

# === KONFIGURASI ===
BOT_TOKEN = "YOUR_PANEL_BOT_TOKEN"
GROUP_ID = -1001234567890
TOPIC_ID = 1234
CHECK_INTERVAL = 60

# Daftar proses bot (cek berdasarkan nama file atau keyword proses)
bots_to_monitor = {
    "Bot AntiSpam": "bot_antispam.py",
    "Bot Monitor": "bot_monitor.py",
    "Bot Log": "bot_log.py",
}

PANEL_MSG_ID = None

# Cek proses berjalan berdasarkan nama file
def is_process_running(keyword: str) -> bool:
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if any(keyword in str(arg) for arg in proc.info['cmdline']):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

# Bangun teks panel
def build_panel_text(statuses: dict) -> str:
    lines = ["📊 <b>Status Uptime Bot</b>\n"]
    for name, online in statuses.items():
        emoji = "🟢" if online else "🔴"
        status = "ONLINE" if online else "OFFLINE"
        lines.append(f"{emoji} <b>{name}</b> - {status}")
    return "\n".join(lines)

# Loop update
async def update_panel_loop(app):
    global PANEL_MSG_ID
    while True:
        statuses = {
            name: is_process_running(keyword)
            for name, keyword in bots_to_monitor.items()
        }
        panel_text = build_panel_text(statuses)

        try:
            if PANEL_MSG_ID:
                await app.bot.edit_message_text(
                    chat_id=GROUP_ID,
                    message_id=PANEL_MSG_ID,
                    message_thread_id=TOPIC_ID,
                    text=panel_text,
                    parse_mode=ParseMode.HTML
                )
            else:
                msg = await app.bot.send_message(
                    chat_id=GROUP_ID,
                    message_thread_id=TOPIC_ID,
                    text=panel_text,
                    parse_mode=ParseMode.HTML
                )
                PANEL_MSG_ID = msg.message_id
        except Exception as e:
            print("Gagal update panel:", e)

        await asyncio.sleep(CHECK_INTERVAL)

# Start
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    asyncio.create_task(update_panel_loop(app))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
