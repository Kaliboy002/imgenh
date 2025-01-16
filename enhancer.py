import requests
import json
from io import BytesIO

# API endpoint for enhancing photos
ENHANCER_API = "https://for-free.serv00.net/K/img_enhancer.php?url="

# Function to enhance the photo
def enhance_photo(photo_url: str) -> BytesIO:
    """
    Send the photo URL to the API, download the enhanced photo,
    and return it as a BytesIO object.
    """
    try:
        # Send the photo to the enhancement API
        response = requests.get(ENHANCER_API + photo_url)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "success":
            enhanced_url = data.get("image")

            # Store the enhanced URL in a JSON file for later
            with open("enhanced_photos.json", "a") as file:
                json.dump({"photo_url": photo_url, "enhanced_url": enhanced_url}, file)
                file.write("\n")  # Add new line after each entry

            # Download the enhanced photo
            enhanced_response = requests.get(enhanced_url)
            enhanced_response.raise_for_status()

            # Save the image to a BytesIO object
            image_data = BytesIO(enhanced_response.content)
            image_data.name = "enhanced_photo.jpg"  # Set a filename for the image
            return image_data
        return None
    except Exception as e:
        print(f"Error enhancing photo: {e}")
        return None
