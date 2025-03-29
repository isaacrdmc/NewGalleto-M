

from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
from ..services import agregar_proveedor, obtener_proveedores
#  ~ Importamos el archvio con el nombre del Blueprint para la sección
from ...admin import bp_admistracion


# ? En esta sección ira la parte de las rutas para el CRUD de los clientes (No se cual es la diferencia):
    # * Agregar nuevos usuarios a la BD
    # * Mostrar los datos de la BD
    # * Modificar los usuarios en la BD
    # * Actualizar nuevos usuairos a la BD

# http://127.0.0.1:5000/admin/usuarios


# ^ Sección del cliente

# Ruta para el dashboard del cliente
@bp_admistracion.route('/portal_cliente')
def portal_cliente():
    if 'username' not in session or session['role'] != 'cliente':
        return redirect(url_for('cliente.login'))
    return render_template('client/portal_cliente.html')


@bp_admistracion.route('/clientes')
def clientes():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('cliente.login'))
    return render_template('admin/clientes.html')


 