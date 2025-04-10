

# ? En esta parte es donde tnedremos la calse para poder registrar los logs del sistema
from datetime import datetime
from flask_login import current_user
from flask import current_app, request
import logging
from database.conexion import db
# from modules.admin.models import LogsSistema
from .models import LogSistema


# ? Clase para el manejo de los logs dentro de la base de datos
class DatabaseHandle(logging.Handler):
    
    #  ^ Método para inicializar el handler
    def emit(self, record):
        try:
            # ? Guardamos el log dentro de la base de datos 
            with current_app.app_context():     # ? Creamos un ocntexto de la aplicación para poder usar la BD
                
                # * Creamos el registro de la Base de datos
                log_entry = LogSistema(
                    tipoLog=record.levelname,       # ~ Tipo de log (ERROR, SEGURIDAD, ACCESO, OPERACION)
                    descripcionLog=record.getMessage(),     # ~ Descripción del log
                    fechaHora=datetime.now(),       # Fechay la hora actual
                    ipOrigen=request.remote_addr if request else None,        # La IP del cliente
                    idUser=current_user.idUser if current_user.is_authenticated else None   # ~ ID del usuario que hizo la acción
                )

            # * Guardamos el log dentro de la base de datos
            db.session.add(log_entry)
            db.session.commit()

        except Exception as e:
            # ? si ocurre un fallo podemos registrar el error en el logger estándar
            logging.getLogger(__name__).error(f"Error al guardar log: {e}")
            db.session.rollback()


# ^ Método para configurar el logger
def configure_logging(app):

    # ? Configuramos el logger para la aplicación
    if not app.debug:  # ? Si la aplicación no está en modo debug
        # * Configuración básica del logging    
        logger = logging.getLogger('don_galleto')   # Nmobre del logger (Puede ser cualquiera)
        logging.basicConfig(level=logging.INFO) # Establecemos el nivel minimo de logging a mostar (minimo INFO que es el más bajo)

    
        # ? Configuramos el logger para que guarde los logs en la base de datos
        if not any(isinstance(h, DatabaseHandle) for h in logger.handlers):
            # * Crear y configurar el handler para la base de datos
            handler = DatabaseHandle()       # ? Instancia para usar la BD
            handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            logger.addHandler(handler)

        # * Configuramos el logger para que guarde los logs en un archivo
        app.logger = logger



# # ? Instanciamos el logger para usarlo en la aplicación
# loggerPersonalizado = setup_logging()
    

"""

"""