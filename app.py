
# TODO archvio de ejecución de la APP
from app import create_app         # ? De la acrpeta de APP importamos la carpeta app

app = create_app()

# * Ejecutar la aplicación en su totalidad
if __name__ == '__main__':
    app.run(debug=True)


# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import csv
from io import StringIO
from datetime import datetime, timedelta




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


# Ruta principal (puede redirigir al login o al dashboard)


# ^ Comprtido
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

    return render_template('shared/login.html')


# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.clear()  # Elimina la sesión del usuario
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('login'))










# ^ Sección del adminstrador

# Ruta para el dashboard del administrador
@app.route('/dashboard_admin')
def dashboard_admin():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('admin/dashboard.html')

@app.route('/insumos/<id>', methods=['GET'])
def obtener_insumo(id):
    for i in insumo:
        if i['id'] == id:
            return jsonify(i)
    return jsonify({"error": "Insumo no encontrado"}), 404

@app.route('/insumos/editar/<id>', methods=['POST'])
def editar_insumo(id):
    if request.is_json:
        datos = request.get_json()  # Obtener los datos JSON del cuerpo de la solicitud
        for i in insumo:  # Asegúrate de que el nombre de la lista sea "insumos"
            if i['id'] == id:
                # Usar los datos del JSON recibido para actualizar el insumo
                i['lote'] = datos['lote']
                i['producto'] = datos['producto']
                i['cantidad'] = datos['cantidad']
                i['fechaCaducidad'] = datos['fechaCaducidad']
                i['mermas'] = datos['mermas']
                # Retornar el mensaje de éxito junto con el insumo actualizado
                return jsonify({"mensaje": "Insumo actualizado correctamente", "insumo": i})
        # Si no se encontró el insumo
        return jsonify({"error": "Insumo no encontrado"}), 404
    else:
        return jsonify({"error": "Tipo de contenido no soportado"}), 415

@app.route('/insumos/eliminar/<id>', methods=['DELETE'])
def eliminar_insumo(id):
    global insumo
    insumo = [i for i in insumo if i['id'] != id]
    return jsonify({"mensaje": "Insumo eliminado"})

@app.route('/perfil')
def perfil():
    if 'username' not in session or session['role'] != 'cliente':
        return redirect(url_for('login'))
    return render_template('client/perfil_cliente.html')










# ^ Sección del vendedor

# Ruta para el dashboard de ventas
@app.route('/ventas')
def ventas():
    if 'username' not in session or session['role'] != 'ventas':
        return redirect(url_for('login'))
    return render_template('ventas/ventas.html')

@app.route('/insumos/agregar', methods=['POST'])
def agregar_insumo():
    datos = request.get_json()
    nuevo_insumo = {
        "id": str(len(insumo) + 1).zfill(4),  # Generar ID automático
        "lote": datos['lote'],
        "producto": datos['producto'],
        "cantidad": datos['cantidad'],
        "fechaCaducidad": datos['fechaCaducidad'],
        "mermas": datos['mermas']
    }
    insumo.append(nuevo_insumo)
    return jsonify({"mensaje": "Insumo agregado", "insumo": nuevo_insumo})











# ^ Sección de producción

# Ruta para el dashboard de producción
@app.route('/produccion')
def produccion():
    if 'username' not in session or session['role'] != 'produccion':
        return redirect(url_for('login'))
    return render_template('produccion/produccion.html')

@app.route('/proveedores')
def proveedores():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('admin/proveedores.html', proveedor=proveedor)

@app.route('/proveedores/agregar', methods=['POST'])
def agregar_proveedor():
    datos = request.get_json()
    nuevo_proveedor = {
        "id": str(len(proveedor) + 1).zfill(4),  # Generar ID automático
        "empresa": datos['empresa'],
        "telefono": datos['telefono'],
        "correo": datos['correo'],
        "direccion": datos['direccion'],
        "productos": datos['productos']
    }
    proveedor.append(nuevo_proveedor)
    return jsonify({"mensaje": "Proveedor agregado", "proveedor": nuevo_proveedor})

@app.route('/proveedores/<id>', methods=['GET'])
def obtener_proveedor(id):
    for p in proveedor:
        if p['id'] == id:
            return jsonify(p)
    return jsonify({"error": "Proveedor no encontrado"}), 404

@app.route('/proveedores/editar/<id>', methods=['POST'])
def editar_proveedor(id):
    if request.is_json:
        datos = request.get_json()  # Obtener los datos JSON del cuerpo de la solicitud
        for p in proveedor:  # Asegúrate de que el nombre de la lista sea "proveedores"
            if p['id'] == id:
                # Usar los datos del JSON recibido para actualizar el proveedor
                p['empresa'] = datos['empresa']
                p['telefono'] = datos['telefono']
                p['correo'] = datos['correo']
                p['direccion'] = datos['direccion']
                p['productos'] = datos['productos']
                # Retornar el mensaje de éxito junto con el proveedor actualizado
                return jsonify({"mensaje": "Proveedor actualizado correctamente", "proveedor": p})
        # Si no se encontró el proveedor
        return jsonify({"error": "Proveedor no encontrado"}), 404
    else:
        return jsonify({"error": "Tipo de contenido no soportado"}), 415

@app.route('/proveedores/eliminar/<id>', methods=['DELETE'])
def eliminar_proveedor(id):
    global proveedor
    proveedor = [p for p in proveedor if p['id'] != id]
    return jsonify({"mensaje": "Proveedor eliminado"})

@app.route('/recetas')
def recetas():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('admin/recetas.html')

# Ruta para gestionar insumos
@app.route('/insumos')
def insumos():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('admin/insumos.html', insumo=insumo)

@app.route('/inventario_insumos')
def inventario_insumos():
    if 'username' not in session or session['role'] != 'produccion':
        return redirect(url_for('login'))
    return render_template('produccion/mat_prim.html')

@app.route('/inventario_galletas')
def inventario_galletas():
    if 'username' not in session or session['role'] != 'ventas':
        return redirect(url_for('login'))
    return render_template('ventas/prod_term.html')











# ^ Sección del cliente

# Ruta para el dashboard del cliente
@app.route('/portal_cliente')
def portal_cliente():
    if 'username' not in session or session['role'] != 'cliente':
        return redirect(url_for('login'))
    return render_template('client/portal_cliente.html')

# Otras rutas...
@app.route('/usuarios')
def usuarios():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('admin/usuarios.html')


@app.route('/clientes')
def clientes():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('admin/clientes.html')







