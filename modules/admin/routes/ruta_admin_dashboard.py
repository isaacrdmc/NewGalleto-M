

from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import login_required, current_user
from ...admin import bp_admistracion

@bp_admistracion.route('/dashboard_admin')
@login_required
def dashboard_admin():
    if current_user.rol.nombreRol != 'Administrador':
        flash('No tienes permisos para acceder a esta sección', 'danger')
        return redirect(url_for('shared.index'))
    return render_template('admin/dashboard.html')