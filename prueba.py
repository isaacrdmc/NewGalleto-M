from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Clave secreta para manejar sesiones

# Datos de ejemplo de usuarios (simulando una base de datos)
usuarios = {
    'admin': {'password': 'admin123', 'rol': 'admin'},
    'vendedor': {'password': 'vendedor123', 'rol': 'vendedor'},
    'productor': {'password': 'productor123', 'rol': 'productor'},
    'cliente': {'password': 'cliente123', 'rol': 'cliente'}  # Nuevo usuario cliente
}

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    active_tab = 'login'  # Pestaña activa

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verificar si el usuario existe y la contraseña es correcta
        if username in usuarios and usuarios[username]['password'] == password:
            session['username'] = username
            session['rol'] = usuarios[username]['rol']
            return redirect(url_for('dashboard'))
        else:
            return "Usuario o contraseña incorrectos", 401

    return render_template('login.html', active_tab=active_tab)

@app.route('/register', methods=['GET', 'POST'])
def register():
    active_tab = 'register'  # Pestaña activa

    if request.method == 'POST':
        newUsername = request.form['newUsername']
        newPassword = request.form['newPassword']
        confirmPassword = request.form['confirmPassword']

        # Verificar si las contraseñas coinciden
        if newPassword != confirmPassword:
            return "Las contraseñas no coinciden", 400

        # Verificar si el usuario ya existe
        if newUsername in usuarios:
            return "El usuario ya existe", 400

        # Registrar el nuevo usuario (por defecto como cliente)
        usuarios[newUsername] = {'password': newPassword, 'rol': 'cliente'}
        return redirect(url_for('login'))

    return render_template('login.html', active_tab=active_tab)

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        rol = session['rol']
        if rol == 'admin':
            return render_template('dashboard_admin.html')
        elif rol == 'vendedor':
            return render_template('dashboard_vendedor.html')
        elif rol == 'productor':
            return render_template('dashboard_productor.html')
        elif rol == 'cliente':
            return redirect(url_for('portal_cliente'))  # Redirigir al portal del cliente
    return redirect(url_for('login'))

@app.route('/portal_cliente')
def portal_cliente():
    if 'username' in session and session['rol'] == 'cliente':
        return render_template('portal_cliente.html')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('rol', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)