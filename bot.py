import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import logging
from io import BytesIO
from PIL import Image
import mimetypes

# Replace with your actual bot token
BOT_TOKEN = "7542750844:AAHy_rrWqETDZEqQJ5HVWlaKsEADCcfF3UE"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to start the bot
async def start(update: Update, context):
    await update.message.reply_text("Welcome! Send me any image, and I'll process it for you.")

# Function to validate if the file is a valid image
def is_valid_image(image_bytes):
    try:
        # Try to open the image using PIL to check if it's a valid image
        image = Image.open(BytesIO(image_bytes))
        image.verify()  # Verify the image integrity
        return True
    except Exception as e:
        logger.error(f"Invalid image: {e}")
        return False

# Function to handle received photo
async def handle_photo(update: Update, context):
    try:
        # Get the photo file from the user's message
        photo = update.message.photo[-1]  # Get the highest quality photo
        file = await context.bot.get_file(photo.file_id)

        # Log the received file info
        logger.info(f"Received photo: {file.file_path}")

        # Step 1: Download the image from Telegram
        photo_file = requests.get(file.file_path)

        if photo_file.status_code == 200:
            # Step 2: Validate the file content
            if not is_valid_image(photo_file.content):
                await update.message.reply_text("The uploaded file is not a valid image. Please send a valid image.")
                return

            # Step 3: Check if the file size is acceptable (optional, you can adjust the limit)
            if len(photo_file.content) > 10 * 1024 * 1024:  # 10 MB limit
                await update.message.reply_text("The uploaded image is too large. Please send an image smaller than 10MB.")
                return

            # Step 4: Check MIME type to ensure it's an image format (support all types of images)
            mime_type, _ = mimetypes.guess_type(file.file_path)
            if mime_type is None or not mime_type.startswith('image'):
                await update.message.reply_text("The uploaded file is not an image. Please send a valid image.")
                return

            # Step 5: Send the photo to the image enhancement API (using binary content)
            enhancer_url = "https://for-free.serv00.net/C/img_enhancer.php"
            files = {'file': ('photo', BytesIO(photo_file.content), mime_type)}

            # Send the image to the external API
            response = requests.post(enhancer_url, files=files)
            response_data = response.json()

            if response_data["status"] == "success":
                # Step 6: Extract the enhanced image URL from the API response
                enhanced_image_url = response_data["image"]

                # Step 7: Send the enhanced image back to the user
                await update.message.reply_photo(enhanced_image_url)
            else:
                # Log and notify user if the image processing failed
                logger.error(f"API processing failed: {response_data}")
                await update.message.reply_text("Failed to process the image. Please try again later.")
        else:
            # Log the download error and notify user
            logger.error(f"Failed to download image: {file.file_path} - Status Code: {photo_file.status_code}")
            await update.message.reply_text("Failed to download the image. Please try again later.")
        
    except Exception as e:
        # Log any unexpected errors and notify user
        logger.error(f"An error occurred: {str(e)}")
        await update.message.reply_text(f"An unexpected error occurred: {str(e)}")

# Main function to run the bot
def main():
    # Create the bot application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Adding handlers to the bot
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Run the bot using long polling
    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
