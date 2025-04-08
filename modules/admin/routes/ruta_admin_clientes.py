

from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import login_required, current_user
from ...admin import bp_admistracion


# ? En esta sección ira la parte de las rutas para el CRUD de los clientes (No se cual es la diferencia):
    # * Agregar nuevos usuarios a la BD
    # * Mostrar los datos de la BD
    # * Modificar los usuarios en la BD
    # * Actualizar nuevos usuairos a la BD

# http://127.0.0.1:5000/admin/usuarios


# ^ Sección del clientes

@bp_admistracion.route('/clientes')
@login_required
def clientes():
    if current_user.rol.nombreRol != 'Administrador':
        return redirect(url_for('shared.login'))
    return render_template('admin/clientes.html')
