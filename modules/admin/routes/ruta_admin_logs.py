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
    # ?  Pirmero verificación de permisos
    if current_user.rol.nombreRol != 'Administrador':
        flash('No tienes permisos para acceder a esta sección', 'danger')
        current_app.logger.error(f'Acceso no autorizado a logs por {current_user.username}')
        return redirect(url_for('shared.index'))

    # * Filtros dle sistema
    tipo_log = request.args.get('tipo_log', '')     #  Filtramos le tipo de log, y si no hay nada, que traiga todos los logs 
    search_query = request.args.get('q', '')     #  Filtramos le tipo de log, y si no hay nada, que traiga todos los logs 
    page = request.args.get('page', 1, type=int)    # Númmero de página actual a la que se accede
    per_page = 15  # Cantidad de logs por página de la pagínación

    # ? COnusltamos la base de datos y hacemo un join para traernos el nombre dle usuario
    query = LogSistema.query.outerjoin(LogSistema.usuario)


    # ? Filtramos los logs por el tipo de log
    if tipo_log:
        query = query.filter(LogSistema.tipoLog == tipo_log)

    # # ? Filtramos los logs por el nombre del usuario
    # if search_query:
    #     query = query.filter(or_(
    #         LogSistema.descripcionLog.ilike(f'%{search_query}%'),
    #         LogSistema.ipOrigen.ilike(f'%{search_query}%'),
    #         LogSistema.usuario.has(username=search_query)
    #     ))

    # ? Ordemos la salida de la ocnsulta de fomra descendente
    query = query.order_by(LogSistema.fechaHora.desc())



    # ? Si tenemos un query de búsqueda, apicamos el flitro
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    logs = pagination.items

    # ? Si no hay logs, mostramos un mensaje
    current_app.logger.info(f'Acceso a Eventos por {current_user.username}')
    return render_template('admin/logs.html', logs=logs, pagination=pagination) # Renderizamos el HTML y le pasamos los logs y la pagínación