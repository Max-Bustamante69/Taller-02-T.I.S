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


def validate_image_url(image_url):
    """
    Validates that the URL points to an image and checks its content type.
    
    :param image_url: URL of the image to validate
    :return: tuple of (content_type, possible_extension)
    :raises: Exception with descriptive message if validation fails
    """
    valid_image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'svg', 'webp', 'bmp', 'ico']
    
    try:
        head_response = requests.head(image_url, allow_redirects=True, timeout=10)
    except requests.exceptions.MissingSchema:
        raise Exception("URL inválida: Debe incluir http:// o https://")
    except requests.exceptions.ConnectionError:
        raise Exception("No se pudo conectar al servidor de la imagen. Verifique la URL o intente más tarde.")
    except requests.exceptions.Timeout:
        raise Exception("Tiempo de espera agotado al intentar acceder a la URL. Intente con otra imagen.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error al acceder a la URL: {str(e)}")
        
    content_type = head_response.headers.get('content-type', '')
    
    # Check if content type is an image with specific messages
    if not content_type:
        raise Exception("No se pudo determinar el tipo de contenido. Verifique que la URL sea accesible.")
    elif content_type == 'application/octet-stream':
        raise Exception("El servidor no especifica que el archivo es una imagen. Intente con otra URL.")
    elif content_type.startswith('text/html'):
        raise Exception("La URL apunta a una página web HTML, no a una imagen. Proporcione la URL directa de la imagen.")
    elif content_type.startswith('application/'):
        raise Exception(f"El archivo es de tipo {content_type} (posiblemente un documento o archivo comprimido), no una imagen.")
    elif content_type.startswith('video/'):
        raise Exception("El archivo es un video, no una imagen. Solo se permiten imágenes.")
    elif content_type.startswith('audio/'):
        raise Exception("El archivo es un audio, no una imagen. Solo se permiten imágenes.")
    elif not content_type.startswith('image/'):
        raise Exception(f"El contenido no es una imagen. Tipo detectado: {content_type}")

    # Get file extension from content type
    possible_ext = content_type.split('/')[-1].lower()
    
    # Initial validation of image format
    if possible_ext not in valid_image_extensions and possible_ext != 'jpeg':
        if possible_ext in ['tiff', 'tif']:
            raise Exception("Los archivos TIFF no son compatibles con la mayoría de navegadores. Use JPG, PNG o GIF.")
        elif possible_ext == 'psd':
            raise Exception("Los archivos de Photoshop (PSD) no son imágenes web. Exporte como JPG o PNG.")
        elif possible_ext == 'raw':
            raise Exception("Los formatos RAW de cámara no son compatibles con navegadores web. Convierta a JPG o PNG.")
        else:
            raise Exception(f"Formato de imagen no compatible: {possible_ext}. Formatos permitidos: {', '.join(valid_image_extensions)}")
    
    return content_type, possible_ext

def download_image(image_url, temp_file):
    """
    Downloads an image from URL to a temporary file.
    
    :param image_url: URL of the image to download
    :param temp_file: Path where to save the downloaded file
    :raises: Exception if download fails
    """
    response = requests.get(image_url)
    if response.status_code != 200:
        raise Exception(f"Error al descargar la imagen: código {response.status_code}")
    
    # Save the image to a temporary file
    with open(temp_file, 'wb') as f:
        f.write(response.content)
    
    return response

def validate_image_format(temp_file, possible_ext):
    """
    Validates that the downloaded file is a valid web image format.
    
    :param temp_file: Path to the temporary image file
    :param possible_ext: Possible extension from content type
    :return: Valid file extension
    :raises: Exception if format is invalid
    """
    valid_image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'svg', 'webp', 'bmp', 'ico']
    
    # Check file format using imghdr
    import imghdr
    file_ext = imghdr.what(temp_file)
    
    if not file_ext:
        # Fallback to content type if imghdr fails
        file_ext = possible_ext
    
    # Final validation of extension
    if not file_ext:
        raise Exception("No se pudo determinar el formato de la imagen descargada. Verifique que sea una imagen válida.")
    elif file_ext.lower() not in valid_image_extensions:
        if file_ext == 'jpeg':
            file_ext = 'jpg'  # Normalize jpeg to jpg
        elif file_ext == 'xbm':
            raise Exception("El formato XBM es obsoleto y no compatible con la mayoría de navegadores.")
        elif file_ext == 'tiff':
            raise Exception("El formato TIFF no es compatible con navegadores web. Use JPG, PNG o GIF.")
        else:
            raise Exception(f"Formato no válido para web: {file_ext}. Use: {', '.join(valid_image_extensions)}")
    
    return file_ext

def prepare_image_file(temp_file, base_name, file_ext):
    """
    Prepares the image file with proper name for uploading.
    
    :param temp_file: Path to the temporary file
    :param base_name: Base name for the file
    :param file_ext: File extension
    :return: Final filename
    """
    # Create final filename
    final_filename = f"{base_name.lower().replace(' ', '_')}.{file_ext}"
    
    # Rename the temp file to the final filename
    os.rename(temp_file, final_filename)
    
    return final_filename

def upload_to_s3(file_path, bucket_name, region_name):
    """
    Uploads a file to S3 bucket.
    
    :param file_path: Path to the file to upload
    :param bucket_name: S3 bucket name
    :param region_name: AWS region
    :return: Public URL of the uploaded file
    """
    s3 = boto3.client(
        's3',
        region_name=region_name,
        config=Config(signature_version=UNSIGNED),
    )
    
    # Upload the file to S3
    s3.upload_file(
        file_path, 
        bucket_name, 
        file_path,  # Use the same name in S3
        ExtraArgs={'ACL': 'public-read'}
    )
    
    return get_aws_image_url(file_path)

def cleanup_files(*file_paths):
    """
    Cleans up temporary files.
    
    :param file_paths: Paths to files that need to be cleaned up
    """
    for file_path in file_paths:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Warning: Could not remove file {file_path}: {e}")

def upload_aws_image_url(image_url, base_name):
    """
    Sube una imagen a un bucket S3 de AWS y devuelve la URL pública.
    Usando el bucket name y la región de AWS desde las variables de entorno.
    
    :param image_url: URL de la imagen a descargar
    :param base_name: Nombre base para el archivo (sin extensión)
    :return: URL pública de la imagen en S3
    :raises: Exception with custom messages for different validation issues
    """
    temp_file = "temp_download"
    final_filename = None
    
    try:
        # Step 1: Validate URL and check content type
        _, possible_ext = validate_image_url(image_url)
        
        # Step 2: Download the image
        download_image(image_url, temp_file)
        
        # Step 3: Validate image format
        file_ext = validate_image_format(temp_file, possible_ext)
        
        # Step 4: Prepare image file
        final_filename = prepare_image_file(temp_file, base_name, file_ext)
        
        # Step 5: Upload to S3
        aws_url = upload_to_s3(
            final_filename, 
            os.getenv("AWS_BUCKET"), 
            os.getenv("AWS_REGION")
        )
        
        return aws_url
        
    except Exception as e:
        # Re-raise the exception to be handled by the caller
        raise e
    
    finally:
        # Step 6: Clean up temporary files
        cleanup_files(temp_file, final_filename)

def get_container_id():
    """
    Get the Docker container ID of the current container.
    Returns the hostname which is set by Docker to the container ID by default.
    """
    try:
        return socket.gethostname()
    except:
        return "unknown-container"
