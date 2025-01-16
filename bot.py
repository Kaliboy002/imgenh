import requests
import time

# Telegram Bot Token
BOT_TOKEN = "7542750844:AAHy_rrWqETDZEqQJ5HVWlaKsEADCcfF3UE"  # Replace with your bot token
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# Picsart API Configurations
PICSART_API_URL = "https://ai.picsart.com/gw1/enhancement/v0319/pipeline"
BEARER_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ijk3MjFiZTM2LWIyNzAtNDlkNS05NzU2LTlkNTk3Yzg2YjA1MSJ9.eyJzdWIiOiJhdXRoLXNlcnZpY2Utd2ViIiwiYXVkIjoiYXV0aC1zZXJ2aWNlLXdlYiIsIm5iZiI6MTY4NzQyOTgyOCwic2NvcGUiOltdLCJpYXQiOjE2ODc0NDA2MjgsImlzcyI6Imh0dHBzOi8vcGEtYXV0aG9yaXphdGlvbi1zZXJ2ZXIuc3RhZ2UucGljc2FydC50b29scy9hcGkvb2F1dGgyIiwianRpIjoiYjRkYzU1MzAtYzEzOC00MzBmLWFiNjUtYTMyNDZlYmMwNWU3In0.UpUJB5QBuQKekvSWcBiA_lH0YdB6wKGXu2VscIK3hNYfzCDvvu-jKF7hnVgbX-REE1fAO3CY68eKBthJU1cC48UqLmQHQk8imPIUdPfARRXnH_6y2Qc7FgP3-Go2hLPwTxPXcTX0_AvAt6nviLPnvbfhKrqB6bCp6W4nmVWakrE-PLCJtZ-KuCa5-b6MIsRz_tqNeDXP-TLZhjjdfjIk0hrqr86WIQOH2MsrwLibSpJyKBhNDh314T7fsV4pHx3uQj_NhchsDBATf6vF0x74VjHO1Y6r5XSi6zgBEm-zfdqPOVitC-J-nnQNlOwAEmgFL_Ho49mkgWKjFKmXvm4bFw"  # Replace with your Picsart Bearer token


def get_file_url(file_id):
    """Retrieve the file URL from Telegram using the file_id."""
    response = requests.get(f"{TELEGRAM_API_URL}getFile", params={"file_id": file_id})
    if response.status_code == 200:
        file_path = response.json().get("result", {}).get("file_path")
        if file_path:
            return f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    return None


def get_transaction_id(photo_url):
    """Send the photo URL to Picsart API to get a transaction ID."""
    url_with_params = f"{PICSART_API_URL}?picsart_cdn_url={photo_url}&format=PNG&model=REALESERGAN"
    headers = {
        "Content-Type": "application/json",
        "x-touchpoint-referrer": "/ai-image-enhancer/",
        "x-touchpoint": "widget_EnhancedImage",
        "x-app-authorization": f"Bearer {BEARER_TOKEN}",
        "Origin": "https://picsart.com",
        "Accept": "application/json",
    }

    response = requests.post(url_with_params, headers=headers, json={})
    if response.status_code == 200:
        return response.json().get("transaction_id")
    return None


def get_enhanced_photo(transaction_id):
    """Retrieve the enhanced photo URL using the transaction ID."""
    headers = {
        "x-app-authorization": f"Bearer {BEARER_TOKEN}",
        "Accept": "application/json",
    }

    for _ in range(3):  # Retry logic
        response = requests.get(f"{PICSART_API_URL}/{transaction_id}", headers=headers)
        if response.status_code == 200:
            tmp_url = response.json().get("results", {}).get("tmp_url")
            if tmp_url:
                return tmp_url
        time.sleep(5)  # Wait before retrying

    return None


def send_message(chat_id, text):
    """Send a message to a Telegram chat."""
    requests.post(f"{TELEGRAM_API_URL}sendMessage", json={"chat_id": chat_id, "text": text})


def send_photo(chat_id, photo_url, caption=""):
    """Send a photo to a Telegram chat."""
    requests.post(f"{TELEGRAM_API_URL}sendPhoto", json={"chat_id": chat_id, "photo": photo_url, "caption": caption})


def process_update(update):
    """Process incoming Telegram updates."""
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]

        # Handle photos sent by the user
        if "photo" in message:
            file_id = message["photo"][-1]["file_id"]  # Get the highest resolution photo
            file_url = get_file_url(file_id)

            if file_url:
                send_message(chat_id, "Processing your photo. Please wait...")

                # Step 1: Get the transaction ID
                transaction_id = get_transaction_id(file_url)

                if transaction_id:
                    # Step 2: Get the enhanced photo URL
                    enhanced_photo_url = get_enhanced_photo(transaction_id)

                    if enhanced_photo_url:
                        send_photo(chat_id, enhanced_photo_url, "Here is your enhanced photo!")
                    else:
                        send_message(chat_id, "Sorry, I couldn't enhance your photo. Please try again later.")
                else:
                    send_message(chat_id, "Failed to process your photo. Please try again.")
            else:
                send_message(chat_id, "Couldn't fetch your photo. Please try again.")
        else:
            send_message(chat_id, "Please send a valid photo.")


def main():
    """Main function to handle Telegram bot updates."""
    offset = None

    while True:
        # Fetch updates from Telegram
        params = {"timeout": 100, "offset": offset}
        response = requests.get(f"{TELEGRAM_API_URL}getUpdates", params=params)

        if response.status_code == 200:
            updates = response.json().get("result", [])

            for update in updates:
                process_update(update)
                offset = update["update_id"] + 1
        else:
            print(f"Error fetching updates: {response.status_code}")
            time.sleep(5)  # Wait before retrying in case of errors


if __name__ == "__main__":
    main()
