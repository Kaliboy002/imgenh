import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
import requests

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define states for conversation
PROMPT = 1
CREATE = 2

# Define API URL
API_URL = "https://for-free.serv00.net/A/aiimage.php"

# Start command handler
async def start(update: Update, context):
    await update.message.reply_text('Welcome! Please enter a prompt to generate an image:')
    return PROMPT

# Handle prompt input
async def prompt_input(update: Update, context):
    user_prompt = update.message.text
    context.user_data['prompt'] = user_prompt

    # Create inline button for the user to generate the image
    keyboard = [
        [InlineKeyboardButton("Create", callback_data='create_image')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f'Your prompt: {user_prompt}\nClick "Create" to generate the image.', reply_markup=reply_markup)
    return CREATE

# Handle "Create" button click
async def create_image(update: Update, context):
    query = update.callback_query
    await query.answer()

    # Get the prompt from user_data
    prompt = context.user_data.get('prompt')

    # Make API request
    response = requests.get(API_URL, params={'prompt': prompt, 'image': 3})
    data = response.json()

    # Handle image responses
    if data.get('images'):
        for image in data['images']:
            image_url = image['image']
            await query.message.reply_text(f"Generated Image:\n{image_url}")
    else:
        await query.message.reply_text("Error generating the image. Please try again later.")

    return ConversationHandler.END

# Cancel command handler
async def cancel(update: Update, context):
    await update.message.reply_text('Conversation canceled.')
    return ConversationHandler.END

# Main function to run the bot
def main():
    # Set up the Application with your bot's token
    application = Application.builder().token('7542750844:AAH3oKXtFK7NT2BAkmkOX_cifSIu9lHdDQk').build()

    # Set up conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PROMPT: [MessageHandler(filters.TEXT & ~filters.COMMAND, prompt_input)],
            CREATE: [CallbackQueryHandler(create_image, pattern='^create_image$')],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
