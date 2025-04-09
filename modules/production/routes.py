from datetime import datetime
import os
from flask import abort, json, render_template, request, redirect, url_for, session, flash, jsonify
from .services import ProveedorService, GalletaService, InsumoService, RecetaService, HorneadoService, ProduccionService, UserService
from .models import db, Horneado
from modules.shared.models import User 
from flask_login import login_required, current_user
from . import bp_production
from database.conexion import db
from datetime import datetime, timedelta

# Inicialización de servicios
proveedor_service = ProveedorService(db.session)
galleta_service = GalletaService(db.session)
insumo_service = InsumoService(db.session)
receta_service = RecetaService(db.session)
horneado_service = HorneadoService(db.session)
produccion_service = ProduccionService(db.session)
user_service = UserService(db.session)

# Rutas para Proveedor
@bp_production.route('/proveedores', methods=['GET'])
@login_required
def get_all_proveedores():
    proveedores = proveedor_service.get_all_proveedores()
    return jsonify([proveedor.to_dict() for proveedor in proveedores])

@bp_production.route('/proveedor', methods=['POST'])
@login_required
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

# Rutas para Galleta
@bp_production.route('/galletas', methods=['GET'])
@login_required
def get_all_galletas():
    galletas = galleta_service.get_all_galletas()
    return jsonify([galleta.to_dict() for galleta in galletas])

@bp_production.route('/galleta', methods=['POST'])
@login_required
def add_galleta():
    data = request.get_json()
    nueva_galleta = galleta_service.add_galleta(
        data['nombre'],
        data['precio_unitario'],
        data['cantidad_disponible'],
        data['gramaje'],
        data['tipo_galleta'],
        data['fecha_anaquel'],
        data['fecha_final_anaquel']
    )
    if nueva_galleta:
        return jsonify(nueva_galleta.to_dict()), 201
    return jsonify({"error": "No se pudo agregar la galleta"}), 400

# Rutas para Insumo
@bp_production.route('/insumos', methods=['GET'])
@login_required
def get_all_insumos():
    insumos = insumo_service.get_all_insumos()
    return jsonify([insumo.to_dict() for insumo in insumos])

@bp_production.route('/insumo', methods=['POST'])
@login_required
def add_insumo():
    data = request.get_json()
    nuevo_insumo = insumo_service.add_insumo(
        data['nombre'],
        data['unidad'],
        data['cantidad_disponible'],
        data['cantidad_minima']
    )
    if nuevo_insumo:
        return jsonify(nuevo_insumo.to_dict()), 201
    return jsonify({"error": "No se pudo agregar el insumo"}), 400

# Rutas para Receta
@bp_production.route('/recetas', methods=['GET'])
@login_required
def get_all_recetas():
    recetas = receta_service.get_all_recetas()
    return jsonify([receta.to_dict(include_galleta=True) for receta in recetas])

@bp_production.route('/receta', methods=['POST'])
@login_required
def add_receta():
    data = request.get_json()
    nueva_receta = receta_service.add_receta(
        data['nombre'],
        data['instrucciones'],
        data['cantidad_producida'],
        data['galletTipo'],
        data['id_galleta']
    )
    if nueva_receta:
        return jsonify(nueva_receta.to_dict(include_galleta=True)), 201
    return jsonify({"error": "No se pudo agregar la receta"}), 400

# Rutas para Horneado
@bp_production.route('/horneados', methods=['GET'])
@login_required
def get_all_horneados():
    horneados = horneado_service.get_all_horneados()
    return jsonify([horneado.to_dict() for horneado in horneados])

@bp_production.route('/horneado', methods=['POST'])
@login_required
def horneado():
    data = request.get_json()
    nuevo_horneado = horneado_service.registrar_horneado(
        temperatura_horno=data['temperatura_horno'],
        tiempo_horneado=data['tiempo_horneado'],
        cantidad_producida=data['cantidad_producida'],
        observaciones=data.get('observaciones', ''),
        id_receta=data['id_receta'],
        id_usuario=current_user.idUser
    )
    if nuevo_horneado:
        return jsonify(nuevo_horneado.to_dict()), 201
    return jsonify({"error": "No se pudo registrar el horneado"}), 400

# Rutas para Producción
@bp_production.route('/producciones', methods=['GET'])
@login_required
def get_all_producciones():
    producciones = produccion_service.get_producciones()
    return jsonify([produccion.to_dict() for produccion in producciones])

# Rutas para Usuarios
@bp_production.route('/usuarios', methods=['GET'])
@login_required
def get_all_users():
    if current_user.rol.nombreRol != 'Administrador':
        return jsonify({"error": "No autorizado"}), 403
    users = user_service.get_all_users()
    return jsonify([{
        'id': user.idUser,
        'username': user.username,
        'rol': user.rol.nombreRol,
        'estado': user.estado
    } for user in users])

# Rutas para Dashboard
@bp_production.route('/dashboard_produccion')
@login_required
def dashboard_produccion():
    if current_user.rol.nombreRol not in ['Administrador', 'Produccion']:
        return redirect(url_for('shared.login'))
    
    # Obtener estadísticas para el dashboard
    estadisticas = horneado_service.get_estadisticas_horneado(30)
    producciones = produccion_service.get_producciones()
    
    return render_template('produccion/produccion.html',
                         estadisticas=estadisticas,
                         producciones=producciones)

@bp_production.route('/inventario')
@login_required
def inventario():
    insumos = insumo_service.get_all_insumos()
    return render_template('production/inventario.html', insumos=insumos)

@bp_production.route('/historial_horneados')
@login_required
def historial():
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    id_receta = request.args.get('id_receta')
    
    horneados = horneado_service.get_horneados_filtrados(fecha_inicio, fecha_fin, id_receta)
    recetas = receta_service.get_all_recetas()
    
    return render_template('production/historial_horneados.html',
                         horneados=horneados,
                         recetas=recetas)