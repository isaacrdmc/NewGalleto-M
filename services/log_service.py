

# ? En esta parte es donde tnedremos la calse para poder registrar los logs del sistema
from datetime import datetime
from flask import current_app, logging, request
from flask_login import current_user
# from app.models import LogsSistema, TipoLog
from database.conexion import db
# from modules.admin.models import LogsSistema, LogLevel
from modules.admin.models import SystemLog, LogLevel

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

            # * Obtener el contexto de la aplicación Flask
            app = current_app._get_current_object()

            with app.app_context():
                # Obtener información del usuario si está autenticado
                user_id = None
                if hasattr(current_app, 'login_manager'):
                    from flask_login import current_user
                    if current_user.is_authenticated:
                        user_id = current_user.idUser

            # * Obtenemos la IP del cliente
            ip = request.remote_addr if request else None

            # * Creamos el registro de la Base de datos
            log_entry = SystemLog(
                level=record.levelname,  # Nivel del log (INFO, WARNING, ERROR, etc.)
                message=record.getMessage(),  # Mensaje del log
                timestamp=datetime.utcnow(),  # Usamos UTC para consistencia
                ip_address=ip,
                user_id=user_id,
                extra_data={
                    'module': record.module,
                    'funcName': record.funcName,
                    'lineno': record.lineno
                }
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
        
    """Configura el sistema de logging para la aplicación"""
    
    # Eliminar handlers existentes del logger root
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Configurar el logger específico de la aplicación
    logger = logging.getLogger('don_galleto')
    logger.setLevel(logging.INFO)
    
    # Eliminar handlers existentes para evitar duplicados
    logger.handlers = []

    # Crear y configurar el handler para la base de datos
    db_handler = DatabaseHandler()
    db_handler.setLevel(logging.INFO)

    # Formato para los logs
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'
    )
    db_handler.setFormatter(formatter)

    # Añadir el handler al logger
    logger.addHandler(db_handler)

    # Configurar el logger de Flask
    app.logger = logger

    return logger

