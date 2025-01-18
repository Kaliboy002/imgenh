import json
import aiohttp
import logging
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters, CallbackContext

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your Telegram bot token
BOT_TOKEN = '7328870287:AAFwBWlNMBVtyU1bhw2QmSkmWLz0e9kAa8M'
WEBHOOK_URL = 'https://imgenh-production.up.railway.app/webhook'  # Replace with your domain and path

# Initialize Flask app
app = Flask(__name__)

# Initialize the bot with your token
bot = Bot(BOT_TOKEN)

# Function to handle start command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Welcome! Please provide a prompt for the image generation.")

# Function to handle messages
def handle_message(update: Update, context: CallbackContext) -> None:
    prompt = update.message.text
    user_id = update.message.from_user.id
    amount = 3  # Number of images

    # Your API logic to fetch images
    # (Make sure you replace this with your own API handling code)
    api_url = f"https://for-free.serv00.net/A/aiimage.php?prompt={prompt}&image={amount}"

    response = aiohttp.get(api_url)
    data = response.json()

    if 'images' in data:
        images = data['images']
        for image in images:
            update.message.reply_photo(image['image'])
    else:
        update.message.reply_text("No images generated.")

# Function to set up webhook
def set_webhook():
    webhook_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={WEBHOOK_URL}"
    response = requests.get(webhook_url)
    logger.info(f"Webhook setup response: {response.text}")

# Webhook route
@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = Update.de_json(json.loads(json_str), bot)

    # Use Dispatcher to handle the update
    dispatcher = Dispatcher(bot, None, workers=0)
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    dispatcher.process_update(update)

    return 'ok', 200

if __name__ == '__main__':
    # Set up the webhook on your server
    set_webhook()

    # Run the Flask app
    app.run(host='0.0.0.0', port=5000)
