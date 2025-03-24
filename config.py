

import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'clave-secreta')   # ? Clave de seguridad para evitar atques CSRF
    SQLALCHEMY_DATABASE_URI = 'mysql://usuario:contraseña@localhost/basedatos'  # ? Configuración de la conexión a la BD de MySQL
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # ? Evita advertencias de SQLAlchemy
    DEBUG = True  # ? Activa el modo depuración
    # UPLOAD_FOLDER = 'static/uploads'  # ? Carpeta para archivos subidos

