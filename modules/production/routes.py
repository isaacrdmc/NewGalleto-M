from datetime import datetime
import os
from flask import abort, json, render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
from .services import ProveedorService, GalletaService, InsumoService, RecetaService,HorneadoService
from .models import db,Horneado
#  ~ Importamos el archvio con el nombre del Blueprint para la sección
from . import bp_production
from database.conexion import db
from datetime import datetime, timedelta

# Servicios
proveedor_service = ProveedorService(db.session)
galleta_service = GalletaService(db.session)
insumo_service = InsumoService(db.session)
receta_service = RecetaService(db.session)

# Rutas para Proveedor
@bp_production.route('/proveedores', methods=['GET'])
def get_all_proveedores():
    proveedores = proveedor_service.get_all_proveedores()
    return jsonify([proveedor.to_dict() for proveedor in proveedores])

@bp_production.route('/proveedor', methods=['POST'])
def add_proveedor():
    data = request.get_json()
    nuevo_proveedor = proveedor_service.add_proveedor(
        data['nombre'],
        data['telefono'],
        data['correo'],
        data['direccion'],
        data['productosProveedor']
    )
    if nuevo_proveedor:
        return jsonify(nuevo_proveedor.to_dict()), 201
    return jsonify({"error": "No se pudo agregar el proveedor"}), 400

@bp_production.route('/proveedor/<int:id>', methods=['GET'])
def get_proveedor(id):
    proveedor = proveedor_service.get_proveedor(id)
    if proveedor:
        return jsonify(proveedor.to_dict())
    return jsonify({"error": "Proveedor no encontrado"}), 404

# Rutas para Galleta
@bp_production.route('/galletas', methods=['GET'])
def get_all_galletas():
    galletas = galleta_service.get_all_galletas()
    return jsonify([galleta.to_dict() for galleta in galletas])

@bp_production.route('/galleta', methods=['POST'])
def add_galleta():
    data = request.get_json()
    nueva_galleta = galleta_service.add_galleta(
        data['nombreGalleta'],
        data['precioUnitario'],
        data['cantidadDisponible'],
        data['gramajeGalleta'],
        data['tipoGalleta'],
        data['fechaAnaquel'],
        data['fechaFinalAnaquel']
    )
    if nueva_galleta:
        return jsonify(nueva_galleta.to_dict()), 201
    return jsonify({"error": "No se pudo agregar la galleta"}), 400

@bp_production.route('/galleta/<int:id>', methods=['GET'])
def get_galleta(id):
    galleta = galleta_service.get_galleta(id)
    if galleta:
        return jsonify(galleta.to_dict())
    return jsonify({"error": "Galleta no encontrada"}), 404

# Rutas para Insumo
@bp_production.route('/insumos', methods=['GET'])
def get_all_insumos():
    insumos = insumo_service.get_all_insumos()
    return jsonify([insumo.to_dict() for insumo in insumos])

@bp_production.route('/insumo', methods=['POST'])
def add_insumo():
    data = request.get_json()
    nuevo_insumo = insumo_service.add_insumo(
        data['nombre'],
        data['unidadInsumo'],  # Este nombre se mantiene igual porque viene del cliente
        data['cantidadDisponible'],  # Este nombre se mantiene igual porque viene del cliente
        data['cantidadMinima']  # Este nombre se mantiene igual porque viene del cliente
    )
    if nuevo_insumo:
        return jsonify(nuevo_insumo.to_dict()), 201
    return jsonify({"error": "No se pudo agregar el insumo"}), 400

@bp_production.route('/insumo/<int:id>', methods=['GET'])
def get_insumo(id):
    insumo = insumo_service.get_insumo(id)
    if insumo:
        return jsonify(insumo.to_dict())
    return jsonify({"error": "Insumo no encontrado"}), 404

# Rutas para Receta
@bp_production.route('/recetas', methods=['GET'])
def get_all_recetas():
    recetas = receta_service.get_all_recetas()
    return jsonify([receta.to_dict() for receta in recetas])

@bp_production.route('/receta', methods=['POST'])
def add_receta():
    data = request.get_json()
    nueva_receta = receta_service.add_receta(
        data['nombreReceta'],
        data['instruccionReceta'],
        data['cantGalletasProduction'],
        data['galletTipo'],
        data['idGalleta']
    )
    if nueva_receta:
        return jsonify(nueva_receta.to_dict()), 201
    return jsonify({"error": "No se pudo agregar la receta"}), 400

