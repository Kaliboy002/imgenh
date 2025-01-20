import time
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Define API URLs
apis = [
    "https://api.fast-creat.ir/gpt/chat?apikey=6070733162:7auX01wjzJ3klLf@Api_ManagerRoBot&text=",
    "https://api.fast-creat.ir/gpt/chat?apikey=7046488481:JR7XP48glkHLSf1@Api_ManagerRoBot&text=",
    "https://api.fast-creat.ir/gpt/chat?apikey=7421174870:HPiJoNcsjKMAelC@Api_ManagerRoBot&text="
]

# Initialize last used time for each API
last_used_time = [0, 0, 0]

# Function to fetch response from the selected API
def get_api_response(text, api_index):
    url = apis[api_index] + text
    response = requests.get(url)
    return response.json()

# Function to handle user message
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.message.chat_id

    # Find the next available API (round-robin approach)
    current_time = time.time()
    for i in range(len(apis)):
        if current_time - last_used_time[i] > 5:  # If 5 seconds have passed since last use
            last_used_time[i] = current_time
            api_response = get_api_response(text, i)
            message = api_response['result']['text']
            await update.message.reply_text(message)
            return

    # If all APIs have been recently used, wait and use the first one
    await asyncio.sleep(5)  # Wait for 5 seconds before using the first API again
    last_used_time[0] = time.time()
    api_response = get_api_response(text, 0)
    message = api_response['result']['text']
    await update.message.reply_text(message)

# Main function to start the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send me a message and I will respond.")

def main():
    # Replace with your actual bot token
    token = "7817420437:AAEBdeljD8u1LkoxcD7TKYZQh58F-TkywXo"
    
    # Create the application instance
    application = Application.builder().token(token).build()

    # Command and message handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
