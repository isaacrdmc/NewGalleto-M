from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash,check_password_hash
#  ~ Importamos el archvio con el nombre del Blueprint para la sección
from . import bp_shared


# ? Ahora vamos a definir las rutas necesarias para el bluprint


# ^ Comprtido


# Simularemos algunos usuarios y contraseñas
users = {
    'admin': {
        'password': generate_password_hash('adminpass'),
        'role': 'admin'
    },
    'produccion': {
        'password': generate_password_hash('produccionpass'),
        'role': 'produccion'
    },
    'ventas': {
        'password': generate_password_hash('ventaspass'),
        'role': 'ventas'
    },
    'cliente': {
        'password': generate_password_hash('clientepass'),
        'role': 'cliente'
    },
}


# TODO Esta es la ruta que cargara por defecto
@bp_shared.route('/')
def index():
    if 'username' in session:
        # Redirige al dashboard correspondiente según el rol
        if session['role'] == 'admin':
            return redirect(url_for('admin.dashboard_admin'))
        elif session['role'] == 'produccion':
            return redirect(url_for('production.produccion'))
        elif session['role'] == 'ventas':
            return redirect(url_for('ventas.ventas'))
        elif session['role'] == 'cliente':
            return redirect(url_for('cliente.portal_cliente'))
    return redirect(url_for('shared.login'))


# Ruta para el login
@bp_shared.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users.get(username)

        if user and check_password_hash(user['password'], password):
            # Validar si el usuario tiene un rol válido
            if username == 'admin' or user['role'] in ['produccion', 'ventas', 'cliente']:
                session['username'] = username
                session['role'] = user['role']
                flash('¡Has iniciado sesión correctamente!', 'success')
                return redirect(url_for('shared.index'))  # Redirige al dashboard correspondiente

            flash('No tienes permisos para acceder.', 'danger')
            return redirect(url_for('shared.login'))

        flash('Nombre de usuario o contraseña incorrectos', 'danger')

    return render_template('shared/login.html')


# Ruta para cerrar sesión
@bp_shared.route('/logout')
def logout():
    session.clear()  # Elimina la sesión del usuario
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('shared.login'))


@bp_shared.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Lógica para registrar un cliente
        pass
    return render_template('shared/register.html')

