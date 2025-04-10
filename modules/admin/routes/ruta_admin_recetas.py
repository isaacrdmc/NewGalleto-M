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
from ...production.models import Galleta

@bp_admistracion.route('/recetas')
@login_required
def recetas():
    if current_user.rol.nombreRol != 'Administrador':
        return redirect(url_for('shared.login'))
    
    recetas = obtener_recetas()
    galletas = obtener_galletas()
    return render_template('admin/recetas.html', recetas=recetas, galletas=galletas)

@bp_admistracion.route('/recetas/nueva', methods=['GET', 'POST'])
@login_required
def nueva_receta():
    if current_user.rol.nombreRol != 'Administrador':
        return redirect(url_for('shared.login'))
    
    form = RecetaForm()
    form.id_galleta.choices = [(g.idGalleta, g.nombreGalleta) for g in obtener_galletas()]
    
    if request.method == 'POST' and form.validate():
        try:
            data = {
                'nombre': form.nombre.data,
                'instrucciones': form.instrucciones.data,
                'cantidad_producida': form.cantidad_producida.data,
                'galletTipo': form.galletTipo.data,
                'id_galleta': form.id_galleta.data
            }
            
            imagen = request.files.get('imagen')
            receta = agregar_receta(data, imagen)
            return jsonify({
                'success': True,
                'mensaje': 'Receta creada exitosamente!',
                'receta': receta.to_dict(include_galleta=True)
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Error al crear receta: {str(e)}'
            }), 400
    
    return render_template('admin/form_receta.html', form=form)

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

@bp_admistracion.route('/recetas/editar/<int:id_receta>', methods=['POST'])
@login_required
def editar_receta(id_receta):
    try:
        data = {
            'nombre': request.form.get('nombre'),
            'instrucciones': request.form.get('instrucciones'),
            'cantidad_producida': int(request.form.get('cantidad_producida')),
            'galletTipo': request.form.get('galletTipo'),
            'id_galleta': int(request.form.get('id_galleta'))
        }
        
        imagen = request.files.get('imagen')
        receta = actualizar_receta(id_receta, data, imagen)
        return jsonify({
            'success': True,
            'mensaje': 'Receta actualizada exitosamente!',
            'receta': receta.to_dict(include_galleta=True)
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