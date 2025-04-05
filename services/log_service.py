

# ? En esta parte es donde tnedremos la calse para poder registrar los logs del sistema
from datetime import datetime
from flask import logging, request
from flask_login import current_user
# from app.models import LogsSistema, TipoLog
from app import db
from modules.admin.models import LogsSistema, TipoLog
"""
class LogService:
    # ? Creamos los metodos para poder crear un nuevo log del sistema
    @staticmethod
    def registrar_log(tipo_log, descripcion_log, usuario_id=None, ip=None):

        # * Obtenemos la Ip del usuario si es que aun no la tenemos
        if not ip:
            ip=request.remote_addr if request else None

        
        # * Creamos el nuevo log
        nuevo_log = LogsSistema(
            tipoLog=tipo_log,
            descripcionLog=descripcion_log,
            ipOrigen=ip,
            idUsuario=usuario_id
        )

        
        # * Guardamos el llog dentro de la BD
        db.session.add(nuevo_log)
        try:
            db.session.commi()
            return True
        except Exception as e:
            db.session.rollback()
            print(f'Error al guardar el log: {e}')
            return False



    # ? Metodo para poder crear los logs cuando se tiene el objeto creado
    @staticmethod
    def crear_log(tipo_log, descripcion_log, usuario_actual):
        
        # * Si el usuario no está autenticado, no se crea el log
        if not usuario_actual or not usuario_actual.is_authenticated:
            return False
        
        # * Obtenemos la IP del cliente
        ip = request.remote_addr if request else None

        # * Entregamos
        return LogService.registrar_log(
            tipo_log=tipo_log,
            descripcion_log=descripcion_log,
            usuario_id=usuario_actual.idUser,
            ip=ip
        )
    


    # ^ Creamos los nuevos metodos para los Logs del sistema

    @staticmethod
    # * Log para registrar un evento de seguridad/errores
    def log_segurdidad(descripcion_log, usuario_actual):
        LogService.crear_log(TipoLog.SEGURIDAD, descripcion_log, usuario_actual)

    @staticmethod
    # * Log para registrar una operacion del admistrador
    def log_operacion(descripcion_log, usuario_actual):
        LogService.crear_log(TipoLog.OPERACION, descripcion_log, usuario_actual)

    @staticmethod
    # * Log para registrar un error del sistema
    def log_error(descripcion_log, usuario_actual):
        LogService.crear_log(TipoLog.ERROR, descripcion_log, usuario_actual)

    @staticmethod
    # * Log para un evento de acceso
    def log_acceso(descripcion_log, usuario_actual):
        LogService.crear_log(TipoLog.ACCESO, descripcion_log, usuario_actual)

    
    # ? Metodo para obtener logs con filtros opconeales
    @staticmethod
    def obtener_log(usuario_id=None, tipo_log=None, limite=100):
        
        # * Obtenemos los logs:
        query = LogService.query.order_by(LogsSistema.fechaHora.desc())

        # Filtro por el usuario
        if usuario_id:
            query = query.filter_by(idUsuario=usuario_id)

        # filtro por el tipo de log
        if tipo_log:
            query = query.filter_by(tipoLog=tipo_log)

        # 
        return query.limit(limite).all()

"""

class DatabaseHandle(logging.Handler):
    
    #  ^ Método para inicializar el handler
    def emit(self, record):
        try:
            # * Obtenemos información sobre sis el usuario esta autenticado
            user_id = current_user.idUser if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated else None

            # * Obtenemos la IP del cliente
            ip = request.remote_addr if request else None

            # * Creamos el registro de la Base de datos
            log_entry = LogsSistema(
                TipoLog=record.levelname,       # Tipo de log (ERROR, SEGURIDAD, ACCESO, OPERACION)
                descripcionLog=record.getMessage(),     # Descripción del log
                fechaHora=datetime.now(),       # Fechay la hora actual
                ipOrigen=ip,        # La IP del cliente
                ipUser=user_id      # ID del usuario que hizo la acción
            )

            # * Guardamos el log dentro de la base de datos
            db.session.add(log_entry)
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            # ? si ocurre un fallo podemos registrar el error en el logger estándar
            logging.getLogger(__name__).error(f"No se pudo guardar el log en la BD: {e}")




    # ^ Método para configurar el logger
    def setup_logging(app):
        
        # * Configuración básica del logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('don_galleto')

        # * Eliminamos handlers existentes para evitar duplicados
        if logger.handlers:
            logger.handlers = []


        # * Crear y configurar el handler para la base de datos
        db_handler = DatabaseHandle()
        db_handler.setLevel(logging.INFO)

        # * Formato del log
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        db_handler.setFormatter(formatter)

        # * Añadimos el handler al logger
        logger.addHandler(db_handler)

        return logger
    

    # ? logger = setup_logging(app)
    logger = setup_logging()
    

