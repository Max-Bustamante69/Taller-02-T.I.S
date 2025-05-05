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

