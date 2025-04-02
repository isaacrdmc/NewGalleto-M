from datetime import datetime
import os
from flask import abort, json, render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify

from modules.admin.services import obtener_proveedores
#  ~ Importamos el archvio con el nombre del Blueprint para la sección
from . import bp_production


# ? Ahora vamos a definir las rutas necesarias para el bluprint
# * Ruta para el dashboard de producción

@bp_production.route('/produccion')
def produccion():
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


insumo = [
    {"id": 1, "lote": 1, "producto": "Huevo", "cantidad": 100, "fechaCaducidad": "2024-11-20", "mermas": 5},
    {"id": 2, "lote": 2, "producto": "Leche", "cantidad": 50, "fechaCaducidad": "2024-11-10", "mermas": 10}
]


###############
# * Ruta para el horneado de galletas
# Función para guardar y cargar datos (simulando una base de datos)
DATA_FILE = 'horneado_data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try:
                return json.load(f)
            except:
                return {"cookies_queue": [], "cookies_in_process": [], "finished_cookies": []}
    return {"cookies_queue": [], "cookies_in_process": [], "finished_cookies": []}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

# Tipos de galletas disponibles
cookie_types = ["Chocolate", "Vainilla", "Avena", "Mantequilla"]

@bp_production.route('/horneado', methods=['GET'])
def horneado():
    # Cargar datos
    data = load_data()
    
    # Obtener fecha actual para lotes
    current_date = datetime.now().strftime("%d%m%y")
    
    # Renderizar plantilla con datos
    return render_template(
        'produccion/hornear_galleta.html',
        cookies_queue=data['cookies_queue'],
        cookies_in_process=data['cookies_in_process'],
        finished_cookies=data['finished_cookies'],
        cookie_types=cookie_types,
        current_date=current_date
    )

@bp_production.route('/add_to_queue', methods=['POST'])
def add_to_queue():
    # Obtener tipo de galleta del formulario
    cookie_type = request.form.get('cookie_type')
    
    # Validar tipo de galleta
    if cookie_type not in cookie_types:
        flash('Tipo de galleta no válido', 'danger')
        return redirect(url_for('production.horneado'))
    
    # Cargar datos actuales
    data = load_data()
    
    # Generar ID para la galleta
    cookie_id = f"{cookie_type[0:2].upper()}{datetime.now().strftime('%d%m%y%H%M%S')}"
    
    # Agregar galleta a la cola
    data['cookies_queue'].append({
        'id': cookie_id,
        'type': cookie_type,
        'created_at': datetime.now().strftime("%H:%M:%S")
    })
    
    # Guardar datos
    save_data(data)
    
    flash(f'Galleta de {cookie_type} agregada a la cola', 'success')
    return redirect(url_for('production.horneado'))

@bp_production.route('/start_process/<cookie_id>', methods=['POST'])
def start_process(cookie_id):
    # Cargar datos actuales
    data = load_data()
    
    # Buscar galleta en la cola
    for i, cookie in enumerate(data['cookies_queue']):
        if cookie['id'] == cookie_id:
            # Mover galleta de la cola al proceso
            cookie_to_process = data['cookies_queue'].pop(i)
            cookie_to_process['process_started_at'] = datetime.now().strftime("%H:%M:%S")
            data['cookies_in_process'].append(cookie_to_process)
            
            # Guardar datos
            save_data(data)
            
            flash(f'Galleta de {cookie_to_process["type"]} movida a proceso', 'success')
            return redirect(url_for('production.horneado'))
    
    flash('Galleta no encontrada', 'danger')
    return redirect(url_for('production.horneado'))

@bp_production.route('/finish_process/<cookie_id>', methods=['POST'])
def finish_process(cookie_id):
    # Cargar datos actuales
    data = load_data()
    
    # Buscar galleta en proceso
    for i, cookie in enumerate(data['cookies_in_process']):
        if cookie['id'] == cookie_id:
            # Mover galleta del proceso a terminadas
            cookie_to_finish = data['cookies_in_process'].pop(i)
            cookie_to_finish['finished_at'] = datetime.now().strftime("%H:%M:%S")
            
            # Generar número de lote
            batch_number = f"{cookie_to_finish['type'][0:2].upper()}{datetime.now().strftime('%d%m%y')}"
            cookie_to_finish['batch'] = batch_number
            
            data['finished_cookies'].append(cookie_to_finish)
            
            # Guardar datos
            save_data(data)
            
            flash(f'Galleta de {cookie_to_finish["type"]} finalizada con éxito', 'success')
            return redirect(url_for('production.horneado'))
    
    flash('Galleta no encontrada', 'danger')
    return redirect(url_for('production.horneado'))

@bp_production.route('/delete_cookie', methods=['POST'])
def delete_cookie():
    cookie_id = request.form.get('cookie_id')
    list_type = request.form.get('list_type')
    
    # Cargar datos actuales
    data = load_data()
    
    # Seleccionar lista correcta
    if list_type == 'queue':
        target_list = data['cookies_queue']
        list_name = 'cookies_queue'
    elif list_type == 'process':
        target_list = data['cookies_in_process']
        list_name = 'cookies_in_process'
    elif list_type == 'finished':
        target_list = data['finished_cookies']
        list_name = 'finished_cookies'
    else:
        flash('Lista no válida', 'danger')
        return redirect(url_for('production.horneado'))
    
    # Buscar y eliminar la galleta
    for i, cookie in enumerate(target_list):
        if cookie['id'] == cookie_id:
            cookie_info = target_list[i]
            del data[list_name][i]
            
            # Guardar datos
            save_data(data)
            
            flash(f'Galleta de {cookie_info["type"]} eliminada', 'success')
            return redirect(url_for('production.horneado'))
    
    flash('Galleta no encontrada', 'danger')
    return redirect(url_for('production.horneado'))
#########################












