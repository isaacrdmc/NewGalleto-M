from flask import current_app, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from ..services import (agregar_cliente, obtener_clientes, actualizar_cliente, 
                       eliminar_cliente, obtener_pedidos_cliente)
from ..forms.clientes import ClienteForm
from ...admin import bp_admistracion
from ...shared.models import User
from ...client.models import Pedido, DetallePedido
from ...ventas.models import Venta, DetalleVenta
from ...production.models import Galleta
from sqlalchemy import desc
from database.conexion import db

@bp_admistracion.route('/clientes')
@login_required
def clientes():
    if current_user.rol.nombreRol != 'Administrador':
        current_app.logger.warning(f'Intento de acceso no autorizado a la página de clientes por {current_user.username}')
        return redirect(url_for('shared.login'))
    
    lista_clientes = obtener_clientes()
    form = ClienteForm()
    current_app.logger.info(f'Acceso a la página de clientes por {current_user.username}')
    return render_template('admin/clientes.html', clientes=lista_clientes, form=form)


@bp_admistracion.route('/clientes/agregar', methods=['POST'])
@login_required
def agregar_cliente_route():
    try:
        data = request.get_json()
        
        if not all(key in data for key in ['username', 'password']):
            return jsonify({'error': 'Datos incompletos'}), 400
            
        nuevo_cliente = agregar_cliente(
            username=data['username'],
            password=data['password']
            # No pasar estado aquí si no es necesario
        )
        
        # Opcional: Actualizar el estado después si es diferente del default
        if 'estado' in data:
            nuevo_cliente.estado = data['estado']
            db.session.commit()

        
        # current_app.logger.info(f'Cliente {cu} agregado correctamente por {current_user.username}')
        current_app.logger.info(f'Cliente {nuevo_cliente.username} agregado correctamente por {current_user.username}')
        
        return jsonify({
            "mensaje": "Cliente agregado correctamente",
            "cliente": {
                "id": nuevo_cliente.idUser,
                "username": nuevo_cliente.username,
                "estado": nuevo_cliente.estado
            }
        }), 201        
    except Exception as e:
        current_app.logger.error(f'Error al agregar cliente: {str(e)}')
        return jsonify({"error": str(e)}), 500

@bp_admistracion.route('/clientes/editar/<int:id>', methods=['POST'])
@login_required
def editar_cliente(id):
    try:
        data = request.get_json()
        
        if not all(key in data for key in ['username', 'estado']):
            return jsonify({'error': 'Datos incompletos'}), 400
            
        cliente = actualizar_cliente(
            cliente_id=id,
            username=data['username'],
            estado=data['estado']
        )

        current_app.logger.info(f'Cliente {cliente.username} editado correctamente por {current_user.username}')
        
        return jsonify({
            "mensaje": "Cliente actualizado correctamente",
            "cliente": {
                "id": cliente.idUser,
                "username": cliente.username,
                "estado": cliente.estado
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'Error al editar el cliente: {str(e)}')
        return jsonify({"error": str(e)}), 500

@bp_admistracion.route('/clientes/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_cliente_route(id):
    try:
        cliente = eliminar_cliente(id)
        current_app.logger.info(f'Cliente {cliente.username} eliminado correctamente po {current_user.username}')
        return jsonify({
            "mensaje": "Cliente eliminado correctamente",
            "cliente": {
                "id": cliente.idUser,
                "username": cliente.username
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f'Error al eliminar el cliente: {str(e)}')
        return jsonify({"error": str(e)}), 500

@bp_admistracion.route('/clientes/obtener/<int:id>')
@login_required
def obtener_cliente(id):
    try:
        cliente = User.query.get_or_404(id)
        if cliente.idRol != 4:
            current_app.logger.warning(f'Acceso no autorizado a la información del cliente {cliente.username} por {current_user.username}')
            raise ValueError("El usuario no es un cliente")
            
        current_app.looger.info(f'Acceso a la información del cliente {cliente.username} por {current_user.username}')

        return jsonify({
            "id": cliente.idUser,
            "username": cliente.username,
            "estado": cliente.estado,
            "fechaRegistro": cliente.fechaRegistro.strftime('%Y-%m-%d %H:%M:%S') if cliente.fechaRegistro else None,
            "ultimoAcceso": cliente.ultimoAcceso.strftime('%Y-%m-%d %H:%M:%S') if cliente.ultimoAcceso else None
        }), 200
    
    except Exception as e:
        current_app.logger.error(f'Error al obtener el cliente: {str(e)}')        
        return jsonify({"error": str(e)}), 404




# TODO Falta el logger de esta ruta
@bp_admistracion.route('/clientes/pedidos/<int:id>')
@login_required
def ver_pedidos_cliente(id):
    if current_user.rol.nombreRol != 'Administrador':
        current_app.logger.warning(f'Intento de acceso no autorizado a la página de pedidos por {current_user.username}')
        return redirect(url_for('shared.login'))
    
    pedidos = obtener_pedidos_cliente(id)
    cliente = User.query.get_or_404(id)
    
    pedidos_data = []
    for pedido in pedidos:
        detalles = DetallePedido.query.filter_by(idPedido=pedido.idPedidos).all()
        items = []
        for detalle in detalles:
            galleta = Galleta.query.get(detalle.idGalleta)  # Obtener la galleta directamente
            items.append({
                'galleta': galleta.nombre,
                'cantidad': detalle.cantidad,
                'precio_unitario': detalle.precioUnitario,
                'subtotal': detalle.subtotal
            })
        
        pedidos_data.append({
            'id': pedido.idPedidos,
            'fecha': pedido.fechaPedido.strftime('%d/%m/%Y %H:%M'),
            'estado': pedido.estadoPedido,
            'total': pedido.costoPedido,
            'items': items
        })
    
    current_app.logger.info(f'Acceso a los pedidos del cliente {cliente.username} por {current_user.username}')
    return render_template('admin/pedidos_cliente.html', cliente=cliente, pedidos=pedidos_data)