from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from pymongo import MongoClient
import json
import os
from bson import ObjectId  # Import ObjectId from bson
from telegram import InputFile

# Function to start the bot and ask for MongoDB URI
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Welcome! Please provide your MongoDB URI connection string to continue. Example:\n"
        "mongodb+srv://username:password@cluster0.mongodb.net/database?retryWrites=true&w=majority"
    )

# Function to handle the MongoDB URI provided by the user
async def handle_mongodb_uri(update: Update, context: CallbackContext) -> None:
    # Get the MongoDB URI from the user
    mongodb_uri = update.message.text.strip()

    try:
        # Try to connect to the MongoDB server using the URI
        client = MongoClient(mongodb_uri)
        db = client.get_database()  # Get the database

        # List all collections in the database
        collections = db.list_collection_names()

        # Check if there are any collections
        if not collections:
            await update.message.reply_text("No collections found in the database.")
            return

        # Fetch and send data from each collection
        for collection_name in collections:
            collection = db.get_collection(collection_name)
            documents = list(collection.find())

            if not documents:
                await update.message.reply_text(f"No data found in collection '{collection_name}'.")
                continue

            # Convert ObjectId to string for each document in the collection
            for doc in documents:
                doc['_id'] = str(doc['_id'])

            # Convert documents to JSON
            data_json = json.dumps(documents, default=str)

            # Send the collection data as a JSON file
            with open(f"{collection_name}_data.json", "w") as json_file:
                json.dump(documents, json_file)

            await update.message.reply_document(document=open(f"{collection_name}_data.json", "rb"), filename=f"{collection_name}_data.json")

        # Fetch and send files from the server
        directory_path = 'path_to_your_files_directory'  # Update with your directory path
        files = get_files_from_directory(directory_path)

        if files:
            for file_path in files:
                await update.message.reply_document(document=open(file_path, "rb"))
        else:
            await update.message.reply_text("No files found in the specified directory.")

    except Exception as e:
        # Handle errors if MongoDB connection fails
        await update.message.reply_text(f"Error connecting to MongoDB: {str(e)}")

# Function to fetch all files from a directory (including subdirectories)
def get_files_from_directory(directory_path):
    file_paths = []
    
    # Walk through the directory and subdirectories
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_paths.append(os.path.join(root, file))
    
    return file_paths

# Function to handle unknown messages
async def unknown(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Sorry, I don't understand that command.")

# Main function to run the bot
def main():
    # Replace 'YOUR_BOT_TOKEN' with your Telegram bot token
    application = Application.builder().token("7817420437:AAEBdeljD8u1LkoxcD7TKYZQh58F-TkywXo").build()

    # Command handler for the /start command
    application.add_handler(CommandHandler("start", start))

    # Message handler for MongoDB URI input
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_mongodb_uri))

    # Handler for unknown messages
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
