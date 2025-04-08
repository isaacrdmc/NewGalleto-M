

from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import login_required, current_user
from ...admin import bp_admistracion


# ? En esta sección ira la parte de las rutas para el CRUD de los usuairos:
    # * Agregar nuevos usuarios a la BD
    # * Mostrar los datos de la BD
    # * Modificar los usuarios en la BD
    # * Actualizar nuevos usuairos a la BD

# http://127.0.0.1:5000/admin/usuarios


# * Sección para el CRUD de los Uusarios

# TODO Ruta de prueva?
# @bp_admistracion.route('/usuarios')
# def usuarios():
#     if 'username' not in session or session['role'] != 'admin':
#         return redirect(url_for('cliente.login'))
#     return render_template('admin/usuarios.html')


@bp_admistracion.route('/usuarios')
def usuarios():
    if current_user.rol.nombreRol != 'Administrador':
        return redirect(url_for('shared.login'))
    return render_template('admin/usuarios.html')
# ~ Sección para el porveedores
 