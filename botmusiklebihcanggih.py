from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import os
import random
import logging
from dotenv import load_dotenv


load_dotenv()  # Memuat isi file .env

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Ambil token dari file .env

print("Token Bot:", BOT_TOKEN)  #cek apakah berhasil (opsional)

# === DIREKTORI FILE MUSIK ===
direktori_musik = "musik"

# === DATA PENGGUNA ===
data_pengguna = {}

# === INISIALISASI LOGGING ===
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# === PERINTAH /start ===
def start(update: Update, context: CallbackContext) -> None:
    keyboard = [[InlineKeyboardButton("🎵 Buat Musik", callback_data='buatmusik')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Selamat datang! Klik tombol di bawah untuk membuat musik:", reply_markup=reply_markup)

# === FUNGSI UTAMA PEMBUATAN MUSIK ===
def buatmusik(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user = query.from_user
    user_id = str(user.id)
    nama = user.first_name

    # Hapus tombol dan beri notifikasi loading
    query.answer()
    query.edit_message_text("🎧 Sabar yah musiknya lagi dibuat...")

    # Inisialisasi pengguna
    if user_id not in data_pengguna:
        data_pengguna[user_id] = {
            "nama": nama,
            "klik": 0,
            "musik_terkirim": []
        }

    data_pengguna[user_id]["klik"] += 1

    # Ambil daftar musik
    semua_musik = [f for f in os.listdir(direktori_musik) if f.endswith((".mp3", ".wav"))]
    terkirim = data_pengguna[user_id]["musik_terkirim"]

    # Reset jika semua lagu sudah terkirim
    if set(terkirim) == set(semua_musik):
        terkirim.clear()

    # Pilih musik acak yang belum dikirim
    pilihan = list(set(semua_musik) - set(terkirim))
    lagu = random.choice(pilihan)
    path = os.path.join(direktori_musik, lagu)

    # Kirim musik ke pengguna
    context.bot.send_audio(chat_id=query.message.chat_id, audio=open(path, 'rb'))

    # Simpan ke log pengguna
    terkirim.append(lagu)

    # Tampilkan log ke terminal
    logging.info(f"[{nama} | ID: {user_id}] klik ke-{data_pengguna[user_id]['klik']} | Kirim: {lagu}")

    # Tampilkan tombol lagi
    keyboard = [[InlineKeyboardButton("🎵 Buat Musik", callback_data='buatmusik')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=query.message.chat_id, text="Klik lagi untuk musik lainnya!", reply_markup=reply_markup)

# === FUNGSI HANDLE TOMBOL ===
def respon_tombol(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if query.data == 'buatmusik':
        buatmusik(update, context)

# === PERINTAH /log UNTUK TERMINAL SAJA ===
def tampilkan_log(update: Update, context: CallbackContext) -> None:
    print("\n=== STATISTIK PENGGUNA ===")
    for uid, info in data_pengguna.items():
        print(f"{info['nama']} (ID: {uid})")
        print(f"  Jumlah klik: {info['klik']}")
        print(f"  Musik terkirim: {', '.join(info['musik_terkirim']) if info['musik_terkirim'] else 'Belum ada'}\n")
    print("=== AKHIR LOG ===\n")
    update.message.reply_text("📊 Statistik pengguna ditampilkan di terminal (bukan di Telegram).")

# === MAIN ===
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("log", tampilkan_log))
    dp.add_handler(CallbackQueryHandler(respon_tombol))

    print("Bot berjalan... Buka Telegram dan ketik /start.")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()