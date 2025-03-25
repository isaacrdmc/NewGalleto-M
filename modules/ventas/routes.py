from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash,check_password_hash
#  ~ Importamos el archvio con el nombre del Blueprint para la sección
from . import bp_ventas


# ? Ahora vamos a definir las rutas necesarias para el bluprint




# ^ Sección del vendedor

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

# Ruta para el dashboard de ventas
@bp_ventas.route('/ventas')
def ventas():
    if 'username' not in session or session['role'] != 'ventas':
        return redirect(url_for('ventas.login'))
    return render_template('ventas/ventas.html')

@bp_ventas.route('/insumos/agregar', methods=['POST'])
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



