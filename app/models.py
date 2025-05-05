import random
from app import db

class Pokenea(db.Model):
    __tablename__ = 'pokeneas'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    altura = db.Column(db.Float, nullable=False)
    habilidad = db.Column(db.String(100), nullable=False)
    imagen = db.Column(db.String(100), nullable=False)
    frase = db.Column(db.Text, nullable=False)
    
    def to_json(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'altura': self.altura,
            'habilidad': self.habilidad
        }
    
    def __str__(self):
        return f"{self.nombre} (ID: {self.id}) - Altura: {self.altura}m - Habilidad: {self.habilidad}"

# Initial data that will be used to populate the database
initial_pokeneas = [
    {"nombre": "Paisitico", "altura": 1.70, "habilidad": "Amabilidad extrema", "imagen": "paisitico.jpg", 
     "frase": "¿Entonces qué pues, mijo? La vida es como una arepa: mejor con quesito."},
    {"nombre": "Arreperro", "altura": 1.65, "habilidad": "Ladrido paisa", "imagen": "arreperro.png", 
     "frase": "¡Parce, eso está muy bueno! El mejor amigo del hombre es quien le da una oportunidad."},
    {"nombre": "Guapetón", "altura": 1.80, "habilidad": "Conquista instantánea", "imagen": "guapeton.png", 
     "frase": "Tranquilo, que yo me encargo. La belleza está en el ojo del que mira y en el corazón de quien actúa."},
    {"nombre": "Montañero", "altura": 1.75, "habilidad": "Resistencia a la altura", "imagen": "montanero.png", 
     "frase": "En la vida hay que escalar como en las montañas: paso a paso pero sin detenerse."},
    {"nombre": "Carrieloso", "altura": 1.60, "habilidad": "Almacenamiento infinito", "imagen": "carrieloso.png", 
     "frase": "En mi carriel llevo la vida entera. No son las cosas que guardas, sino los recuerdos que atesoras."},
    {"nombre": "Aguardientoso", "altura": 1.68, "habilidad": "Resistencia al licor", "imagen": "aguardientoso.png", 
     "frase": "¡Un guaro más y seguimos! La vida es cuestión de encontrar el balance entre lo dulce y lo amargo."},
    {"nombre": "Bandejudo", "altura": 1.90, "habilidad": "Alimentación poderosa", "imagen": "bandejudo.png", 
     "frase": "La bandeja paisa es el secreto de mi fuerza. La abundancia está en compartir lo que tenemos."}
]

def init_db():
    """Initialize the database with the default pokeneas if they don't exist"""
    # Only populate if the table is empty
    if Pokenea.query.count() == 0:
        for pokenea_data in initial_pokeneas:
            pokenea = Pokenea(**pokenea_data)
            db.session.add(pokenea)
        db.session.commit()

def get_random_pokenea():
    """Get a random pokenea from the database"""
    count = Pokenea.query.count()
    if count == 0:
        return None
    random_offset = random.randint(0, count - 1)
    return Pokenea.query.offset(random_offset).first()

def get_pokenea(pokenea_id):
    """Get a pokenea by ID"""
    return Pokenea.query.get(pokenea_id)

def get_all_pokeneas():
    """Get all pokeneas from the database"""
    return Pokenea.query.all()

