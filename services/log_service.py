

# ? En esta parte es donde tnedremos la calse para poder registrar los logs del sistema
from datetime import datetime
from flask import request
# from app.models import LogsSistema, TipoLog
from app import db
from modules.admin.models import LogsSistema, TipoLog

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




