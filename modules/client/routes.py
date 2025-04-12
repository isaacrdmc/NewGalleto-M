from datetime import datetime
from flask import render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps

from modules.shared.models import User
from . import bp_clientes
from .services import obtener_detalles_galletas
from .models import Pedido, DetallePedido
from modules.production.models import Galleta
from database.conexion import db

# Decorador personalizado para validar rol de Cliente
def cliente_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Por favor inicie sesión para acceder a esta página', 'warning')
            return redirect(url_for('shared.login', next=request.url))
        
        if current_user.rol.nombreRol != 'Cliente':
            flash('No tiene permisos para acceder a esta sección', 'danger')
            return redirect(url_for('shared.index'))
        
        return f(*args, **kwargs)
    return decorated_function

# Portal del cliente
@bp_clientes.route('/portal_cliente')
@cliente_required
def portal_cliente():
    # Obtener información relevante para el dashboard del cliente
    ultimos_pedidos = Pedido.query.filter_by(
        idCliente=current_user.idUser
    ).order_by(
        Pedido.fechaPedido.desc()
    ).limit(3).all()
    
    # Obtener galletas destacadas
    galletas_destacadas = Galleta.query.order_by(
        Galleta.cantidad_disponible.desc()
    ).limit(4).all()
    
    return render_template(
        'client/portal_cliente.html',
        ultimos_pedidos=ultimos_pedidos,
        galletas_destacadas=galletas_destacadas
    )

# Perfil del cliente
@bp_clientes.route('/perfil')
@cliente_required
def perfil():
    # Obtener información del cliente
    pedidos_totales = Pedido.query.filter_by(
        idCliente=current_user.idUser
    ).count()
    
    return render_template(
        'client/perfil_cliente.html',
        usuario=current_user,
        pedidos_totales=pedidos_totales
    )

# Lista de pedidos del cliente
@bp_clientes.route('/pedidos')
@cliente_required
def pedidos_cliente():
    # Obtener todos los pedidos del cliente actual
    pedidos = Pedido.query.filter_by(
        idCliente=current_user.idUser
    ).order_by(
        Pedido.fechaPedido.desc()
    ).all()
    
    detalles_galletas = obtener_detalles_galletas()
    
    return render_template(
        'client/pedidos_cliente.html',
        pedidos=pedidos,
        detalles_galletas=detalles_galletas
    )

# Detalle de un pedido específico
@bp_clientes.route('/pedido/detalle/<int:id_pedido>')
@cliente_required
def detalle_pedido(id_pedido):
    # Verificar que el pedido pertenece al cliente actual
    pedido = Pedido.query.filter_by(
        idPedidos=id_pedido,
        idCliente=current_user.idUser
    ).first()
    
    if not pedido:
        flash('Pedido no encontrado', 'danger')
        return redirect(url_for('client.pedidos_cliente'))
    
    # Obtener detalles del pedido
    detalles = DetallePedido.query.filter_by(
        idPedido=id_pedido
    ).all()
    
    # Obtener información de las galletas
    items = []
    for detalle in detalles:
        galleta = Galleta.query.get(detalle.idGalleta)
        items.append({
            'galleta': galleta.nombre,
            'cantidad': detalle.cantidad,
            'precio_unitario': detalle.precioUnitario,
            'subtotal': detalle.subtotal,
            'imagen': galleta.imagen_url if hasattr(galleta, 'imagen_url') else None
        })
    
    return render_template(
        'client/detalle_pedido.html',
        pedido=pedido,
        items=items
    )

# Crear nuevo pedido
@bp_clientes.route('/pedido/nuevo', methods=['POST'])
@cliente_required
def crear_pedido():
    try:
        data = request.get_json()
        
        if not data or 'items' not in data:
            return jsonify({
                'success': False,
                'message': 'Datos del pedido incompletos'
            }), 400
        
        # Validar items del pedido
        items_validos = []
        total = 0.0
        
        for item in data['items']:
            galleta = Galleta.query.get(item.get('id_galleta'))
            
            if not galleta:
                return jsonify({
                    'success': False,
                    'message': f'Galleta con ID {item.get("id_galleta")} no encontrada'
                }), 404
                
            cantidad = int(item.get('cantidad', 0))
            if cantidad <= 0:
                return jsonify({
                    'success': False,
                    'message': 'La cantidad debe ser mayor a cero'
                }), 400
                
            if galleta.cantidad_disponible < cantidad:
                return jsonify({
                    'success': False,
                    'message': f'No hay suficiente stock de {galleta.nombre}'
                }), 400
                
            subtotal = cantidad * galleta.precio_unitario
            total += subtotal
            
            items_validos.append({
                'galleta': galleta,
                'cantidad': cantidad,
                'subtotal': subtotal
            })
        
        # Crear el pedido en la base de datos
        nuevo_pedido = Pedido(
            fechaPedido=datetime.now(),
            estadoPedido='Pendiente',
            costoPedido=total,
            idCliente=current_user.idUser
        )
        
        db.session.add(nuevo_pedido)
        db.session.flush()  # Para obtener el ID del nuevo pedido
        
        # Agregar los detalles del pedido
        for item in items_validos:
            detalle = DetallePedido(
                idPedido=nuevo_pedido.idPedidos,
                idGalleta=item['galleta'].id,
                cantidad=item['cantidad'],
                precioUnitario=item['galleta'].precio_unitario,
                subtotal=item['subtotal']
            )
            db.session.add(detalle)
            
            # Actualizar el inventario
            item['galleta'].cantidad_disponible -= item['cantidad']
            db.session.add(item['galleta'])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Pedido creado exitosamente',
            'pedido_id': nuevo_pedido.idPedidos
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al crear el pedido: {str(e)}'
        }), 500

