from flask import render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from ..services import (
    obtener_recetas, obtener_receta, agregar_receta, 
    actualizar_receta, eliminar_receta, obtener_galletas,
    obtener_horneados_receta, obtener_ingredientes_receta,
    agregar_ingrediente_receta, eliminar_ingrediente_receta
)
from ..forms.recetas import RecetaForm
from ...admin import bp_admistracion
from ...production.models import Galleta, Receta
from datetime import datetime

@bp_admistracion.route('/recetas')
@login_required
def recetas():
    if current_user.rol.nombreRol != 'Administrador':
        return redirect(url_for('shared.login'))
    
    recetas = obtener_recetas()
    galletas = obtener_galletas()
    timestamp = int(datetime.now().timestamp())  # Añade esto
    return render_template('admin/recetas.html', 
                         recetas=recetas, 
                         galletas=galletas,
                         timestamp=timestamp)

@bp_admistracion.route('/recetas/nueva', methods=['POST'])
@login_required
def nueva_receta():
    if current_user.rol.nombreRol != 'Administrador':
        return jsonify({'success': False, 'error': 'No autorizado'}), 403
    
    try:
        data = {
            'nombre': request.form.get('nombre'),
            'instrucciones': request.form.get('instrucciones'),
            'cantidad_producida': int(request.form.get('cantidad_producida')),
            'galletTipo': int(request.form.get('galletTipo')),
            'id_galleta': int(request.form.get('id_galleta'))
        }
        
        # Validaciones básicas
        if data['cantidad_producida'] <= 0:
            return jsonify({'success': False, 'error': 'La cantidad producida debe ser mayor a 0'}), 400
        
        if data['galletTipo'] < 0:
            return jsonify({'success': False, 'error': 'El tipo de galleta no puede ser negativo'}), 400
        
        imagen = request.files.get('imagen')
        receta = agregar_receta(data, imagen)
        
        return jsonify({
            'success': True,
            'mensaje': 'Receta creada exitosamente!',
            'receta': receta.to_dict(include_galleta=True),
            'imagen_url': receta.imagen_url  # Asegúrate de devolver esto
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al crear receta: {str(e)}'
        }), 400
    

@bp_admistracion.route('/recetas/<int:id_receta>')
@login_required
def detalle_receta(id_receta):
    if current_user.rol.nombreRol != 'Administrador':
        return redirect(url_for('shared.login'))
    
    receta = obtener_receta(id_receta)
    horneados = obtener_horneados_receta(id_receta)
    ingredientes = obtener_ingredientes_receta(id_receta)
    
    return render_template('admin/detalle_receta.html', 
                         receta=receta, 
                         horneados=horneados,
                         ingredientes=ingredientes)


@bp_admistracion.route('/recetas/obtener/<int:id_receta>')
@login_required
def obtener_receta_para_edicion(id_receta):
    try:
        receta = obtener_receta(id_receta)  # Esto ya es un diccionario
        return jsonify({
            'success': True,
            'receta': receta  # No necesitamos to_dict() aquí
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    

@bp_admistracion.route('/recetas/editar/<int:id_receta>', methods=['POST'])
@login_required
def editar_receta(id_receta):
    if current_user.rol.nombreRol != 'Administrador':
        return jsonify({'success': False, 'error': 'No autorizado'}), 403
    
    try:
        data = {
            'nombre': request.form.get('nombre'),
            'instrucciones': request.form.get('instrucciones'),
            'cantidad_producida': int(request.form.get('cantidad_producida')),
            'galletTipo': int(request.form.get('galletTipo')),
            'id_galleta': int(request.form.get('id_galleta'))
        }
        
        # Validaciones básicas
        if data['cantidad_producida'] <= 0:
            return jsonify({'success': False, 'error': 'La cantidad producida debe ser mayor a 0'}), 400
        
        if data['galletTipo'] < 0:
            return jsonify({'success': False, 'error': 'El tipo de galleta no puede ser negativo'}), 400
        
        imagen = request.files.get('imagen')
        receta = actualizar_receta(id_receta, data, imagen)
        
        return jsonify({
            'success': True,
            'mensaje': 'Receta actualizada exitosamente!',
            'receta': receta.to_dict(include_galleta=True),
            'imagen_url': receta.imagen_url  # Asegúrate de devolver esto
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al actualizar receta: {str(e)}'
        }), 400
    

@bp_admistracion.route('/recetas/<int:id_receta>/eliminar', methods=['POST'])
@login_required
def eliminar_receta_route(id_receta):
    try:
        if current_user.rol.nombreRol != 'Administrador':
            return jsonify({'success': False, 'error': 'No autorizado'}), 403
            
        eliminar_receta(id_receta)
        return jsonify({
            'success': True,
            'mensaje': 'Receta eliminada exitosamente!'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    

@bp_admistracion.route('/recetas/ingredientes/agregar', methods=['POST'])
@login_required
def agregar_ingrediente():
    try:
        data = request.get_json()
        ingrediente = agregar_ingrediente_receta(
            id_receta=data['id_receta'],
            id_insumo=data['id_insumo'],
            cantidad=data['cantidad']
        )
        return jsonify({
            'success': True,
            'ingrediente': {
                'id': ingrediente.idIngredienteReceta,
                'nombre': ingrediente.insumo.nombre,
                'cantidad': ingrediente.cantidad
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp_admistracion.route('/recetas/ingredientes/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_ingrediente(id):
    try:
        eliminar_ingrediente_receta(id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    

@bp_admistracion.route('/recetas/listar')
@login_required
def listar_recetas():
    try:
        if current_user.rol.nombreRol != 'Administrador':
            return jsonify({'error': 'No autorizado'}), 403
            
        recetas = obtener_recetas()
        return jsonify([r.to_dict(include_galleta=True) for r in Receta.query.join(Galleta).order_by(Receta.id.desc()).all()])
    except Exception as e:
        return jsonify({'error': str(e)}), 500