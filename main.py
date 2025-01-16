import requests
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from io import BytesIO
from PIL import Image
import os

# Replace with your actual Telegram bot token
BOT_TOKEN = "7619913840:AAE0YGPTYTFIJOQEivGIfd5WaJczuUdSZdg"
API_URL = 'https://for-free.serv00.net/K/img_enhancer.php?url='

# Start handler function
async def start(update, context):
    await update.message.reply_text("Welcome! Please send me a photo to enhance.")

# Handle photo and interact with the API
async def handle_photo(update, context):
    # Get the photo sent by the user
    photo = update.message.photo[-1]
    file = await photo.get_file()

    # Download the photo
    photo_url = file.file_url
    response = requests.get(photo_url)

    if response.status_code == 200:
        # Save the photo temporarily
        img = Image.open(BytesIO(response.content))
        temp_image_path = 'temp_image.jpg'
        img.save(temp_image_path)

        # Upload the image to the API for enhancement
        files = {'file': open(temp_image_path, 'rb')}
        api_response = requests.post(API_URL + 'url=' + photo_url, files=files)

        # Check if the API responded with success
        if api_response.status_code == 200:
            api_result = api_response.json()

            # If success, send back the enhanced image
            if api_result.get("status") == "success":
                enhanced_image_url = api_result.get("image")
                await update.message.reply_photo(enhanced_image_url)
            else:
                await update.message.reply_text("Sorry, there was an error enhancing the image.")
        else:
            await update.message.reply_text("Sorry, there was an issue with the enhancement API.")
        
        # Clean up the temporary image
        os.remove(temp_image_path)
    else:
        await update.message.reply_text("Sorry, I couldn't download your image.")

def main():
    # Create bot application
    application = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Start the bot
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
