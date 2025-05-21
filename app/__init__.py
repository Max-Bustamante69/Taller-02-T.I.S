from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from urllib.parse import urlparse

# Conditional loading of .env file
from dotenv import load_dotenv

def reload_env():
    """Force reload environment variables from .env file"""
    load_dotenv(override=True)

if not os.environ.get('SECRET_KEY') or not os.environ.get('DATABASE_URL'):
    reload_env()

# Initialize SQLAlchemy here so it can be imported by models
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Set secret key explicitly - REQUIRED for CSRF protection
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-pokeneas')
    
    # Configure SQLAlchemy with PostgreSQL or fallback to SQLite
    if os.environ.get('DATABASE_URL'):
        # Parse the DATABASE_URL from Neon
        postgres_url = urlparse(os.environ.get('DATABASE_URL'))
        # Format for standard SQLAlchemy (not async) with SSL required
        app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{postgres_url.username}:{postgres_url.password}@{postgres_url.hostname}{postgres_url.path}?sslmode=require"
    else:
        # Fallback to SQLite for development
        print('Failed to load DATABASE_URL, using SQLite instead')
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pokeneas.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Connection pooling for better performance with multiple containers
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_pre_ping': True,  # Verify connections before use
    }
    
    # Initialize extensions
    db.init_app(app)
    
    # Import and register blueprint after db initialization
    from app.routes import main
    app.register_blueprint(main)
    
    # Create database tables and initialize data within application context
    with app.app_context():
        db.create_all()

    
    return app