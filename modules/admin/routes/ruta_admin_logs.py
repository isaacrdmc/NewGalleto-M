from flask import redirect, render_template, jsonify, request, session, url_for
from flask_login import current_user

from modules.admin.models import TipoLog
from services.log_service import LogService
from ..services import obtener_logs
from ...admin import bp_admistracion

@bp_admistracion.route('/logs', methods=['GET'])
def ver_logs():

    #  
    if 'username' not in session or session['rol'] != 'admin':
        LogService.log_segurdidad("Intento de acceso no autorizado a los logs del sistema", current_user if 'username' in session else None)
        return redirect(url_for('shared.login'))
    
    # ? Parámetros de filtro
    tipo_log = request.args.get('tipo')
    usuario_id = request.args.get('usuario_id')
    limite = int(request.args.get('limite', 100))
    
    # * Registrar acceso
    LogService.log_acceso(f"Usuario {session['username']} consultó los logs del sistema", current_user)

    # ? Obtenemos los logs del sistema
    log = LogService.obtener_log(
        usuario_id=usuario_id,
        tipo_log=tipo_log if tipo_log else None,
        limite=limite
    )

    # * Listamos los usuarios para el filtro de los datos
    usuario = usuario.query.all()

    # * 
    return render_template(
        'admin/logs.html',
        logs=log,
        usuarios=usuario,
        tipo_log=TipoLog,
        filtro_actual={
            'tipo': tipo_log,
            'usuario_id': usuario_id,
            'limite': limite
        }
        

    )