@bp_production.route('/receta/<int:id>', methods=['GET'])
def get_receta(id):
    receta = receta_service.get_receta(id)
    if receta:
        return jsonify(receta.to_dict())
    return jsonify({"error": "Receta no encontrada"}), 404

@bp_production.route('/inventario', methods=['GET'])
def inventario():
    # Obtener todos los insumos desde el servicio
    insumos = insumo_service.get_all_insumos()
    
    # Pasar los insumos al template
    return render_template('produccion/inventario_insumos.html', inventario=insumos)

@bp_production.route('/insumo/detalle/<string:nombre_insumo>', methods=['GET'])
def detalle_insumo(nombre_insumo):
    # Obtener el insumo según su nombre
    insumo = insumo_service.get_insumo_por_nombre(nombre_insumo)
    
    if insumo:
        # Pasar los detalles del insumo al template
        return render_template('detalle_insumo.html', insumo=insumo)
    else:
        flash("Insumo no encontrado", "error")
        return redirect(url_for('production.inventario'))
    

@bp_production.route('/dashboard_produccion')
def dashboard_produccion():
    if 'username' not in session or session['role'] != 'produccion':
        return redirect(url_for('shared.login'))
    return render_template('produccion/produccion.html')

# Añadir a routes.py

# Instanciamos el servicio de horneado
horneado_service = HorneadoService(db.session)

@bp_production.route('/historial', methods=['GET'])
def historial():
    # Obtener parámetros de filtrado
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    id_receta = request.args.get('receta')
    
    # Convertir id_receta a entero si existe
    if id_receta:
        try:
            id_receta = int(id_receta)
        except ValueError:
            id_receta = None
    
    # Obtener los horneados filtrados
    horneados = horneado_service.get_horneados_filtrados(fecha_inicio, fecha_fin, id_receta)
    
    # Obtener todas las recetas para el filtro
    recetas = receta_service.get_all_recetas()
    
    # Renderizar el template con los datos
    return render_template(
        'produccion/historial_horneada.html',
        horneados=horneados,
        recetas=recetas
    )

@bp_production.route('/estadisticas_horneado', methods=['GET'])
def estadisticas_horneado():
    # Obtener parámetro de días a consultar (por defecto 30 días)
    dias = request.args.get('dias', 30, type=int)
    
    # Obtener estadísticas
    estadisticas = horneado_service.get_estadisticas_horneado(dias)
    
    # Devolver en formato JSON para ser consumido por ajax
    return jsonify(estadisticas)

@bp_production.route('/horneado', methods=['GET'])
def horneado():
    # Obtener todas las recetas para el selector
    recetas = receta_service.get_all_recetas()
    return render_template('produccion/hornear_galleta.html', recetas=recetas)

@bp_production.route('/registrar_horneado', methods=['POST'])
def registrar_horneado():
    try:
        # Obtener datos del formulario
        id_receta = request.form.get('id_receta', type=int)
        temperatura = request.form.get('temperatura', type=int)
        tiempo = request.form.get('tiempo', type=int)
        cantidad = request.form.get('cantidad', type=int)
        observaciones = request.form.get('observaciones', '')
        
        # Validar datos
        if not all([id_receta, temperatura, tiempo, cantidad]):
            flash('Todos los campos son obligatorios excepto observaciones', 'danger')
            return redirect(url_for('production.horneado'))
        
        # Obtener id del usuario de la sesión
        id_usuario = session.get('user_id')
        if not id_usuario:
            flash('Debes iniciar sesión para registrar horneados', 'danger')
            return redirect(url_for('shared.login'))
        
        # Registrar horneado usando el servicio
        resultado = horneado_service.registrar_horneado(
            temperatura,
            tiempo,
            cantidad,
            observaciones,
            id_receta,
            id_usuario
        )
        
        if resultado:
            flash('Horneado registrado exitosamente', 'success')
        else:
            flash('Error al registrar el horneado', 'danger')
        
        return redirect(url_for('production.horneado'))
    
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('production.horneado'))

@bp_production.route('/detalle_horneado/<int:id_horneado>', methods=['GET'])
def detalle_horneado(id_horneado):
    # Obtener el horneado por ID
    horneado = horneado_service.get_horneado(id_horneado)
    
    if not horneado:
        flash('Horneado no encontrado', 'danger')
        return redirect(url_for('production.historial'))
    
    # Renderizar template con los detalles
    return render_template('produccion/detalle_horneado.html', horneado=horneado)