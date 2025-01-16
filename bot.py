import asyncio
from io import BytesIO
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import aiohttp
from pymongo import MongoClient
from gridfs import GridFS

# MongoDB Configuration
MONGO_URI = "mongodb+srv://mrshokrullah:L7yjtsOjHzGBhaSR@cluster0.aqxyz.mongodb.net/shah?retryWrites=true&w=majority&appName=Cluster0"  # Replace with your MongoDB URI
DB_NAME = "shah"
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
fs = GridFS(db)

# API endpoint
ENHANCER_API = "https://for-free.serv00.net/C/img_enhancer.php?url="

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the bot starts."""
    await update.message.reply_text("Welcome! Send me a photo, and I'll enhance it for you.")

async def enhance_photo(photo_url: str) -> BytesIO:
    """
    Enhance the photo by sending it to the API, download the enhanced photo,
    and return it as a BytesIO object.
    """
    try:
        # Call the enhancement API asynchronously
        async with aiohttp.ClientSession() as session:
            async with session.get(ENHANCER_API + photo_url, timeout=15) as response:
                if response.status != 200:
                    raise Exception(f"Failed to call API: {response.status}")
                data = await response.json()
        
        if data.get("status") == "success":
            enhanced_url = data.get("image")
            
            # Download the enhanced image asynchronously
            async with aiohttp.ClientSession() as session:
                async with session.get(enhanced_url, timeout=15) as enhanced_response:
                    if enhanced_response.status != 200:
                        raise Exception(f"Failed to download enhanced image: {enhanced_response.status}")
                    content = await enhanced_response.read()
            
            # Save to BytesIO
            image_data = BytesIO(content)
            image_data.name = "enhanced_photo.jpg"
            return image_data
        else:
            raise Exception("Enhancement API failed.")
    except Exception as e:
        print(f"Error enhancing photo: {e}")
        return None

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photos sent by the user."""
    try:
        await update.message.reply_text("Enhancing your photo, please wait...")

        # Get the highest resolution photo
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        file_url = file.file_path

        # Enhance the photo
        enhanced_image = await enhance_photo(file_url)
        if enhanced_image:
            # Store the enhanced image in MongoDB
            image_id = fs.put(enhanced_image.getvalue(), filename=enhanced_image.name)

            # Retrieve and send the enhanced photo
            stored_image = fs.get(image_id)
            await update.message.reply_photo(BytesIO(stored_image.read()), caption="Here is your enhanced photo!")

            # Clean up from MongoDB
            fs.delete(image_id)
        else:
            await update.message.reply_text("Sorry, I couldn't enhance the photo. Please try again later.")
    except Exception as e:
        print(f"Error handling photo: {e}")
        await update.message.reply_text("An error occurred. Please try again later.")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo files sent by the user."""
    try:
        file = update.message.document
        if not file.mime_type.startswith("image/"):
            await update.message.reply_text("Please send a valid image file!")
            return

        await update.message.reply_text("Enhancing your photo, please wait...")
        file_obj = await context.bot.get_file(file.file_id)
        file_url = file_obj.file_path

        # Enhance the photo
        enhanced_image = await enhance_photo(file_url)
        if enhanced_image:
            # Store the enhanced image in MongoDB
            image_id = fs.put(enhanced_image.getvalue(), filename=enhanced_image.name)

            # Retrieve and send the enhanced photo
            stored_image = fs.get(image_id)
            await update.message.reply_photo(BytesIO(stored_image.read()), caption="Here is your enhanced photo!")

            # Clean up from MongoDB
            fs.delete(image_id)
        else:
            await update.message.reply_text("Sorry, I couldn't enhance the photo. Please try again later.")
    except Exception as e:
        print(f"Error handling file: {e}")
        await update.message.reply_text("An error occurred. Please try again later.")

def main():
    """Run the bot."""
    TOKEN = "7542750844:AAHy_rrWqETDZEqQJ5HVWlaKsEADCcfF3UE"  # Replace with your bot token
    application = Application.builder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    # Start the bot
    application.run_polling()
    print("Bot is running...")

if __name__ == "__main__":
    main()
