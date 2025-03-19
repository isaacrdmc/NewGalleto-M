from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'mySecretKey'  # Necesario para manejar las sesiones

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


# Ruta principal (puede redirigir al login o al dashboard)
@app.route('/')
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
@app.route('/login', methods=['GET', 'POST'])
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

    return render_template('login.html')

# Ruta para el dashboard del administrador
@app.route('/dashboard_admin')
def dashboard_admin():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('modules/admin/dashboard.html')


# Ruta para el dashboard de producción
@app.route('/produccion')
def produccion():
    if 'username' not in session or session['role'] != 'produccion':
        return redirect(url_for('login'))
    return render_template('modules/produccion/produccion.html')


# Ruta para el dashboard de ventas
@app.route('/ventas')
def ventas():
    if 'username' not in session or session['role'] != 'ventas':
        return redirect(url_for('login'))
    return render_template('modules/ventas/ventas.html')


# Ruta para el dashboard del cliente
@app.route('/portal_cliente')
def portal_cliente():
    if 'username' not in session or session['role'] != 'cliente':
        return redirect(url_for('login'))
    return render_template('modules/client/portal_cliente.html')


# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.clear()  # Elimina la sesión del usuario
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('login'))


# Otras rutas...
@app.route('/usuarios')
def usuarios():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('modules/admin/usuarios.html')


@app.route('/proveedores')
def proveedores():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('modules/admin/proveedores.html')


@app.route('/clientes')
def clientes():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('modules/admin/clientes.html')


@app.route('/recetas')
def recetas():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('modules/admin/recetas.html')


@app.route('/inventario_insumos')
def inventario_insumos():
    if 'username' not in session or session['role'] != 'produccion':
        return redirect(url_for('login'))
    return render_template('modules/produccion/mat_prim.html')


@app.route('/inventario_galletas')
def inventario_galletas():
    if 'username' not in session or session['role'] != 'ventas':
        return redirect(url_for('login'))
    return render_template('modules/ventas/prod_term.html')


@app.route('/perfil')
def perfil():
    if 'username' not in session or session['role'] != 'cliente':
        return redirect(url_for('login'))
    return render_template('modules/client/perfil_cliente.html')

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)
