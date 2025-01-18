import aiohttp
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import logging
import asyncio

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your Telegram bot token
BOT_TOKEN = '7328870287:AAFwBWlNMBVtyU1bhw2QmSkmWLz0e9kAa8M'
USER_DATA_FILE = 'user_data.json'

# Function to read the user data from the JSON file
def load_user_data():
    try:
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Function to save the user data to the JSON file
def save_user_data(data):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

# Function to start the bot
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Welcome! Please provide a prompt for the image generation.")

# Function to handle the image prompt
async def handle_message(update: Update, context: CallbackContext) -> None:
    prompt = update.message.text
    user_id = update.message.from_user.id
    amount = 3  # The number of images to generate

    # Load current user data from JSON
    user_data = load_user_data()

    # If the user already has an active prompt, inform them
    if user_id in user_data and user_data[user_id]['status'] == 'processing':
        await update.message.reply_text("Your request is already being processed. Please wait.")
        return

    # Mark the user's status as processing
    user_data[user_id] = {
        'status': 'processing',
        'prompt': prompt,
        'amount': amount
    }
    save_user_data(user_data)  # Save data to JSON

    await update.message.reply_text("Processing your image generation request...")

    # API URL
    api_url = f"https://for-free.serv00.net/A/aiimage.php?prompt={prompt}&image={amount}"

    try:
        # Using aiohttp to make an async HTTP request
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                # Wait for the API response
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"API response: {data}")

                    # Check if images are returned
                    if 'images' in data:
                        images = data['images']
                        for image in images:
                            await update.message.reply_photo(image['image'])

                        # Optionally, add a join message from the API
                        join_message = data.get('join', 'No join message found.')
                        await update.message.reply_text(join_message)

                        # Update user status to 'completed'
                        user_data[user_id]['status'] = 'completed'
                    else:
                        await update.message.reply_text("Sorry, no images were generated for the given prompt.")
                        user_data[user_id]['status'] = 'failed'
                else:
                    logger.error(f"API request failed with status {response.status}")
                    await update.message.reply_text("There was an error while fetching the images. Please try again later.")
                    user_data[user_id]['status'] = 'failed'

    except Exception as e:
        logger.error(f"Error during API request: {e}")
        await update.message.reply_text("An error occurred while processing your request. Please try again later.")
        user_data[user_id]['status'] = 'failed'

    # Save updated user data to JSON
    save_user_data(user_data)

# Set up the application and dispatcher
def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
