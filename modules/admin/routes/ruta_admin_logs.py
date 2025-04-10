from flask import current_app, redirect, render_template, jsonify, request, session, url_for
from flask_login import current_user

from modules.admin.models import SystemLog, LogLevel
from services.log_service import LogService
from ..services import obtener_logs
from ...admin import bp_admistracion

# @bp_admistracion.route('/logs', methods=['GET'], endpoint='logs')
@bp_admistracion.route('/logs', methods=['GET'])
def ver_logs():
    if 'username' not in session or session['role'] != 'admin':
        current_app.logger.warning(
            "Intento de acceso no autorizado a los logs del sistema",
            extra={
                'user': current_user.username if hasattr(current_user, 'username') else None,
                'ip': request.remote_addr,
                'tipo_log': 'SECURITY'
            }
        )
        return redirect(url_for('login'))
    
    # Obtener parámetros de filtrado
    page = request.args.get('page', 1, type=int)
    per_page = 20
    tipo_log = request.args.get('tipo_log', None)
    usuario_id = request.args.get('usuario_id', None)
    
    # Construir consulta
    query = SystemLog.query.order_by(SystemLog.timestamp.desc())
    
    if tipo_log:
        query = query.filter(SystemLog.level == tipo_log.upper())
    
    if usuario_id:
        query = query.filter(SystemLog.user_id == usuario_id)
    
    # Paginación
    logs = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/logs.html', logs=logs)
