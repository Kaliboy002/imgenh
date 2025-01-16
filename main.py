import requests
import json
from io import BytesIO
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio

# API endpoint for enhancing photo
ENHANCER_API = "https://for-free.serv00.net/K/img_enhancer.php?url="

# Path to store temporary JSON file
JSON_FILE_PATH = "photo_urls.json"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the bot starts."""
    await update.message.reply_text("Welcome! Send me a photo, and I'll enhance it for you.")

# Function to read the stored URLs from the JSON file
def read_json_file():
    try:
        with open(JSON_FILE_PATH, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Function to save URLs to the JSON file
def save_json_file(data):
    with open(JSON_FILE_PATH, 'w') as file:
        json.dump(data, file)

async def enhance_photo(photo_url: str) -> BytesIO:
    """Enhance the photo using the external API."""
    try:
        # Send the photo to the enhancement API
        response = requests.get(ENHANCER_API + photo_url)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "success":
            enhanced_url = data.get("image")

            # Download the enhanced photo
            enhanced_response = requests.get(enhanced_url)
            enhanced_response.raise_for_status()

            # Save the image to a BytesIO object
            image_data = BytesIO(enhanced_response.content)
            image_data.name = "enhanced_photo.jpg"  # Set a filename for the image
            return image_data
        return None
    except Exception as e:
        print(f"Error enhancing photo: {e}")
        return None

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photos sent by the user."""
    photo = update.message.photo[-1]  # Get the highest resolution photo
    file = await context.bot.get_file(photo.file_id)
    file_url = file.file_path  # Get the direct URL to the photo

    # Read stored photo URLs from the JSON file
    stored_urls = read_json_file()

    # Store the current URL if not already stored
    if file_url not in stored_urls:
        stored_urls[file_url] = "pending"
        save_json_file(stored_urls)

    await update.message.reply_text("Enhancing your photo, please wait...")

    # Enhance photo using the API
    enhanced_image = await enhance_photo(file_url)
    if enhanced_image:
        # Update status and save the enhanced image
        stored_urls[file_url] = "completed"
        save_json_file(stored_urls)

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

    # Read stored photo URLs from the JSON file
    stored_urls = read_json_file()

    # Store the current URL if not already stored
    if file_url not in stored_urls:
        stored_urls[file_url] = "pending"
        save_json_file(stored_urls)

    await update.message.reply_text("Enhancing your photo, please wait...")

    # Enhance photo using the API
    enhanced_image = await enhance_photo(file_url)
    if enhanced_image:
        # Update status and save the enhanced image
        stored_urls[file_url] = "completed"
        save_json_file(stored_urls)

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
