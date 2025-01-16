import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# API endpoint
ENHANCER_API = "https://for-free.serv00.net/C/img_enhancer.php?url="

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message when the user starts the bot."""
    await update.message.reply_text(
        "Welcome! Send me a photo, and I'll enhance it for you."
    )

async def enhance_photo(photo_url: str) -> str:
    """
    Send the photo URL to the API and return the enhanced photo URL.
    """
    try:
        response = requests.get(ENHANCER_API + photo_url)
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "success":
            return data.get("image")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photos sent by the user."""
    photo = update.message.photo[-1]  # Get the highest resolution photo
    file = await context.bot.get_file(photo.file_id)
    file_url = file.file_path  # Get the direct URL to the photo

    await update.message.reply_text("Enhancing your photo, please wait...")

    # Enhance photo using the API
    enhanced_url = await enhance_photo(file_url)
    if enhanced_url:
        await update.message.reply_photo(enhanced_url, caption="Here is your enhanced photo!")
    else:
        await update.message.reply_text("Sorry, I couldn't enhance the photo. Please try again.")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo files sent by the user."""
    file = update.message.document
    if not file.mime_type.startswith("image/"):
        await update.message.reply_text("Please send a valid image file!")
        return

    file_obj = await context.bot.get_file(file.file_id)
    file_url = file_obj.file_path  # Get the direct URL to the file

    await update.message.reply_text("Enhancing your photo, please wait...")

    # Enhance photo using the API
    enhanced_url = await enhance_photo(file_url)
    if enhanced_url:
        await update.message.reply_photo(enhanced_url, caption="Here is your enhanced photo!")
    else:
        await update.message.reply_text("Sorry, I couldn't enhance the photo. Please try again.")

def main():
    """Run the bot."""
    TOKEN = "7542750844:AAHy_rrWqETDZEqQJ5HVWlaKsEADCcfF3UE"  # Replace with your bot token
    application = Application.builder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    # Start polling
    application.run_polling()
    print("Bot is running...")

if __name__ == "__main__":
    main()
