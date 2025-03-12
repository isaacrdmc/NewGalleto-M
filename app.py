from flask import Flask, render_template

app = Flask(__name__)

# Ruta principal (puede redirigir al login o al dashboard)
@app.route('/')
def index():
    return render_template('login.html')

# Ruta para el login
@app.route('/login')
def login():
    return render_template('login.html')

# Ruta para el dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Ruta para la gestión de usuarios
@app.route('/usuarios')
def usuarios():
    return render_template('usuarios.html')

# Ruta para la gestión de proveedores
@app.route('/proveedores')
def proveedores():
    return render_template('proveedores.html')

# Ruta para la gestión de clientes
@app.route('/clientes')
def clientes():
    return render_template('clientes.html')

# Ruta para la gestión de recetas
@app.route('/recetas')
def recetas():
    return render_template('recetas.html')

# Ruta para el inventario de materias primas
@app.route('/inventario_materias_primas')
def inventario_materias_primas():
    return render_template('mat_prim.html')

# Ruta para el inventario de productos terminados
@app.route('/inventario_productos_terminados')
def inventario_productos_terminados():
    return render_template('prod_term.html')

# Ruta para el módulo de producción
@app.route('/produccion')
def produccion():
    return render_template('produccion.html')

# Ruta para el módulo de ventas
@app.route('/ventas')
def ventas():
    return render_template('ventas.html')

# Ruta para el módulo de pedidos
@app.route('/pedidos')
def pedidos():
    return render_template('pedidos.html')

# Ruta para el portal del cliente
@app.route('/portal_cliente')
def portal_cliente():
    return render_template('portal_cliente.html')

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)