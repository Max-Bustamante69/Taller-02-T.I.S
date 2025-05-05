from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Conditional loading of .env file
from dotenv import load_dotenv
if not os.environ.get('SECRET_KEY'):
    load_dotenv()


# Initialize SQLAlchemy here so it can be imported by models
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Set secret key explicitly - REQUIRED for CSRF protection
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-pokeneas')
    
    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pokeneas.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    
    # Import and register blueprint after db initialization
    from app.routes import main
    app.register_blueprint(main)
    
    # Create database tables and initialize data within application context
    with app.app_context():
        from app.models import init_db
        db.create_all()
        init_db()
    
    return app
