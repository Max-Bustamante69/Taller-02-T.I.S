from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, SubmitField, URLField
from wtforms.validators import DataRequired, Length, NumberRange

class PokeneaForm(FlaskForm):
    nombre = StringField('Nombre', validators=[
        DataRequired(message="Nombre es requerido"),
        Length(min=3, max=50, message="El nombre debe tener entre 3 y 50 caracteres")
    ])
    
    altura = FloatField('Altura (m)', validators=[
        DataRequired(message="Altura es requerida"), 
        NumberRange(min=0.1, max=3.0, message="La altura debe estar entre 0.1 y 3.0 metros")
    ])
    
    habilidad = StringField('Habilidad', validators=[
        DataRequired(message="Habilidad es requerida"),
        Length(min=3, max=100, message="La habilidad debe tener entre 3 y 100 caracteres")
    ])
    
    url_imagen = URLField('URL de imagen', validators=[
        DataRequired(message="URL de imagen es requerida"),
        Length(min=10, max=200, message="La URL de imagen debe tener entre 10 y 200 caracteres")
    ])
    
    
    frase = TextAreaField('Frase filosófica', validators=[
        DataRequired(message="Frase filosófica es requerida"),
        Length(min=10, max=500, message="La frase debe tener entre 10 y 500 caracteres")
    ])
    
    submit = SubmitField('Crear Pokenea')
