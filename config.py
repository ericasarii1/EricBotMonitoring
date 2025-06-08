from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import asyncio
import time
import os

# === KONFIGURASI ===
BOT_NAME = os.getenv("BOT_NAME", "Bot Anime 1")  # Nama bot ini sendiri
TOKEN = os.getenv("TOKEN")  # Token bot ini
CHAT_ID_GRUP = int(os.getenv("GRUP_ID", "-100xxxxxxxxx"))  # Grup tujuan laporan
MESSAGE_THREAD_ID = int(os.getenv("TOPIK_ID", "1234"))  # ID topik grup

# Daftar bot lain yang harus kirim heartbeat (termasuk bot ini sendiri)
DAFTAR_BOT = [
    "Bot Anime 1", "Bot Anime 2", "Bot Admin", "Bot Tools", "Bot Anime 3"
]

# Penyimpanan waktu terakhir heartbeat
last_heartbeat = {}

# === Kirim heartbeat ke diri sendiri ===
async def kirim_heartbeat(application: Application):
    while True:
        try:
            await application.bot.send_message(
                chat_id=application.bot.id,
                text=f"HEARTBEAT::{BOT_NAME}::{int(time.time())}"
            )
        except Exception as e:
            print("Gagal kirim heartbeat:", e)
        await asyncio.sleep(60)  # Setiap 60 detik

# === Terima heartbeat dari semua bot ===
async def handle_heartbeat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text
        if text.startswith("HEARTBEAT::"):
            _, nama_bot, timestamp = text.split("::")
            last_heartbeat[nama_bot] = int(timestamp)
    except Exception as e:
        print("Gagal parsing heartbeat:", e)

# === Cek status bot-bot lain ===
async def cek_status_bot(application: Application):
    while True:
        now = int(time.time())
        mati = []
        for nama in DAFTAR_BOT:
            last = last_heartbeat.get(nama, 0)
            if now - last > 180:  # Lebih dari 3 menit dianggap mati
                mati.append(nama)

        if mati:
            msg = "❌ Bot yang kemungkinan *mati*:\n" + "\n".join(f"- {m}" for m in mati)
            try:
                await application.bot.send_message(
                    chat_id=CHAT_ID_GRUP,
                    message_thread_id=MESSAGE_THREAD_ID,
                    text=msg,
                    parse_mode="Markdown"
                )
            except Exception as e:
                print("Gagal kirim laporan:", e)

        await asyncio.sleep(300)  # Cek setiap 5 menit

# === Fungsi utama ===
def main():
    print(f"[INFO] {BOT_NAME} mulai menjalankan monitoring...")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_heartbeat))

    # Jalankan task heartbeat dan pengecekan status bot
    app.job_queue.run_repeating(lambda ctx: asyncio.create_task(kirim_heartbeat(app)), interval=60, first=0)
    app.job_queue.run_repeating(lambda ctx: asyncio.create_task(cek_status_bot(app)), interval=300, first=60)

    app.run_polling()

# === Jalankan ===
if __name__ == "__main__":
    main()
