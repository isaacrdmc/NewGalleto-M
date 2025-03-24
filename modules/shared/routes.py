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
    'user_produccion': {
        'password': generate_password_hash('produccionpass'),
        'role': 'produccion'
    },
    'user_ventas': {
        'password': generate_password_hash('ventaspass'),
        'role': 'ventas'
    },
    'user_cliente': {
        'password': generate_password_hash('clientepass'),
        'role': 'cliente'
    },
}

proveedor = [
    {"id": "0001", "empresa": "19 Hermanos", "telefono": "477-724-5893", 
     "correo": "queso@gmail.com", "direccion": "Paseo de los Insurgentes 362", 
     "productos": "Leche y queso"},
    {"id": "0002", "empresa": "Skibidi", "telefono": "477-123-4567", 
     "correo": "skibidi@gmail.com", "direccion": "Avenida Central 123", 
     "productos": "Bebidas"}
]

insumo = [
    {"id": 1, "lote": 1, "producto": "Huevo", "cantidad": 100, "fechaCaducidad": "2024-11-20", "mermas": 5},
    {"id": 2, "lote": 2, "producto": "Leche", "cantidad": 50, "fechaCaducidad": "2024-11-10", "mermas": 10}
]



# TODO Esta es la ruta que cargara por defecto
@bp_shared.route('/')
def index():
    if 'username' in session:
        # Redirige al dashboard correspondiente según el rol
        if session['role'] == 'admin':
            return redirect(url_for('dashboard_admin'))
        elif session['role'] == 'produccion':
            return redirect(url_for('produccion'))
        elif session['role'] == 'ventas':
            return redirect(url_for('ventas'))
        elif session['role'] == 'cliente':
            return redirect(url_for('portal_cliente'))
    return redirect(url_for('/login'))


# Ruta para el login
@bp_shared.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        active_tab = request.form.get('active_tab', 'Producción')  # Obtén la pestaña activa

        user = users.get(username)

        if user and check_password_hash(user['password'], password):
            # Bloquear admin si intenta entrar desde Cliente
            if active_tab == 'Cliente' and username == 'admin':
                flash('No se puede iniciar sesión como administrador en la pestaña de Cliente.', 'danger')
                return redirect(url_for('login'))

            # Validar si el rol coincide con la pestaña seleccionada
            if (user['role'] == 'produccion' and active_tab == 'Producción') or \
                (user['role'] == 'ventas' and active_tab == 'Ventas') or \
                (user['role'] == 'cliente' and active_tab == 'Cliente') or \
                (username == 'admin'):
            
                session['username'] = username
                session['role'] = user['role']
                flash('¡Has iniciado sesión correctamente!', 'success')
                return redirect(url_for('index'))  # Redirige al dashboard correcto

            flash('No tienes permisos para acceder a esta pestaña.', 'danger')
            return redirect(url_for('login'))

        flash('Nombre de usuario o contraseña incorrectos', 'danger')

    return render_template('shared/login.html')


# Ruta para cerrar sesión
@bp_shared.route('/logout')
def logout():
    session.clear()  # Elimina la sesión del usuario
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('login'))

