

from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
from .services import agregar_proveedor, obtener_proveedores
#  ~ Importamos el archvio con el nombre del Blueprint para la sección
from . import bp_admistracion


# ? Ahora vamos a definir las rutas necesarias para el bluprint


# ^ Sección del adminstrador

proveedor = [
    {"id": "0001", "empresa": "19 Hermanos", "telefono": "477-724-5893", 
     "correo": "queso@gmail.com", "direccion": "Paseo de los Insurgentes 362", 
     "productos": "Leche y queso"},
    {"id": "0002", "empresa": "Skibidi", "telefono": "477-123-4567", 
     "correo": "skibidi@gmail.com", "direccion": "Avenida Central 123", 
     "productos": "Bebidas"}
]



# @bp_admistracion.route('/adminstrador/DashBoad')
# def dashboard():
#     return 

# * Sección para el CRUD de los Uusarios
@bp_admistracion.route('/usuarios')
def usuarios():
    return render_template('admin/usuarios.html')

# * Ruta para el dashboard del administrador
@bp_admistracion.route('/dashboard_admin')
def dashboard_admin():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('admin.login'))
    return render_template('admin/dashboard.html')


# ~ Sección para el porveedores


# * nueva ruta, ruta para el CRUD de los proveedores
@bp_admistracion.route('/agregarProveedor')
def agregarProv():
    proveedoresNuevos=agregar_proveedor()
    return render_template('admin/index.html', proveedores=proveedoresNuevos)










# ! No se que hace
@bp_admistracion.route('/perfil')
def perfil():
    if 'username' not in session or session['role'] != 'cliente':
        return redirect(url_for('admin.login'))
    return render_template('client/perfil_cliente.html')

