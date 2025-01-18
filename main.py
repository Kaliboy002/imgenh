import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Replace with your Telegram bot token
BOT_TOKEN = '7328870287:AAFwBWlNMBVtyU1bhw2QmSkmWLz0e9kAa8M'

# Function to start the bot
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Welcome! Please provide a prompt for the image generation.")

# Function to handle the image prompt
def handle_message(update: Update, context: CallbackContext) -> None:
    prompt = update.message.text
    amount = 3  # The number of images to generate

    # API URL
    api_url = f"https://for-free.serv00.net/A/aiimage.php?prompt={prompt}&image={amount}"

    # Get the response from the API
    response = requests.get(api_url)
    data = response.json()

    # Check if images are returned
    if 'images' in data:
        images = data['images']
        for image in images:
            update.message.reply_photo(image['image'])

        # Optionally, add a join message from the API
        join_message = data.get('join', 'No join message found.')
        update.message.reply_text(join_message)
    else:
        update.message.reply_text("Sorry, no images were generated for the given prompt.")

# Set up the updater and dispatcher
def main() -> None:
    updater = Updater(BOT_TOKEN)

    dispatcher = updater.dispatcher

    # Handlers
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
