import requests
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from io import BytesIO
from enhancer import enhance_photo  # Import the function from enhancer.py

# Start handler function
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the bot starts."""
    await update.message.reply_text(
        "Welcome! Send me a photo, and I'll enhance it for you."
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photos sent by the user."""
    photo = update.message.photo[-1]  # Get the highest resolution photo
    file = await context.bot.get_file(photo.file_id)
    file_url = file.file_path  # Get the direct URL to the photo

    await update.message.reply_text("Enhancing your photo, please wait...")

    # Enhance photo using the API
    enhanced_image = enhance_photo(file_url)
    if enhanced_image:
        # Send the enhanced photo back to the user
        await update.message.reply_photo(enhanced_image, caption="Here is your enhanced photo!")
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
    enhanced_image = enhance_photo(file_url)
    if enhanced_image:
        # Send the enhanced photo back to the user
        await update.message.reply_photo(enhanced_image, caption="Here is your enhanced photo!")
    else:
        await update.message.reply_text("Sorry, I couldn't enhance the photo. Please try again.")

def main():
    """Run the bot."""
    TOKEN = "7619913840:AAE0YGPTYTFIJOQEivGIfd5WaJczuUdSZdg"  # Replace with your bot token
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
