from telegram import Update, InputFile
from telegram.ext import ContextTypes
from photo_processor import enhance_photo

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /start command."""
    await update.message.reply_text("Welcome! Send me a photo, and I'll enhance it for you.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for receiving photos."""
    try:
        photo_file = await update.message.photo[-1].get_file()
        photo_url = photo_file.file_path

        # Notify the user that the process is starting
        await update.message.reply_text("Enhancing your photo, please wait...")

        # Enhance photo using the API
        enhanced_photo_url = enhance_photo(photo_url)

        if enhanced_photo_url:
            # Send the enhanced photo to the user
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=enhanced_photo_url,
                caption="Here is your enhanced photo!"
            )
        else:
            await update.message.reply_text("Sorry, I couldn't enhance your photo. Please try again later.")

    except Exception as e:
        await update.message.reply_text("An error occurred while processing your photo.")
        print(f"Error in handle_photo: {e}")
