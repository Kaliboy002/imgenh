from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from pymongo import MongoClient
import json

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
        collection = db.get_collection('users')  # Replace 'users' with your collection name

        # Fetch all data from the collection
        documents = list(collection.find())

        # Check if there are any documents in the collection
        if not documents:
            await update.message.reply_text("No data found in the database.")
            return

        # Convert documents to JSON
        data_json = json.dumps(documents, default=str)

        # Send the data as a JSON file
        with open("data.json", "w") as json_file:
            json.dump(documents, json_file)

        # Send the file to the user
        await update.message.reply_document(document=open("data.json", "rb"), filename="data.json")

        # Alternatively, send as text file
        with open("data.txt", "w") as txt_file:
            for doc in documents:
                txt_file.write(f"{doc}\n")

        await update.message.reply_document(document=open("data.txt", "rb"), filename="data.txt")
    
    except Exception as e:
        # Handle errors if MongoDB connection fails
        await update.message.reply_text(f"Error connecting to MongoDB: {str(e)}")

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
