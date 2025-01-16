import requests

def enhance_photo(photo_url):
    """Send photo URL to the enhancement API and get the enhanced photo URL."""
    try:
        response = requests.get(f"{ENHANCE_API_URL}?url={photo_url}", timeout=10)
        response_data = response.json()
        if response_data.get("status") == "success":
            return response_data.get("image")
        else:
            return None
    except Exception as e:
        print(f"Error enhancing photo: {e}")
        return None
