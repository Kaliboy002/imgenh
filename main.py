from telegram.ext import Application, CommandHandler, MessageHandler, filters
from handlers import start, handle_photo
from config import BOT_TOKEN

def main():
    # Create bot application
    application = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Start the bot
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
