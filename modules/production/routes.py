from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify

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










