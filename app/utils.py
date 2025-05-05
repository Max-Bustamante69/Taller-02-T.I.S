import os
#get env variables
from dotenv import load_dotenv
import boto3
from botocore import UNSIGNED # Import UNSIGNED
from botocore.client import Config # Import Config
import requests
from urllib.parse import urlparse # Import urlparse
import socket  # Add this to get the hostname/container ID

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


def upload_aws_image_url(image_url, image_name):
    """
    Sube una imagen a un bucket S3 de AWS y devuelve la URL pública.
    Usando el bucket name y la región de AWS desde las variables de entorno.
    """
    
    s3 = boto3.client(
        's3',
        region_name=os.getenv("AWS_REGION"),
        config=Config(signature_version=UNSIGNED), # Use Config with UNSIGNED
    )
    
    #download the image from the url
    response = requests.get(image_url)
    if response.status_code != 200:
        raise Exception(f"Error downloading image: {response.status_code}")
    #save the image to a file
    with open(image_name, 'wb') as f:
        f.write(response.content)
    #upload the image to s3
    s3.upload_file(image_name, os.getenv("AWS_BUCKET"), image_name, ExtraArgs={'ACL': 'public-read'})
    
    #delete the image from the local file system
    os.remove(image_name)
    
    return get_aws_image_url(image_name)

def get_container_id():
    """
    Get the Docker container ID of the current container.
    Returns the hostname which is set by Docker to the container ID by default.
    """
    try:
        return socket.gethostname()
    except:
        return "unknown-container"
