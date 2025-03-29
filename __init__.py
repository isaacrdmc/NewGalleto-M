
# TODO __init__.py principal de la app, es donde creamos y configuramos la APP de flask


from flask import Flask, redirect, url_for
from config import Config   # * Es para poder crea run archivo de configuración para datos importantes del sistema
from database.conexion import db


# ? Definimos una función que es donde iran todos los brueprint del sistio
def create_app():
    app = Flask(__name__)   # * Creamos una variable para instanciar Flask
    app.config.from_object(Config)  # ^ Configuración de la app

    # ^ Inicializmos la conexión con la BD
    db.init_app(app)


    # ? Importamos los Blueprints de cada módulo
    from modules.admin import bp_admistracion
    from modules.client import bp_clientes
    from modules.production import bp_production
    from modules.ventas import bp_ventas
    from modules.shared import bp_shared
 
    # ? Registramos los bluebrints de cada módulo importado
    app.register_blueprint(bp_admistracion, url_prefix='/admin')    # Nombre de la ruta:  admin
    app.register_blueprint(bp_clientes, url_prefix='/cliente')    # Nombre de la ruta:  cliente
    app.register_blueprint(bp_production, url_prefix='/production')    # Nombre de la ruta:  production
    app.register_blueprint(bp_ventas, url_prefix='/ventas')    # Nombre de la ruta:  ventas
    app.register_blueprint(bp_shared, url_prefix='/shared')    # Nombre de la ruta:  shared


    
    # ? Cuando la app se ejecute nos enviara a la ruta del login 
    @app.route('/')
    def index():
        return redirect(url_for('shared.login'))  # Asegúrate de que 'login' es el nombre correcto de la vista



    # * Ejecutamos la app
    return app



    # * Ahora los utilizamos
