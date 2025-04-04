

# ? En esta parte es donde tnedremos la calse para poder registrar los logs del sistema
from datetime import datetime
from flask import request
# from app.models import LogsSistema, TipoLog
from app import db
from modules.admin.models import LogsSistema

class LogService:
    @staticmethod
    def crear_log(tipo_log, descripcion_log, usuario_actual):
        
        # * Si el usuario no está autenticado, no se crea el log
        if not usuario_actual or not usuario_actual.is_authenticated:
            return
        
        # * Obtenemos la IP del cliente
        ip = request.remote_addr if request else None

        # * Creamos el nuevo log
        nuevo_log = LogsSistema(
            tipoLog=tipo_log,
            descripcionLog=descripcion_log,
            ipOrigen=ip,
            idUsuario=usuario_actual.idUser
        )

        # * Guardamos el nuevo log dentro de la Base de datos
        db.session.add(nuevo_log)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f'Error al guardar el log: {e}')
        
        # ^ Creamos los nuevos metodos para los Logs del sistema

        @staticmethod
        # * Log para registrar un evento de seguridad/errores
        def log_segurdidad(descripcion_log, usuario_actual):
            LogService.crear_log(tipo_log.SEGURIDAD, descripcion_log, usuario_actual)

        @staticmethod
        # * Log para registrar una operacion del admistrador
        def log_operacion(descripcion_log, usuario_actual):
            LogService.crear_log(tipo_log.OPERACION, descripcion_log, usuario_actual)

        @staticmethod
        # * Log para registrar un error del sistema
        def log_error(descripcion_log, usuario_actual):
            LogService.crear_log(TipoLog.ERROR, descripcion_log, usuario_actual)

        @staticmethod
        # * Log para un evento de acceso
        def log_acceso(descripcion_log, usuario_actual):
            LogService.crear_log(tipo_log.ACCESO, descripcion_log, usuario_actual)



