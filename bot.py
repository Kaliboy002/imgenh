import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# Replace with your actual bot token
BOT_TOKEN = "7542750844:AAHy_rrWqETDZEqQJ5HVWlaKsEADCcfF3UE"

# Function to start the bot
async def start(update: Update, context):
    await update.message.reply_text("Send me a photo!")

# Function to handle received photo
async def handle_photo(update: Update, context):
    try:
        # Get the photo file from the user's message
        photo = update.message.photo[-1]  # Get the highest quality photo
        file = await context.bot.get_file(photo.file_id)
        file_path = file.file_path

        # Step 1: Send photo to the image enhancement API
        enhancer_url = f"https://for-free.serv00.net/C/img_enhancer.php?url={file_path}"
        response = requests.get(enhancer_url)
        response_data = response.json()

        if response_data["status"] == "success":
            # Step 2: Extract the enhanced image URL from the API response
            enhanced_image_url = response_data["image"]

            # Step 3: Send the enhanced image back to the user
            await update.message.reply_photo(enhanced_image_url)
        else:
            await update.message.reply_text("Failed to process the image. Please try again.")

    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")

# Main function to run the bot
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Adding handlers to the bot
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Run the bot using long polling
    app.run_polling()

if __name__ == "__main__":
    main()
