

from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
from ..services import agregar_proveedor, obtener_proveedores
#  ~ Importamos el archvio con el nombre del Blueprint para la sección
from ...admin import bp_admistracion


# ? En esta sección ira la parte de las rutas para el CRUD de las recetas:
    # * Agregar nuevas recetas a la BD
    # * Mostrar las recetas de la BD
    # * Modificar las recetas en la BD
    # * Actualizar nuevas recetas a la BD

# http://127.0.0.1:5000/production/recetas


@bp_admistracion.route('/recetas')
def recetas():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('shared.login'))
    return render_template('admin/recetas.html')
 