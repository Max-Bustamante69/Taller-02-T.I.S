from flask import Blueprint, jsonify, render_template, redirect, url_for
from app.models import get_random_pokenea, get_pokenea, get_all_pokeneas, Pokenea
# Import the new function
from app.utils import get_aws_image_url, upload_aws_image_url, get_container_id
from app.forms import PokeneaForm
from app import db
import os  # Import the os module


main = Blueprint('main', __name__)

@main.route('/', methods=['GET'])
def home():
    """Ruta principal que muestra todos los pokeneas disponibles"""
    # Generate AWS image URLs for all pokeneas
    pokeneas_with_images = []
    for pokenea in get_all_pokeneas():
        image_url = get_aws_image_url(pokenea.imagen)
        pokeneas_with_images.append({
            'pokenea': pokenea,
            'image_url': image_url
        })
    
    return render_template('home.html', pokeneas_with_images=pokeneas_with_images)

@main.route('/api/pokenea', methods=['GET'])
def get_pokenea_json():
    """Ruta que devuelve JSON con información de un Pokenea aleatorio"""
    pokenea = get_random_pokenea()
    
    if not pokenea:
        return jsonify({"error": "No hay Pokeneas disponibles"}), 404
        
    response = pokenea.to_json()
    
    # Add container ID to the JSON response
    response['container_id'] = get_container_id()
    
    return jsonify(response)

@main.route('/pokenea', methods=['GET'])
def show_pokenea():
    """Ruta que muestra la imagen y frase filosófica de un Pokenea aleatorio"""
    pokenea = get_random_pokenea()
    
    if not pokenea:
        return render_template('error.html', message="No hay Pokeneas disponibles"), 404
        
    image_url = get_aws_image_url(pokenea.imagen)
    
    # Pass the container ID to the template
    return render_template('pokenea_view.html', 
                          pokenea=pokenea, 
                          image_url=image_url,
                          container_id=get_container_id())

@main.route('/pokenea/<int:pokenea_id>', methods=['GET'])
def show_pokenea_by_id(pokenea_id):
    """Ruta que muestra la imagen y frase filosófica de un Pokenea específico"""
    pokenea = get_pokenea(pokenea_id)
    
    if not pokenea:
        return jsonify({"error": "Pokenea no encontrado"}), 404
    
    image_url = get_aws_image_url(pokenea.imagen)
    
    # Pass the container ID to the template
    return render_template('pokenea_view.html', 
                          pokenea=pokenea, 
                          image_url=image_url,
                          container_id=get_container_id())

@main.route('/your-pokenea', methods=['GET', 'POST'])
def add_pokenea():
    """Ruta para que los usuarios creen su propio Pokenea"""
    form = PokeneaForm()
    
    if form.validate_on_submit():
        # Get the image URL
        image_url = form.url_imagen.data
        # Use the form name as the base name for the image
        base_name = form.nombre.data
        
        try:
            # First validate and upload the image to AWS
            # This will raise an exception if the image is not valid
            aws_image_url = upload_aws_image_url(image_url, base_name)
            # Extract just the filename part from the S3 URL
            image_filename = aws_image_url.split('/')[-1]
            
            # Only create a Pokenea if the image is valid and was uploaded successfully
            new_pokenea = Pokenea(
                nombre=form.nombre.data,
                altura=form.altura.data,
                habilidad=form.habilidad.data,
                imagen=image_filename,
                frase=form.frase.data
            )
            
            # Add to database
            db.session.add(new_pokenea)
            db.session.commit()
            
            # Redirect to the new Pokenea's page
            return redirect(url_for('main.show_pokenea_by_id', pokenea_id=new_pokenea.id))
        
        except Exception as e:
            # No need for rollback since we haven't added anything to the DB yet
            error_message = f"Error: {str(e)}"
            print(f"Error al procesar la imagen o guardar el Pokenea: {e}")
            return render_template('create_pokenea.html', form=form, error=error_message)
    
    # GET request or form validation failed
    return render_template('create_pokenea.html', form=form)

@main.app_errorhandler(404)
def page_not_found(e):
    """Handles 404 errors by rendering the custom 404 template."""
    return render_template('404.html'), 404



