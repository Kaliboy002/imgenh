import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Replace with your Telegram bot token
BOT_TOKEN = '7328870287:AAFwBWlNMBVtyU1bhw2QmSkmWLz0e9kAa8M'

# Function to start the bot
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Welcome! Please provide a prompt for the image generation.")

# Function to handle the image prompt
async def handle_message(update: Update, context: CallbackContext) -> None:
    prompt = update.message.text
    amount = 3  # The number of images to generate

    # API URL
    api_url = f"https://for-free.serv00.net/A/aiimage.php?prompt={prompt}&image={amount}"

    # Using aiohttp to make an async HTTP request
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            # Wait for the API response
            data = await response.json()

    # Check if images are returned
    if 'images' in data:
        images = data['images']
        for image in images:
            await update.message.reply_photo(image['image'])

        # Optionally, add a join message from the API
        join_message = data.get('join', 'No join message found.')
        await update.message.reply_text(join_message)
    else:
        await update.message.reply_text("Sorry, no images were generated for the given prompt.")

# Set up the application and dispatcher
def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
