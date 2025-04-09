from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import login_required, current_user
from .. import bp_admistracion


# ? En esta sección ira la parte de las rutas para el CRUD de los insumos que es el inventario:
    # * Agregar nuevos proveedores a la BD
    # * Mostrar los proveedores de la BD
    # * Modificar los proveedores en la BD
    # * Actualizar nuevos proveedores a la BD

    # * Alerta de los que nos quedan pocos


# http://127.0.0.1:5000/production/insumos


# Ruta para gestionar insumos dentro del archivo rutas de la carpeta producción
@bp_admistracion.route('/vistas')
@login_required
def vistas():
    if current_user.rol.nombreRol != 'Administrador':
        return redirect(url_for('shared.login'))
    return render_template('admin/vistas.html')
