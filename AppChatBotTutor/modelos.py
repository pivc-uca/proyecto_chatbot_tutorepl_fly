# modelos.py
from basedatos import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class Usuarios(UserMixin, db.Model):
    # ¡Importante! Mapea el modelo a la tabla existente 'usuarios'
    __tablename__ = 'usuarios'

    id_usu = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(50), nullable=False)
    apellidos = db.Column(db.String(50), nullable=False)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    clave = db.Column(db.String(20), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default='estudiante') # 'estudiante' o 'profesor'

    def set_password(self, clave):
        self.clave = generate_password_hash(clave)

    def check_password(self, clave):
        return check_password_hash(self.clave, clave)
        
    def get_id(self):
        return str(self.id_usu)        

    def __repr__(self):
        return f'<User {self.usuario}>'
        
class Historial(db.Model):
    # Nombre de la tabla explícito si es diferente a 'historial'
    # __tablename__ = 'historial' 
    id_his = db.Column(db.Integer, primary_key=True)
    # Define la ForeignKey que enlaza con el ID del usuario
    # Apunta a 'usuarios.id_usu' porque tu tabla User se llama 'usuarios'
    id_usu = db.Column(db.Integer, db.ForeignKey('usuarios.id_usu'), nullable=False) 
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False) # Campo fecha "YYYY-MM-DD HH:MM:SS". Añadido nullable=False para consistencia.
    actividad = db.Column(db.String(200), nullable=False)
    # fecha = db.Column(db.String(19), nullable=False) # fecha "YYYY-MM-DD HH:MM:SS"

    def __repr__(self):
        return f'<Historial {self.id_his} por Usuario {self.id_usu}>'