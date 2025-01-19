from flask import Flask, request, jsonify
from rembg import remove
from PIL import Image
import io
import os
import requests
from uuid import uuid4

app = Flask(__name__)

# Directory to save processed images
OUTPUT_DIR = "processed_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# API route for background removal
@app.route('/remove-background', methods=['GET'])
def remove_background():
    image_url = request.args.get('url')

    if not image_url:
        return jsonify({"error": "No image URL provided"}), 400

    try:
        # Download the image from the URL
        response = requests.get(image_url)
        if response.status_code != 200:
            return jsonify({"error": "Failed to download image"}), 400

        input_image = Image.open(io.BytesIO(response.content))

        # Remove the background
        output_image = remove(input_image)

        # Save the processed image with a unique filename
        unique_filename = f"{uuid4().hex}.png"
        output_path = os.path.join(OUTPUT_DIR, unique_filename)
        output_image.save(output_path, format="PNG")

        # Generate the public URL for the processed image
        public_url = f"{request.host_url}{OUTPUT_DIR}/{unique_filename}"

        return jsonify({"status": "success", "processed_image_url": public_url}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Serve processed images
@app.route(f'/{OUTPUT_DIR}/<filename>', methods=['GET'])
def serve_processed_image(filename):
    return send_from_directory(OUTPUT_DIR, filename)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