# Cancelar pedido
@bp_clientes.route('/pedido/cancelar/<int:id_pedido>', methods=['POST'])
@cliente_required
def cancelar_pedido(id_pedido):
    try:
        # Verificar que el pedido pertenece al cliente actual
        pedido = Pedido.query.filter_by(
            idPedidos=id_pedido,
            idCliente=current_user.idUser
        ).first()
        
        if not pedido:
            flash('Pedido no encontrado', 'danger')
            return redirect(url_for('client.pedidos_cliente'))
        
        # Solo se pueden cancelar pedidos pendientes
        if pedido.estadoPedido != 'Pendiente':
            flash('Solo se pueden cancelar pedidos en estado Pendiente', 'warning')
            return redirect(url_for('client.detalle_pedido', id_pedido=id_pedido))
        
        # Cambiar estado del pedido
        pedido.estadoPedido = 'Cancelado'
        
        # Devolver productos al inventario
        detalles = DetallePedido.query.filter_by(idPedido=id_pedido).all()
        for detalle in detalles:
            galleta = Galleta.query.get(detalle.idGalleta)
            galleta.cantidad_disponible += detalle.cantidad
            db.session.add(galleta)
        
        db.session.commit()
        
        flash('Pedido cancelado exitosamente', 'success')
        return redirect(url_for('client.detalle_pedido', id_pedido=id_pedido))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al cancelar el pedido: {str(e)}', 'danger')
        return redirect(url_for('client.detalle_pedido', id_pedido=id_pedido))

# Actualizar perfil del cliente
@bp_clientes.route('/perfil/actualizar', methods=['POST'])
@cliente_required
def actualizar_perfil():
    try:
        # Obtener datos del formulario
        nuevo_username = request.form.get('username', '').strip()
        nueva_password = request.form.get('password', '')
        confirmar_password = request.form.get('confirm_password', '')
        
        # Validaciones básicas
        if not nuevo_username:
            flash('El nombre de usuario es requerido', 'danger')
            return redirect(url_for('client.perfil'))
        
        # Verificar si el nuevo username ya existe (excluyendo al usuario actual)
        if User.query.filter(User.username == nuevo_username, User.idUser != current_user.idUser).first():
            flash('El nombre de usuario ya está en uso', 'danger')
            return redirect(url_for('client.perfil'))
        
        # Actualizar username
        current_user.username = nuevo_username
        
        # Actualizar contraseña si se proporcionó
        if nueva_password:
            if nueva_password != confirmar_password:
                flash('Las contraseñas no coinciden', 'danger')
                return redirect(url_for('client.perfil'))
            
            if len(nueva_password) < 8:
                flash('La contraseña debe tener al menos 8 caracteres', 'danger')
                return redirect(url_for('client.perfil'))
            
            current_user.set_password(nueva_password)
        
        db.session.commit()
        flash('Perfil actualizado exitosamente', 'success')
        return redirect(url_for('client.perfil'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar el perfil: {str(e)}', 'danger')
        return redirect(url_for('client.perfil'))

# Obtener galletas disponibles (API)
@bp_clientes.route('/api/galletas')
@cliente_required
def api_galletas():
    galletas = Galleta.query.filter(
        Galleta.cantidad_disponible > 0
    ).with_entities(
        Galleta.id,
        Galleta.nombre,
        Galleta.precio_unitario,
        Galleta.descripcion,
        Galleta.imagen_url
    ).all()
    
    galletas_data = [{
        'id': g.id,
        'nombre': g.nombre,
        'precio': float(g.precio_unitario),
        'descripcion': g.descripcion,
        'imagen': g.imagen_url,
        'disponible': True
    } for g in galletas]
    
    return jsonify(galletas_data)

# Verificar estado de un pedido (API)
@bp_clientes.route('/api/pedido/<int:id_pedido>')
@cliente_required
def api_estado_pedido(id_pedido):
    pedido = Pedido.query.filter_by(
        idPedidos=id_pedido,
        idCliente=current_user.idUser
    ).first()
    
    if not pedido:
        return jsonify({
            'success': False,
            'message': 'Pedido no encontrado'
        }), 404
    
    return jsonify({
        'success': True,
        'pedido': {
            'id': pedido.idPedidos,
            'estado': pedido.estadoPedido,
            'fecha': pedido.fechaPedido.strftime('%Y-%m-%d %H:%M:%S'),
            'total': float(pedido.costoPedido)
        }
    })