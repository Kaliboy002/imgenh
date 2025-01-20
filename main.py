import asyncio
import re
import json
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from pymongo import MongoClient
from telegram.error import TelegramError


# Function to get MongoDB client
def get_mongo_client(uri):
    try:
        client = MongoClient(uri)
        return client
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None


# Function to check if a string can be an ID
def is_valid_user_id(text):
    # Using regex to extract valid user IDs from the message text (numbers only between 7 to 15 digits)
    user_ids = re.findall(r'\b\d{7,15}\b', text)
    return user_ids


# Function to send message to all user IDs
async def send_message_to_users(bot, user_ids, message_text):
    for user_id in user_ids:
        try:
            await bot.send_message(user_id, message_text, parse_mode=ParseMode.HTML)
            print(f"Message sent to {user_id}")
        except TelegramError as e:
            print(f"Error sending message to {user_id}: {e}")


# Function to handle /start command
async def start(update: Update, context: CallbackContext):
    await update.message.reply("Welcome to the Broadcast Bot! Please provide your bot token.")


# Function to handle bot token input
async def get_bot_token(update: Update, context: CallbackContext):
    bot_token = update.message.text.strip()
    context.user_data['bot_token'] = bot_token
    await update.message.reply("Got the bot token! Now, please provide your MongoDB URI.")


# Function to handle MongoDB URI input
async def get_mongo_uri(update: Update, context: CallbackContext):
    mongo_uri = update.message.text.strip()
    context.user_data['mongo_uri'] = mongo_uri
    await update.message.reply("MongoDB URI received! Now, please send the message or file you want to broadcast.")


# Function to handle user IDs (from file, text, or MongoDB)
async def handle_user_ids(update: Update, context: CallbackContext):
    user_data = context.user_data
    bot_token = user_data.get('bot_token')
    mongo_uri = user_data.get('mongo_uri')

    if not bot_token or not mongo_uri:
        await update.message.reply("Please provide both the bot token and MongoDB URI first.")
        return

    message_text = update.message.text.strip()

    # Extracting user IDs from the message (either direct IDs in text or uploaded file)
    user_ids = is_valid_user_id(message_text)

    if user_ids:
        # If user IDs are extracted directly from the message text
        await send_message_to_users(update.message.bot, user_ids, message_text)
        await update.message.reply("Message broadcasted to user IDs in the text.")
    else:
        # If no user IDs found in the message, check if there's a file
        if update.message.document:
            file = await update.message.document.get_file()
            file_path = f"downloads/{file.file_id}.txt"
            await file.download(file_path)

            # Read user IDs from the downloaded file
            with open(file_path, 'r') as f:
                content = f.read()
                user_ids = is_valid_user_id(content)

            if user_ids:
                await send_message_to_users(update.message.bot, user_ids, message_text)
                await update.message.reply("Message broadcasted to user IDs in the file.")
            else:
                await update.message.reply("No valid user IDs found in the file.")
        else:
            # No user IDs in the message or file, check MongoDB
            client = get_mongo_client(mongo_uri)
            if client:
                db = client.get_database()
                collection = db.get_collection('users')  # Collection containing user IDs
                user_ids_from_db = [user['user_id'] for user in collection.find()]
                if user_ids_from_db:
                    await send_message_to_users(update.message.bot, user_ids_from_db, message_text)
                    await update.message.reply("Message broadcasted to all users from MongoDB.")
                else:
                    await update.message.reply("No user IDs found in the MongoDB collection.")
            else:
                await update.message.reply("Failed to connect to MongoDB. Please check the URI.")


# Function to handle incoming file uploads
async def handle_file(update: Update, context: CallbackContext):
    if update.message.document:
        file = await update.message.document.get_file()
        file_path = f"downloads/{file.file_id}.txt"
        await file.download(file_path)
        with open(file_path, 'r') as f:
            content = f.read()
            user_ids = is_valid_user_id(content)

        if user_ids:
            await update.message.reply(f"Found {len(user_ids)} user IDs in the uploaded file.")
            context.user_data['user_ids'] = user_ids
        else:
            await update.message.reply("No valid user IDs found in the file.")


# Function to handle the message broadcast
async def broadcast_message(update: Update, context: CallbackContext):
    user_data = context.user_data
    bot_token = user_data.get('bot_token')
    mongo_uri = user_data.get('mongo_uri')
    message_text = update.message.text.strip()

    if not bot_token or not mongo_uri:
        await update.message.reply("Please provide both the bot token and MongoDB URI first.")
        return

    if 'user_ids' in user_data:
        user_ids = user_data['user_ids']
        await send_message_to_users(update.message.bot, user_ids, message_text)
        await update.message.reply("Message broadcasted to the user IDs from the file.")
    else:
        await update.message.reply("No user IDs available. Please upload a file with IDs or provide them directly.")


# Function to handle errors in the bot
async def error(update: Update, context: CallbackContext):
    print(f"Error occurred: {context.error}")
    await update.message.reply("An error occurred while processing your request. Please try again.")


# Set up the Telegram bot
async def main():
    application = Application.builder().token("7817420437:AAEBdeljD8u1LkoxcD7TKYZQh58F-TkywXo").build()

    # Handlers for various commands and messages
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_bot_token))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_mongo_uri))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_ids))
    application.add_handler(MessageHandler(filters.Document, handle_file))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_message))

    application.add_error_handler(error)

    # Start the bot
    await application.run_polling()


if __name__ == "__main__":
    # Start the bot without using asyncio.run() to avoid conflict with the existing event loop.
    asyncio.ensure_future(main())  # This ensures the main function is run asynchronously
    asyncio.get_event_loop().run_forever()  # This keeps the event loop running
