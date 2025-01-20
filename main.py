import json
import os
from pymongo import MongoClient
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Global variable to store the bot and MongoDB info
user_data = {}

# Function to start the bot
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Welcome to the Broadcast Bot! Please enter the bot token first to proceed."
    )

# Function to handle the bot token and save it
async def handle_bot_token(update: Update, context: CallbackContext) -> None:
    bot_token = update.message.text.strip()
    user_data['bot_token'] = bot_token  # Store the token
    await update.message.reply_text("Bot token saved successfully! Now, please provide your MongoDB link or send a file with user IDs.")

# Function to handle MongoDB URI or file input
async def handle_mongo_or_file(update: Update, context: CallbackContext) -> None:
    if 'bot_token' not in user_data:
        await update.message.reply_text("Please enter the bot token first.")
        return

    if update.message.text.startswith("mongodb+srv") or update.message.text.startswith("mongodb://"):
        # User provided MongoDB link
        user_data['mongo_uri'] = update.message.text.strip()
        await update.message.reply_text("MongoDB link saved. Now, send the message or file you want to broadcast.")
    elif update.message.document:
        # User sent a file (text or JSON with user IDs)
        file = await update.message.document.get_file()
        user_data['user_ids_file'] = file.file_id  # Store the file
        await update.message.reply_text("File saved. Now, send the message or file to broadcast.")
    elif update.message.text:
        # User sent user IDs as text
        user_data['user_ids'] = update.message.text.strip().split(",")  # Parse the comma-separated user IDs
        await update.message.reply_text("User IDs received. Now, send the message or file to broadcast.")

# Function to handle the broadcast message
async def handle_broadcast(update: Update, context: CallbackContext) -> None:
    if 'bot_token' not in user_data:
        await update.message.reply_text("Please enter the bot token first.")
        return
    
    if 'mongo_uri' not in user_data and 'user_ids' not in user_data and 'user_ids_file' not in user_data:
        await update.message.reply_text("Please provide a MongoDB link, file, or user IDs to proceed.")
        return
    
    if 'message' in user_data:
        message = user_data['message']
        await send_broadcast(update, context, message)
    elif update.message.text:
        # User sent a broadcast message
        user_data['message'] = update.message.text.strip()
        await update.message.reply_text(f"Message received: '{user_data['message']}'. Now, I'll send it to all users.")
        await send_broadcast(update, context, user_data['message'])

# Function to send broadcast
async def send_broadcast(update: Update, context: CallbackContext, message: str) -> None:
    bot_token = user_data['bot_token']
    chat_ids = await get_user_ids()

    for chat_id in chat_ids:
        try:
            # Send the message to each user
            await context.bot.send_message(chat_id, message)
        except Exception as e:
            print(f"Error sending message to {chat_id}: {e}")
    
    await update.message.reply_text("Broadcast completed.")

# Function to fetch user IDs from MongoDB or file
async def get_user_ids() -> list:
    chat_ids = []
    
    if 'mongo_uri' in user_data:
        # Connect to MongoDB and fetch user IDs from a collection
        client = MongoClient(user_data['mongo_uri'])
        db = client.get_database()
        collection = db['users']  # You can modify the collection name if necessary
        users = collection.find()  # Retrieve all users
        chat_ids = [str(user['_id']) for user in users]  # Assuming the user ID is stored in '_id'
    
    elif 'user_ids' in user_data:
        # User IDs provided as text (comma-separated)
        chat_ids = user_data['user_ids']
    
    elif 'user_ids_file' in user_data:
        # User sent a file with user IDs
        file = await context.bot.get_file(user_data['user_ids_file'])
        file.download("user_ids.txt")
        with open("user_ids.txt", "r") as f:
            chat_ids = f.read().strip().split("\n")  # Read user IDs from the file (one per line)
    
    return chat_ids

# Function to handle when a user sends a file with user IDs
async def handle_file(update: Update, context: CallbackContext) -> None:
    if 'bot_token' not in user_data:
        await update.message.reply_text("Please enter the bot token first.")
        return
    
    # Save the file and process it
    if update.message.document:
        file = await update.message.document.get_file()
        user_data['user_ids_file'] = file.file_id  # Save the file
        await update.message.reply_text("File with user IDs saved. Now send the message or file to broadcast.")

# Main function to run the bot
def main():
    application = Application.builder().token("7817420437:AAEBdeljD8u1LkoxcD7TKYZQh58F-TkywXo").build()

    # Command handler for the /start command
    application.add_handler(CommandHandler("start", start))

    # Handler for bot token
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_bot_token))

    # Handler for MongoDB link or file input
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_mongo_or_file))

    # Handler for broadcast messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_broadcast))

    # Handler for file upload
    application.add_handler(MessageHandler(filters.Document, handle_file))

    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()
