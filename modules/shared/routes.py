from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
#  ~ Importamos el archvio con el nombre del Blueprint para la sección
from . import bp_shared


# ? Ahora vamos a definir las rutas necesarias para el bluprint




# ^ Comprtido
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
    return redirect(url_for('login'))


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

