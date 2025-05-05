import os
#get env variables

import boto3
from botocore import UNSIGNED # Import UNSIGNED
from botocore.client import Config # Import Config
import requests
from urllib.parse import urlparse # Import urlparse
import socket  # Add this to get the hostname/container ID

from dotenv import load_dotenv
if not (os.environ.get('AWS_BUCKET') and os.environ.get('AWS_REGION')):
    load_dotenv()


def get_file_extension_from_url(url):
    """
    Extracts the file extension from a URL.
    
    :param url: The URL string.
    :return: The file extension (including the dot), or None if not found.
    """
    try:
        parsed_url = urlparse(url)
        path = parsed_url.path
        _, extension = os.path.splitext(path)
        return extension if extension else None
    except Exception as e:
        print(f"Error parsing URL or extracting extension: {e}")
        return None

def get_aws_image_url(image_name):
    """
    Genera la URL pública de una imagen almacenada en un bucket S3 de AWS.
    
    :param image_name: Nombre de la imagen (incluyendo la extensión).
    :param bucket_name: Nombre del bucket S3.
    :param aws_region: Región donde se encuentra el bucket.
    :return: URL pública de la imagen.
    """
    return f"https://{os.getenv('AWS_BUCKET')}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{image_name}"


def upload_aws_image_url(image_url, base_name):
    """
    Sube una imagen a un bucket S3 de AWS y devuelve la URL pública.
    Usando el bucket name y la región de AWS desde las variables de entorno.
    
    :param image_url: URL de la imagen a descargar
    :param base_name: Nombre base para el archivo (sin extensión)
    :return: URL pública de la imagen en S3
    :raises: Exception if the image format is not valid for HTML display
    """
    
    s3 = boto3.client(
        's3',
        region_name=os.getenv("AWS_REGION"),
        config=Config(signature_version=UNSIGNED),
    )
    
    temp_file = "temp_download"
    final_filename = None
    
    # Valid image extensions for HTML img tags
    valid_image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'svg', 'webp', 'bmp', 'ico']
    
    try:
        # Download the image from the URL
        response = requests.get(image_url)
        if response.status_code != 200:
            raise Exception(f"Error downloading image: {response.status_code}")
        
        # Save the image to a temporary file
        with open(temp_file, 'wb') as f:
            f.write(response.content)
        
        # Determine file extension from the downloaded file
        import imghdr
        file_ext = imghdr.what(temp_file)
        
        if not file_ext:
            # Fallback to basic extension detection
            if response.headers.get('content-type', '').startswith('image/'):
                file_ext = response.headers.get('content-type', '').split('/')[-1]
            else:
                file_ext = None
        
        # Check if extension is valid for HTML img tag
        if not file_ext or file_ext.lower() not in valid_image_extensions:
            raise Exception(f"Invalid or unsupported image format: {file_ext}. Supported formats: {', '.join(valid_image_extensions)}")
        
        # Create final filename
        final_filename = f"{base_name.lower().replace(' ', '_')}.{file_ext}"
        
        # Rename the temp file to the final filename
        os.rename(temp_file, final_filename)
        
        # Upload the image to S3
        s3.upload_file(final_filename, os.getenv("AWS_BUCKET"), final_filename, 
                      ExtraArgs={'ACL': 'public-read'})
        
        return get_aws_image_url(final_filename)
    
    except Exception as e:
        raise e
    
    finally:
        # Clean up files regardless of success or failure
        if os.path.exists(temp_file):
            os.remove(temp_file)
        if final_filename and os.path.exists(final_filename):
            os.remove(final_filename)

def get_container_id():
    """
    Get the Docker container ID of the current container.
    Returns the hostname which is set by Docker to the container ID by default.
    """
    try:
        return socket.gethostname()
    except:
        return "unknown-container"
