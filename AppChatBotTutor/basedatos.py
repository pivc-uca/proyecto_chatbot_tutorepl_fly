# basedatos.py
import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """
    Inicializa la base de datos con la aplicación Flask.
    """
    # Ruta persistente en Fly.io
    db_path = "/app/instance/tutorepl.db"
    
    # Asegura que el directorio exista (crucial al usar volúmenes)
    if not os.path.exists("/app/instance"):
        os.makedirs("/app/instance")

    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    print(f"Database path: {app.config['SQLALCHEMY_DATABASE_URI']}")

def create_tables(app):
    """
    Crea las tablas de la base de datos si no existen.
    Debe llamarse dentro del contexto de la aplicación.
    """
    with app.app_context():
        db.create_all() # ¡Descomenta esta línea para que cree las tablas!
    print("Tablas de la base de datos creadas/verificadas.")           
    