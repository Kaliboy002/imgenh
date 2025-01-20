import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Function to handle incoming messages
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Welcome! Please provide the bot token, MongoDB link, or a file containing user IDs."
    )

# Function to handle receiving the bot token
async def handle_token(update: Update, context: CallbackContext) -> None:
    bot_token = update.message.text.strip()

    if bot_token:  # Validate token
        await update.message.reply_text("Bot token received successfully! Now send the user IDs file (txt/json) or list.")
        context.user_data["bot_token"] = bot_token  # Save token for later use
    else:
        await update.message.reply_text("Please send a valid bot token.")

# Function to handle receiving files (text or JSON)
async def handle_file(update: Update, context: CallbackContext) -> None:
    bot_token = context.user_data.get("bot_token")

    if not bot_token:
        await update.message.reply_text("You must provide the bot token first.")
        return

    file = update.message.document
    file_name = file.file_name

    # Download the file
    new_file = await file.get_file()
    file_path = f"/tmp/{file_name}"
    await new_file.download_to_drive(file_path)

    # Read the file based on its extension
    try:
        user_ids = []
        if file_name.endswith(".txt"):
            with open(file_path, "r") as f:
                user_ids = [line.strip() for line in f.readlines() if line.strip()]
        elif file_name.endswith(".json"):
            with open(file_path, "r") as f:
                data = json.load(f)
                # Assuming the user IDs are stored in an array under the key 'user_ids'
                user_ids = data.get('user_ids', [])
        else:
            await update.message.reply_text("Unsupported file type. Please upload a .txt or .json file.")
            return

        await update.message.reply_text(f"File processed successfully. Found {len(user_ids)} user IDs.")
        context.user_data["user_ids"] = user_ids
    except Exception as e:
        await update.message.reply_text(f"Error reading file: {str(e)}")

# Function to handle broadcasting messages
async def handle_broadcast(update: Update, context: CallbackContext) -> None:
    bot_token = context.user_data.get("bot_token")
    user_ids = context.user_data.get("user_ids")

    if not bot_token:
        await update.message.reply_text("You must provide the bot token first.")
        return
    if not user_ids:
        await update.message.reply_text("You must provide the user IDs first.")
        return

    # Broadcast the message to all user IDs
    broadcast_message = update.message.text.split("\n", 1)[1].strip()  # Text after the command

    for user_id in user_ids:
        try:
            # Send the message to each user
            await context.bot.send_message(user_id, broadcast_message)
            print(f"Message sent to {user_id}")
        except Exception as e:
            print(f"Failed to send message to {user_id}: {str(e)}")

    await update.message.reply_text(f"Broadcast message sent to {len(user_ids)} users.")

# Function to handle the bot's main behavior
async def main() -> None:
    application = Application.builder().token("7817420437:AAEBdeljD8u1LkoxcD7TKYZQh58F-TkywXo").build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set_token", handle_token))  # Get token
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))  # Handle files (txt/json)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_broadcast))  # Handle broadcasting text

    # Start the bot
    await application.run_polling()

if __name__ == '__main__':
    main()
