import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

BOT_TOKEN = "7628087790:AAEzbDoI4po7MHKeNw1jg-quRxzogHCiFAo"

async def start(update: Update, context):
    await update.message.reply_text("Send me a photo!")

async def handle_photo(update: Update, context):
    # Get the photo file
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    file_path = file.file_path

    try:
        # Step 1: Send photo to the first API
        first_api_url = f"https://for-free.serv00.net/get_transaction_id.php?image={file_path}"
        first_response = requests.get(first_api_url)
        
        # Log first API response for debugging
        print("First API Response:", first_response.text)

        first_data = first_response.json()

        if first_data.get("status") == "ACCEPTED":
            transaction_id = first_data["transaction_id"]

            # Step 2: Use transaction ID in the second API
            second_api_url = f"https://for-free.serv00.net/final_result_by_transaction_id.php?id={transaction_id}"
            second_response = requests.get(second_api_url)
            
            # Log second API response for debugging
            print("Second API Response:", second_response.text)

            second_data = second_response.json()

            if "tmp_url" in second_data:
                final_url = second_data["tmp_url"].replace("\\", "")  # Remove backslashes
                await update.message.reply_photo(final_url)
            else:
                await update.message.reply_text("Failed to retrieve the processed image.")
        else:
            await update.message.reply_text("Failed to process the image in the first API.")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    app.run_polling()

if __name__ == "__main__":
    main()
