import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from PIL import Image

BOT_TOKEN = os.environ.get("BOT_TOKEN")

user_images = {}

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "👋 Salom!\n\n"
        "📸 Bir nechta rasm yuboring.\n"
        "📄 Keyin /pdf deb yozing — men PDF qilib beraman."
    )
    user_images[update.effective_user.id] = []

def handle_photo(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    if user_id not in user_images:
        user_images[user_id] = []

    photo = update.message.photo[-1]
    file = photo.get_file()

    image_path = f"{user_id}_{len(user_images[user_id])}.jpg"
    file.download(image_path)

    user_images[user_id].append(image_path)
    update.message.reply_text("✅ Rasm qabul qilindi")

def make_pdf(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    images = user_images.get(user_id)

    if not images:
        update.message.reply_text("❌ Avval rasm yuboring")
        return

    pil_images = []
    for img in images:
        image = Image.open(img).convert("RGB")
        pil_images.append(image)

    pdf_path = f"{user_id}.pdf"
    pil_images[0].save(pdf_path, save_all=True, append_images=pil_images[1:])

    update.message.reply_document(open(pdf_path, "rb"))

    # tozalash
    for img in images:
        os.remove(img)
    os.remove(pdf_path)
    user_images[user_id] = []

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("pdf", make_pdf))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
