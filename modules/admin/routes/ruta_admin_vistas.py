from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import login_required, current_user

from modules.admin.routes.ruta_admin_dashboard import admin_required
from modules.admin.services import marcar_notificacion_como_vista, obtener_notificaciones_recientes
from .. import bp_admistracion


@bp_admistracion.route('/vistas')
@admin_required
def vistas():
    return render_template('admin/vistas.html')
