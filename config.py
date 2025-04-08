

import os
from dotenv import load_dotenv

load_dotenv()  # Carga las variables del archivo .env
print("Usuario de MySQL en Flask:", os.getenv("USUARIO_MYSQL"))  # 🕵️‍♂️ Verifica qué está cargando Flask

class Config:
    # ? Clave de seguridad para evitar ataques CSRF
    # ? La usamos para encriptar y validar la sesión del usuario.
    SECRET_KEY = os.getenv('SECRET_KEY', 'clave-secreta')
    
    # Configuración de la conexión a la BD de MySQL
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('USUARIO_MYSQL')}:"  # Usuario de la BD
        f"{os.getenv('CONTRASENA_MYSQL')}@"              # Contraseña de la BD
        f"{os.getenv('MI_SERVIDOR')}/"                  # Servidor de la BD
        f"{os.getenv('NOMBRE_BD')}"                     # Nombre de la BD
    )

    print("Servidor:", os.getenv("MI_SERVIDOR"))
    print("Usuario:", os.getenv("USUARIO_MYSQL"))
    print("Contraseña:", os.getenv("CONTRASENA_MYSQL"))
    print("Base de datos:", os.getenv("NOMBRE_BD"))


    # Configuraciones adicionales de SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Muestra las consultas SQL (útil para depuración)

    # Modo de depuración
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

    
    # # ? Activa el modo depuración
    # DEBUG = True
    


    # # ? Opcional: Carpeta de subidas
    # UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/uploads')


    # # ? 
    # # UPLOAD_FOLDER = 'static/uploads'  # ? Carpeta para archivos subidos


