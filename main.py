# bot.py
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN

# External API for photo enhancement
ENHANCER_API_URL = "https://for-free.serv00.net/K/img_enhancer.php?url="

# Function to enhance photo using the external API
def enhance_photo(image_url: str) -> str:
    """Enhance the photo using the external API."""
    response = requests.get(f"{ENHANCER_API_URL}{image_url}")
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "success":
            return data["image"]
    return None

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the user starts the bot."""
    await update.message.reply_text("Welcome! Send me a photo to enhance it.")

# Handle photo and enhance it
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle photo messages, enhance them, and send back the enhanced photo."""
    photo = update.message.photo[-1]  # Get the highest resolution photo
    file = await photo.get_file()
    file_url = file.file_path  # Get the URL of the photo

    # Enhance the photo using the external API
    enhanced_url = enhance_photo(file_url)
    
    if enhanced_url:
        await update.message.reply_text(f"Here's your enhanced photo: {enhanced_url}")
    else:
        await update.message.reply_text("Sorry, something went wrong while enhancing your photo.")

# Main function to start the bot
def main():
    """Start the bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Start the bot
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
