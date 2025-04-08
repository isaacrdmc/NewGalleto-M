from operator import or_
import re
from flask import current_app, render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
 
from database.conexion import db
#  ~ Importamos el archvio con el nombre del Blueprint para la sección
from flask_login import login_required, current_user

from modules.logs.models import LogSistema
from ...admin import bp_admistracion



# # ^ Vamos a crear las rutas para renderizar el HTML y mostrar los logs almacenados en la BD 


# # * Renderizar el HTML 
@bp_admistracion.route('/logs_admin')
# @login_required
def logs_admin():
    # Verificación de permisos
    if current_user.rol.nombreRol != 'Administrador':
        flash('No tienes permisos para acceder a esta sección', 'danger')
        current_app.logger.error(f'Acceso no autorizado a logs por {current_user.username}')
        return redirect(url_for('shared.index'))

    # Filtros
    tipo_log = request.args.get('tipo_log', '')
    search_query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = 15  # Items por página

    # Consulta base con join a usuarios
    query = LogSistema.query.outerjoin(LogSistema.usuario)

    # Aplicar filtros
    if tipo_log:
        query = query.filter(LogSistema.tipoLog == tipo_log)
    if search_query:
        query = query.filter(or_(
            LogSistema.descripcionLog.ilike(f'%{search_query}%'),
            LogSistema.ipOrigen.ilike(f'%{search_query}%'),
            LogSistema.usuario.has(username=search_query)
        ))

    # Ordenar por fecha descendente (los más recientes primero)
    query = query.order_by(LogSistema.fechaHora.desc())

    # Paginación
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    logs = pagination.items

    current_app.logger.info(f'Acceso a logs por {current_user.username}')
    return render_template('admin/logs.html', 
                         logs=logs,
                         pagination=pagination)