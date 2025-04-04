

from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
from ..services import agregar_proveedor, obtener_proveedores
#  ~ Importamos el archvio con el nombre del Blueprint para la sección
from ...admin import bp_admistracion


# ? En esta sección ira la parte de las rutas para el dashboard principal:
    # * ventas diarias
    # * productos más vendidos
    # * presentaciones más vendidas
# ? Por ahora solo las graficas precargadas y lapantalla priciapl
# http://127.0.0.1:5000/admin/dashboard_admin

# * Ruta para el dashboard del administrador
@bp_admistracion.route('/dashboard_admin')
def dashboard_admin():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('shared.login'))
    return render_template('admin/dashboard.html')