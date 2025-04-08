import re
from flask import current_app, render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
 
from database.conexion import db
#  ~ Importamos el archvio con el nombre del Blueprint para la sección
from flask_login import login_required, current_user
from ...admin import bp_admistracion



# # ^ Vamos a crear las rutas para renderizar el HTML y mostrar los logs almacenados en la BD 


# # * Renderizar el HTML 
@bp_admistracion.route('/logs_admin')
def logs_admin():
    # * Verificamos si el usuario tiene permisos para acceder a esta sección
    if current_user.rol.nombreRol != 'Administrador':
        flash('No tienes permitidos para acceder a esta sección', 'danger')
        current_app.logger.error(f'Acceso no autorizado a la página de logs por el usuario {current_user.username}')
        return redirect(url_for('shared.index'))
    current_app.logger.info(f'Acceso autorizado a la página de logs por el usuario {current_user.username}')
    return render_template('admin/logs.html')
        

 