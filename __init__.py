# __init__.py principal de la app
from flask import Flask, redirect, render_template, url_for
from config import Config
from database.conexion import db
from flask_login import LoginManager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # * Inicializar la base de datos
    db.init_app(app)








    # ^ Configurar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'shared.login'

    # ? Importar modelos después de crear la app para evitar importaciones circulares
    from modules.shared.models import User

    # ? Configurar el cargador de usuarios
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


    # ^ Configuración de las rutas de error
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('shared/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('shared/500.html'), 500



    # ^ Configuración de los logs
    from modules.logs.log_config import configure_logging
    configure_logging(app) # Activamos el logger




    # ^ Importar blueprints
    from modules.admin import bp_admistracion
    from modules.client import bp_clientes
    from modules.production import bp_production
    from modules.ventas import bp_ventas
    from modules.shared import bp_shared

    #  *Registrar blueprints
    app.register_blueprint(bp_admistracion, url_prefix='/admin')
    app.register_blueprint(bp_clientes, url_prefix='/cliente')
    app.register_blueprint(bp_production, url_prefix='/production')
    app.register_blueprint(bp_ventas, url_prefix='/ventas')
    app.register_blueprint(bp_shared, url_prefix='/shared')


    # ~ Configurar ruta principal
    @app.route('/')
    def index():
        return redirect(url_for('shared.login'))    
    
    # @app.before_first_request
    # def show_routes():
    #     print("=== Rutas registradas ===")
    #     for rule in app.url_map.iter_rules():
    #         print(f"{rule.endpoint}: {rule.methods} -> {rule}")
    #     print("========================")


    # * Ejecución de la APP
    return app