import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image

BOT_TOKEN = os.getenv("BOT_TOKEN")

user_images = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Rasmni PDFga aylantirish"]]
    await update.message.reply_text(
        "Start ✅\n\nRasmlarni ketma-ket yuboring, keyin PDF qilib beraman.",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)

    os.makedirs(f"temp/{user_id}", exist_ok=True)
    image_path = f"temp/{user_id}/{photo.file_id}.jpg"
    await file.download_to_drive(image_path)

    user_images.setdefault(user_id, []).append(image_path)
    await update.message.reply_text("✅ Rasm qabul qilindi. Yana yuboring yoki /pdf deb yozing.")

async def make_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    images = user_images.get(user_id)

    if not images:
        await update.message.reply_text("❌ Avval rasmlar yuboring.")
        return

    pil_images = [Image.open(img).convert("RGB") for img in images]
    pdf_path = f"temp/{user_id}/result.pdf"
    pil_images[0].save(pdf_path, save_all=True, append_images=pil_images[1:])

    await update.message.reply_document(document=open(pdf_path, "rb"))

    # cleanup
    for img in images:
        os.remove(img)
    os.remove(pdf_path)
    os.rmdir(f"temp/{user_id}")
    user_images.pop(user_id)

async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pdf", make_pdf))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))

    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
