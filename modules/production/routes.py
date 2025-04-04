from datetime import datetime
import os
from flask import abort, json, render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
from .services import ProveedorService, GalletaService, InsumoService, RecetaService
from .models import db
#  ~ Importamos el archvio con el nombre del Blueprint para la sección
from flask_login import login_required, current_user
from . import bp_production


# Servicios
proveedor_service = ProveedorService(db.session)
galleta_service = GalletaService(db.session)
insumo_service = InsumoService(db.session)
receta_service = RecetaService(db.session)

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

@bp_production.route('/proveedor/<int:id>', methods=['GET'])
@login_required
def get_proveedor(id):
    proveedor = proveedor_service.get_proveedor(id)
    if proveedor:
        return jsonify(proveedor.to_dict())
    return jsonify({"error": "Proveedor no encontrado"}), 404

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
@login_required
def get_galleta(id):
    galleta = galleta_service.get_galleta(id)
    if galleta:
        return jsonify(galleta.to_dict())
    return jsonify({"error": "Galleta no encontrada"}), 404

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
        data['unidadInsumo'],  # Este nombre se mantiene igual porque viene del cliente
        data['cantidadDisponible'],  # Este nombre se mantiene igual porque viene del cliente
        data['cantidadMinima']  # Este nombre se mantiene igual porque viene del cliente
    )
    if nuevo_insumo:
        return jsonify(nuevo_insumo.to_dict()), 201
    return jsonify({"error": "No se pudo agregar el insumo"}), 400

@bp_production.route('/insumo/<int:id>', methods=['GET'])
@login_required
def get_insumo(id):
    insumo = insumo_service.get_insumo(id)
    if insumo:
        return jsonify(insumo.to_dict())
    return jsonify({"error": "Insumo no encontrado"}), 404

# Rutas para Receta
@bp_production.route('/recetas', methods=['GET'])
@login_required
def get_all_recetas():
    recetas = receta_service.get_all_recetas()
    return jsonify([receta.to_dict() for receta in recetas])

@bp_production.route('/receta', methods=['POST'])
@login_required
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
@login_required
def get_receta(id):
    receta = receta_service.get_receta(id)
    if receta:
        return jsonify(receta.to_dict())
    return jsonify({"error": "Receta no encontrada"}), 404

@bp_production.route('/inventario', methods=['GET'])
@login_required
def inventario():
    # Obtener todos los insumos desde el servicio
    insumos = insumo_service.get_all_insumos()
    
    # Pasar los insumos al template
    return render_template('produccion/inventario_insumos.html', inventario=insumos)

@bp_production.route('/insumo/detalle/<string:nombre_insumo>', methods=['GET'])
@login_required
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
@login_required
def dashboard_produccion():
    if current_user.rol.nombreRol != 'Produccion':
        return redirect(url_for('shared.login'))
    return render_template('produccion/produccion.html')

@bp_production.route('/horneado', methods=['GET'])
@login_required
def horneado():
    return render_template('hornear_galleta.html')
