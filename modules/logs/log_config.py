

# ? En esta parte es donde tnedremos la calse para poder registrar los logs del sistema
from datetime import datetime
from flask import logging, request
from flask_login import current_user
# from app.models import LogsSistema, TipoLog
from database.conexion import db
from modules.admin.models import LogsSistema, TipoLog


# ? Clase para el manejo de los logs dentro de la base de datos
class DatabaseHandle(logging.Handler):
    
    #  ^ Método para inicializar el handler
    def emit(self, record):
        try:
            # * Obtenemos información sobre sis el usuario esta autenticado y guardamos su ID
            # * En caso contario el ID queda como None
            user_id = current_user.id if current_user.is_authenticated else None

            # * Obtenemos la IP del cliente
            # * En caso contario la IP queda como None
            ip = request.remote_addr if request else None

            # * Creamos el registro de la Base de datos
            log_entry = LogsSistema(
                tipoLog=record.levelname,       # ~ Tipo de log (ERROR, SEGURIDAD, ACCESO, OPERACION)
                descripcionLog=record.getMessage(),     # ~ Descripción del log
                fechaHora=datetime.now(),       # Fechay la hora actual
                ipOrigen=request.remote_addr if request else None,        # La IP del cliente
                ipUser=user_id      # ID del usuario que hizo la acción
            )

            # * Guardamos el log dentro de la base de datos
            db.session.add(log_entry)
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            # ? si ocurre un fallo podemos registrar el error en el logger estándar
            logging.getLogger(__name__).error(f"Error al guardar log: {e}")




    # ^ Método para configurar el logger
    def setup_logging(app):
        
        # * Configuración básica del logging
        logging.basicConfig(level=logging.INFO) # Establecemos el nivel minimo de logging a mostar (minimo INFO que es el más bajo)
        logger = logging.getLogger('don_galleto')   # Nmobre del logger (Puede ser cualquiera)

        # * Eliminamos handlers existentes para evitar duplicados de logs
        if logger.handlers:
            logger.handlers = []


        # * Crear y configurar el handler para la base de datos
        db_handler = DatabaseHandle()       # ? Instancia para usar la BD
        db_handler.setLevel(logging.INFO)   # * Le decimmos que únicamente capture logs mayoes que INFO (Osea todos)

        # * Formato del log     
                                    # ? Fecha y hora - nivel de log - mensaje del log
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        db_handler.setFormatter(formatter)

        # * Añadimos el handler al logger
        logger.addHandler(db_handler)

        return logger
    

    # ? Instanciamos el logger para usarlo en la aplicación
    loggerPersonalizado = setup_logging()
    

