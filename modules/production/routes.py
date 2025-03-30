from datetime import datetime
from flask import abort, render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify

from modules.admin.services import obtener_proveedores
#  ~ Importamos el archvio con el nombre del Blueprint para la sección
from . import bp_production


# ? Ahora vamos a definir las rutas necesarias para el bluprint

@bp_production.route('/dashboard_produccion')
def dashboard_produccion():
    if 'username' not in session or session['role'] != 'produccion':
        return redirect(url_for('admin.login'))
    return render_template('produccion/produccion.html')
# ^ Sección de producción

@bp_production.route('/inventario')
def inventario():
    productos = [
        {"nombre": "Harina", "imagen": "static/img/harina.png", "cantidad": 100, "piezas": 30, "stock": 5},
        {"nombre": "Azúcar", "imagen": "static/img/azucar.png", "cantidad": 100, "piezas": 30, "stock": 0},
        {"nombre": "Mantequilla", "imagen": "static/img/mantequilla.png", "cantidad": 100, "piezas": 30, "stock": 3},
        {"nombre": "Huevos", "imagen": "static/img/huevos.png", "cantidad": 100, "piezas": 30, "stock": 8},
    ]
    return render_template('produccion/inventario_insumos.html', inventario=productos)


@bp_production.route('/detalle/<nombre_insumo>')
def detalle_insumo(nombre_insumo):
    # Define los datos del inventario directamente aquí o usa la lista global
    inventario_data = [
        {
            "nombre": "Harina", 
            "imagen": "static/img/harina.png", 
            "cantidad": 100, 
            "piezas": 30, 
            "stock": 5,
            "lotes": [
                {"id": 1, "cantidad": 50, "caducidad": "2023-12-31", "mermas": 2},
                {"id": 2, "cantidad": 50, "caducidad": "2025-12-31", "mermas": 0}
            ]
        },
        {
            "nombre": "Azúcar", 
            "imagen": "static/img/azucar.png", 
            "cantidad": 200, 
            "piezas": 2, 
            "stock": 2,
            "lotes": [
                {"id": 1, "cantidad": 100, "caducidad": "2024-06-30", "mermas": 5},
                {"id": 1, "cantidad": 100, "caducidad": "2024-06-30", "mermas": 5}
            ]
        }
    ]
    
    # Buscar el insumo en los datos
    insumo = next((item for item in inventario_data 
                  if item['nombre'].lower() == nombre_insumo.lower()), None)
    
    if not insumo:
        abort(404, description="Insumo no encontrado")
    
    # Calcular lotes próximos a caducar
    hoy = datetime.now().date()
    proximos_caducar = []
    
    for lote in insumo.get('lotes', []):
        fecha_cad = datetime.strptime(lote['caducidad'], "%Y-%m-%d").date()
        if (fecha_cad - hoy).days <= 30:
            proximos_caducar.append(lote)
    
    return render_template('produccion/detalle_insumo.html',
                         insumo=insumo,
                         lotes=insumo.get('lotes', []),
                         proximos_caducar=proximos_caducar)

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


# * Ruta para el dashboard de producción
@bp_production.route('/produccion')
def produccion():
    if 'username' not in session or session['role'] != 'produccion':
        return redirect(url_for('production.login'))
    return render_template('produccion/produccion.html')










