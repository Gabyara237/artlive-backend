import os
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

cloudinary.config(
    cloud_name=os.getenv('CLOUD_NAME'),
    api_key=os.getenv('API_KEY'),
    api_secret=os.getenv('API_SECRET'),
    secure=True
)

def upload_image(file):
    result = cloudinary.uploader.upload(file)
    return result["secure_url"]