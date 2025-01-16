import os
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# API endpoint
ENHANCER_API = "https://for-free.serv00.net/C/img_enhancer.php?url="

def start(update: Update, context: CallbackContext):
    """Send a welcome message when the bot starts."""
    update.message.reply_text(
        "Welcome! Send me a photo, and I'll enhance it for you."
    )

def enhance_photo(photo_url: str) -> str:
    """
    Send the photo URL to the API and return the enhanced photo URL.
    """
    try:
        response = requests.get(ENHANCER_API + photo_url)
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "success":
            return data.get("image")
        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def handle_photo(update: Update, context: CallbackContext):
    """Handle photos sent by the user."""
    message = update.message
    photo = message.photo[-1]  # Get the highest resolution photo
    file = context.bot.get_file(photo.file_id)
    file_url = file.file_path  # Get the direct URL to the photo

    update.message.reply_text("Enhancing your photo, please wait...")
    
    # Enhance photo using the API
    enhanced_url = enhance_photo(file_url)
    if enhanced_url:
        update.message.reply_photo(enhanced_url, caption="Here is your enhanced photo!")
    else:
        update.message.reply_text("Sorry, I couldn't enhance the photo. Please try again.")

def handle_file(update: Update, context: CallbackContext):
    """Handle photo files sent by the user."""
    message = update.message
    file = message.document
    if not file.mime_type.startswith("image/"):
        update.message.reply_text("Please send an image file!")
        return

    file_obj = context.bot.get_file(file.file_id)
    file_url = file_obj.file_path  # Get the direct URL to the file

    update.message.reply_text("Enhancing your photo, please wait...")
    
    # Enhance photo using the API
    enhanced_url = enhance_photo(file_url)
    if enhanced_url:
        update.message.reply_photo(enhanced_url, caption="Here is your enhanced photo!")
    else:
        update.message.reply_text("Sorry, I couldn't enhance the photo. Please try again.")

def main():
    # Create the Updater and pass it your bot's token
    TOKEN = "7542750844:AAHy_rrWqETDZEqQJ5HVWlaKsEADCcfF3UE"
    updater = Updater(TOKEN)

    # Register handlers
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))
    dp.add_handler(MessageHandler(Filters.document, handle_file))

    # Start the bot
    updater.start_polling()
    print("Bot is running...")
    updater.idle()

if __name__ == "__main__":
    main()
