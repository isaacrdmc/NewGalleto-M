# models.py
from database.conexion import db
from hashlib import sha256
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    __tablename__ = 'usuarios'

    idUser = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    fechaRegistro = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    ultimoAcceso = db.Column(db.TIMESTAMP)
    intentosFallidos = db.Column(db.Integer, default=0)
    bloqueoTemporal = db.Column(db.DateTime, nullable=True)  # Nuevo campo para bloqueo temporal
    estado = db.Column(db.Enum('Activo', 'Bloqueado', 'Inactivo'), default='Activo')
    idRol = db.Column(db.Integer, db.ForeignKey('roles.idRol'), nullable=False)
    
    rol = db.relationship('Rol', backref='usuarios')

    def get_id(self):
        return str(self.idUser)

    def set_password(self, password):
        """Genera un hash SHA-256 de la contraseña"""
        self.contrasena = sha256(password.encode('utf-8')).hexdigest()

    def check_password(self, password):
        """Compara el hash SHA-256 de la contraseña ingresada con el almacenado"""
        return self.contrasena == sha256(password.encode('utf-8')).hexdigest()
    
    def esta_bloqueado_temporalmente(self):
        """Verifica si el usuario está en bloqueo temporal"""
        return self.bloqueoTemporal and self.bloqueoTemporal > datetime.now()

    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        return {
            'id': self.idUser,
            'username': self.username,
            'fecha_registro': self.fechaRegistro.strftime('%Y-%m-%d %H:%M:%S') if self.fechaRegistro else None,
            'ultimo_acceso': self.ultimoAcceso.strftime('%Y-%m-%d %H:%M:%S') if self.ultimoAcceso else None,
            'intentos_fallidos': self.intentosFallidos,
            'estado': self.estado,
            'id_rol': self.idRol,
            'rol_nombre': self.rol.nombre if self.rol else None
        }

class Rol(db.Model):
    __tablename__ = 'roles'
    
    idRol = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombreRol = db.Column(db.Enum('Administrador', 'Produccion', 'Ventas', 'Cliente'), nullable=False)
    descripcion = db.Column(db.String(100))
    fechaCreacion = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())