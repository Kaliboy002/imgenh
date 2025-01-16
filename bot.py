import requests
from io import BytesIO
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pymongo import MongoClient
from gridfs import GridFS

# MongoDB Configuration
MONGO_URI = "mongodb+srv://mrshokrullah:L7yjtsOjHzGBhaSR@cluster0.aqxyz.mongodb.net/shah?retryWrites=true&w=majority&appName=Cluster0"  # Replace with your MongoDB URI
DB_NAME = "shah"
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
fs = GridFS(db)  # GridFS for handling large files

# API endpoint
ENHANCER_API = "https://for-free.serv00.net/C/img_enhancer.php?url="

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the bot starts."""
    await update.message.reply_text(
        "Welcome! Send me a photo, and I'll enhance it for you."
    )

async def enhance_photo(photo_url: str) -> BytesIO:
    """
    Enhance the photo by sending it to the API, download the enhanced photo,
    and return it as a BytesIO object.
    """
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
            image_data.name = "enhanced_photo.jpg"
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

    await update.message.reply_text("Enhancing your photo, please wait...")

    # Enhance photo using the API
    enhanced_image = await enhance_photo(file_url)
    if enhanced_image:
        # Store the enhanced image in MongoDB
        image_id = fs.put(enhanced_image.getvalue(), filename=enhanced_image.name)

        # Retrieve the image back from MongoDB and send it to the user
        stored_image = fs.get(image_id)
        await update.message.reply_photo(BytesIO(stored_image.read()), caption="Here is your enhanced photo!")

        # Delete the image from MongoDB after sending
        fs.delete(image_id)
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
    enhanced_image = await enhance_photo(file_url)
    if enhanced_image:
        # Store the enhanced image in MongoDB
        image_id = fs.put(enhanced_image.getvalue(), filename=enhanced_image.name)

        # Retrieve the image back from MongoDB and send it to the user
        stored_image = fs.get(image_id)
        await update.message.reply_photo(BytesIO(stored_image.read()), caption="Here is your enhanced photo!")

        # Delete the image from MongoDB after sending
        fs.delete(image_id)
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
