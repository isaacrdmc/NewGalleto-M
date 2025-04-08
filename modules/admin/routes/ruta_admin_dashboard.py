

from flask import current_app, render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import login_required, current_user
from ...admin import bp_admistracion

@bp_admistracion.route('/dashboard_admin')
@login_required
def dashboard_admin():
    if current_user.rol.nombreRol != 'Administrador':
        flash('No tienes permisos para acceder a esta sección', 'danger')
        current_app.logger.error(f'Acceso no autorizado a la página del dashboard por el usuario {current_user.username}')
        return redirect(url_for('shared.index'))
    current_app.logger.info(f'Acceso autorizado a la página del dashboard por el usuario {current_user.username}')
    return render_template('admin/dashboard.html') 