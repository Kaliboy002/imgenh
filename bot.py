import aiohttp
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# API endpoints
TRANSACTION_API = "https://for-free.serv00.net/get_transaction_id.php?image="
ENHANCER_RESULT_API = "https://for-free.serv00.net/final_result_by_transaction_id.php?id="

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the bot starts."""
    await update.message.reply_text(
        "Welcome! Send me a photo, and I'll enhance it for you."
    )

async def get_transaction_id(photo_url: str) -> str:
    """
    Send the photo URL to the API to get the transaction ID.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{TRANSACTION_API}{photo_url}") as response:
                response.raise_for_status()
                data = await response.json()
                if data.get("status") == "ACCEPTED":
                    return data.get("transaction_id")
                print("Transaction ID not found in response.")
    except aiohttp.ClientResponseError as e:
        print(f"Client error: {e.status} - {e.message}")
    except Exception as e:
        print(f"Error getting transaction ID: {e}")
    return None

async def get_enhanced_photo_url(transaction_id: str) -> str:
    """
    Send the transaction ID to the second API and get the enhanced photo URL.
    """
    retry_count = 3
    for attempt in range(retry_count):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{ENHANCER_RESULT_API}{transaction_id}") as response:
                    response.raise_for_status()
                    data = await response.json()
                    if "tmp_url" in data:
                        return data["tmp_url"]
                    else:
                        print(f"Attempt {attempt + 1}: tmp_url not found, retrying...")
                        await asyncio.sleep(5)  # Wait before retrying
        except Exception as e:
            print(f"Error getting enhanced photo URL: {e}")
            await asyncio.sleep(5)  # Wait before retrying
    return None

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photos sent by the user."""
    photo = update.message.photo[-1]  # Get the highest resolution photo
    file = await context.bot.get_file(photo.file_id)
    file_url = f"https://api.telegram.org/file/bot{context.bot.token}/{file.file_path}"

    await update.message.reply_text("Enhancing your photo, please wait...")

    # Get transaction ID for the photo
    transaction_id = await get_transaction_id(file_url)
    if transaction_id:
        # Get the enhanced photo URL using the transaction ID
        enhanced_url = await get_enhanced_photo_url(transaction_id)
        if enhanced_url:
            # Send the enhanced photo back to the user
            await update.message.reply_photo(enhanced_url, caption="Here is your enhanced photo!")
        else:
            await update.message.reply_text("Sorry, I couldn't retrieve the enhanced photo. Please try again later.")
    else:
        await update.message.reply_text("Sorry, I couldn't process your photo. Please try again.")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo files sent by the user."""
    file = update.message.document
    if not file.mime_type.startswith("image/"):
        await update.message.reply_text("Please send a valid image file!")
        return

    file_obj = await context.bot.get_file(file.file_id)
    file_url = f"https://api.telegram.org/file/bot{context.bot.token}/{file_obj.file_path}"

    await update.message.reply_text("Enhancing your photo, please wait...")

    # Get transaction ID for the photo
    transaction_id = await get_transaction_id(file_url)
    if transaction_id:
        # Get the enhanced photo URL using the transaction ID
        enhanced_url = await get_enhanced_photo_url(transaction_id)
        if enhanced_url:
            # Send the enhanced photo back to the user
            await update.message.reply_photo(enhanced_url, caption="Here is your enhanced photo!")
        else:
            await update.message.reply_text("Sorry, I couldn't retrieve the enhanced photo. Please try again later.")
    else:
        await update.message.reply_text("Sorry, I couldn't process your photo. Please try again.")

def main():
    """Run the bot."""
    TOKEN = "7542750844:AAHy_rrWqETDZEqQJ5HVWlaKsEADCcfF3UE"  # Replace with your bot token
    application = Application.builder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    # Start polling
    application.run_polling()
    print("Bot is running...")

if __name__ == "__main__":
    main()
