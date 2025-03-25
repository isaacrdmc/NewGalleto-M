

from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
from .services import agregar_proveedor, obtener_proveedores
#  ~ Importamos el archvio con el nombre del Blueprint para la sección
from . import bp_admistracion


# ? Ahora vamos a definir las rutas necesarias para el bluprint


# ^ Sección del adminstrador

@bp_admistracion.route('/adminstrador/DashBoad')
def dashboard():
    return 

@bp_admistracion.route('/usuarios')
def usuarios():
    return render_template('admin/usuarios.html')

# Ruta para el dashboard del administrador
@bp_admistracion.route('/dashboard_admin')
def dashboard_admin():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('admin.login'))
    return render_template('admin/dashboard.html')


@bp_admistracion.route('/perfil')
def perfil():
    if 'username' not in session or session['role'] != 'cliente':
        return redirect(url_for('admin.login'))
    return render_template('client/perfil_cliente.html')


# TODO nueva ruta,
@bp_admistracion.route('/agregarProveedor')
def agregarProv():
    proveedoresNuevos=agregar_proveedor()
    return render_template('admin/index.html', proveedores=proveedoresNuevos)