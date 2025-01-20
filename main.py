import logging
import json
import re
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from pymongo import MongoClient
from bson import ObjectId

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Utility function to extract IDs (7 to 15 digits) from text and JSON files
def extract_ids_from_text(content):
    # Extract IDs that are 7 to 15 digits long from text or mixed content
    return re.findall(r'\b\d{7,15}\b', content)

# Function to connect to MongoDB and fetch IDs
def fetch_ids_from_mongo(db_link):
    ids = []
    try:
        client = MongoClient(db_link)
        db = client.get_database()
        users_collection = db.get_collection("users")  # Assuming the collection is named 'users'
        users = users_collection.find({}, {"_id": 1})  # Fetch only the user IDs
        ids = [str(user["_id"]) for user in users if isinstance(user["_id"], ObjectId)]
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
    return ids

# Handler for the /start command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Please send the bot token.")

# Handler for receiving the bot token and asking for MongoDB or file input
async def handle_bot_token(update: Update, context: CallbackContext):
    bot_token = update.message.text.strip()
    context.user_data['bot_token'] = bot_token
    await update.message.reply_text("Please send your MongoDB link, a file with IDs (TXT/JSON), or the user IDs directly.")

# Handler for MongoDB link or file input
async def handle_ids_or_db_link(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    if text.startswith("mongodb+srv://"):
        context.user_data['db_link'] = text
        await update.message.reply_text("MongoDB link received. Please send the message or file to broadcast.")
    elif text.endswith('.txt') or text.endswith('.json'):
        # Handle files
        await update.message.reply_text("Please send me the file with user IDs.")
    else:
        # Handle user IDs directly from the message
        ids = extract_ids_from_text(text)
        context.user_data['user_ids'] = ids
        await update.message.reply_text(f"User IDs extracted: {', '.join(ids)}. Please send the message or file to broadcast.")

# Handler to process files and extract IDs
async def handle_file(update: Update, context: CallbackContext):
    file = await update.message.document.get_file()
    file_content = await file.download_as_bytearray()

    if file.file_name.endswith('.txt'):
        content = file_content.decode('utf-8')
        ids = extract_ids_from_text(content)
        context.user_data['user_ids'] = ids
    elif file.file_name.endswith('.json'):
        content = json.loads(file_content.decode('utf-8'))
        ids = [str(item['id']) for item in content if 'id' in item]
        context.user_data['user_ids'] = ids

    await update.message.reply_text(f"User IDs extracted: {', '.join(ids)}. Please send the message or file to broadcast.")

# Handler for receiving the broadcast message
async def handle_broadcast_message(update: Update, context: CallbackContext):
    if 'user_ids' in context.user_data:
        message = update.message.text.strip()
        bot_token = context.user_data.get('bot_token')
        user_ids = context.user_data['user_ids']

        # Send message to all user IDs
        for user_id in user_ids:
            try:
                await context.bot.send_message(user_id, message)
            except Exception as e:
                logger.error(f"Error sending message to {user_id}: {e}")

        await update.message.reply_text("Message broadcasted successfully.")
    else:
        await update.message.reply_text("No user IDs found. Please provide user IDs.")

# Main function to run the bot
async def main():
    bot_token = '7817420437:AAEBdeljD8u1LkoxcD7TKYZQh58F-TkywXo'  # Replace with your bot token
    application = Application.builder().token(bot_token).build()

    # Add command and message handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_bot_token))
    application.add_handler(MessageHandler(filters.TEXT, handle_ids_or_db_link))
    application.add_handler(MessageHandler(filters.DOCUMENT, handle_file))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_broadcast_message))

    # Run the bot
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
