from flask import Flask
from config import Config   # * Es para poder crea run archivo de configuración para datos importantes del sistema



from werkzeug.security import generate_password_hash, check_password_hash
import csv
from io import StringIO
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy   # * Es para la conexión con la BD
from flask_login import LoginManager   # * Es para menjar las sesiónes de usuarios


# TODO __init__.py principal de la app, es donde creamos y configuramos la APP de flask


# ? Definimos una función que es donde iran todos los brueprint del sistio
def create_app():
    # * Creamos una variable para instanciar Flask
    app = Flask(__name__)

    # ^ Configuración desde config.py
    app.config.from_object(Config)


    # ? Importamos los Blueprints de cada módulo
    from modules.admin import bp_admistracion
    from modules.client import bp_clientes
    from modules.production import bp_production
    from modules.ventas import bp_ventas
    from modules.shared import bp_shared

    # ? Registramos los bluebrints de cada módulo importado
    app.register_blueprint(bp_admistracion, url_prefix='/admin')
    app.register_blueprint(bp_clientes, url_prefix='/cliente')
    app.register_blueprint(bp_production, url_prefix='/production')
    app.register_blueprint(bp_ventas, url_prefix='/ventas')
    app.register_blueprint(bp_shared, url_prefix='/shared')


    # * Ejecutamos la app
    return app



    # * Ahora los utilizamos
