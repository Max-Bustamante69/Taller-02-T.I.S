from flask import Blueprint, jsonify, render_template, redirect, url_for
from app.models import get_random_pokenea, get_pokenea, get_all_pokeneas, Pokenea
# Import the new function
from app.utils import get_aws_image_url, upload_aws_image_url, get_file_extension_from_url, get_container_id
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
        # Extract image extension and create image name
        image_url = form.url_imagen.data
        try:
            # Use the utility function to get the file extension
            file_extension = get_file_extension_from_url(image_url) 
            if not file_extension:  # Check if extension was found
                raise ValueError("Invalid image URL or missing extension")
            image_name = f"{form.nombre.data.lower().replace(' ', '_')}{file_extension}"
        except ValueError as e: # Catch the specific error
            print(f"Error processing image URL: {e}")
            return render_template('create_pokenea.html', form=form, error=str(e))
        except Exception as e: # Catch other potential errors
            print(f"Unexpected error processing image URL: {e}")
            return render_template('create_pokenea.html', form=form, error="An unexpected error occurred.")

        # Create a new Pokenea with the generated image name
        new_pokenea = Pokenea(
            nombre=form.nombre.data,
            altura=form.altura.data,
            habilidad=form.habilidad.data,
            imagen=image_name,  # Use the generated image name
            frase=form.frase.data
        )
        
        try:
            # Add to database
            db.session.add(new_pokenea)
            db.session.commit()
            # Upload image to AWS using the generated name
            upload_aws_image_url(image_url, image_name)  # Pass image_name
            
            # Redirect to the new Pokenea's page
            return redirect(url_for('main.show_pokenea_by_id', pokenea_id=new_pokenea.id))
        
        except Exception as e:
            db.session.rollback()
            print(f"Error al guardar el Pokenea o subir imagen: {e}")
            
            #Delete the Entry for the new Pokenea if it was created but not committed, check if the pokenea exists in the session
            if new_pokenea in db.session:
                db.session.delete(new_pokenea)
                db.session.commit()
                
            # More specific error message might be helpful depending on the exception
            error_message = "Error al guardar el Pokenea. Asegúrate de que el nombre sea único y la URL de la imagen sea válida."
            return render_template('create_pokenea.html', form=form, error=error_message)
    
    # GET request or form validation failed
    return render_template('create_pokenea.html', form=form)

@main.app_errorhandler(404)
def page_not_found(e):
    """Handles 404 errors by rendering the custom 404 template."""
    return render_template('404.html'), 404



