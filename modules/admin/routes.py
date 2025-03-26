

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
@bp_admistracion.route('/agregarProveedor', methots=['POST'])
def agregarProv():
    if request.method == 'POST':
        # * Recibimos los datos del formulario
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        correo = request.form['correo']
        direccion = request.form['direccion']
        productosProveedor = request.form['productosProveedor']
        tipoProveedor = request.form['tipoProveedor']

        # * Llamamos a la función para poder agregar un proveedor
        agregar_proveedor(nombre, telefono, correo, direccion, productosProveedor, tipoProveedor)

        # * Obtenemos los proveedores
        proveedoresNuevos=obtener_proveedores()

    proveedoresNuevos=agregar_proveedor()
    return render_template('admin/index.html', proveedores=proveedoresNuevos)





"""
* Opcion de copilot:
@bp_admistracion.route('/agregarProveedor', methods=['GET', 'POST'])
def agregarProv():
    if request.method == 'POST':
        # Recibimos los datos del formulario
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        correo = request.form.get('correo')
        direccion = request.form.get('direccion')
        productosProveedor = request.form.get('productosProveedor')
        tipoProveedor = request.form.get('tipoProveedor')

        # Llamamos a la función agregar_proveedor
        agregar_proveedor(nombre, telefono, correo, direccion, productosProveedor, tipoProveedor)

        flash('Proveedor agregado exitosamente', 'success')
        return redirect(url_for('admin.dashboard_admin'))

    # Si es una solicitud GET, renderizamos el formulario
    return render_template('admin/agregar_proveedor.html')

"""