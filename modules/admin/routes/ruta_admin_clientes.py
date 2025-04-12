from flask import render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user

from modules.admin.routes.ruta_admin_dashboard import admin_required
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
@admin_required
def clientes():
    lista_clientes = obtener_clientes()
    form = ClienteForm()
    return render_template('admin/clientes.html', clientes=lista_clientes, form=form)

@bp_admistracion.route('/clientes/agregar', methods=['POST'])
@admin_required
def agregar_cliente_route():
    try:
        data = request.get_json()
        
        if not all(key in data for key in ['username', 'password']):
            return jsonify({'error': 'Datos incompletos'}), 400
            
        nuevo_cliente = agregar_cliente(
            username=data['username'],
            password=data['password']
        )
        
        return jsonify({
            "mensaje": "Cliente agregado correctamente",
            "cliente": {
                "id": nuevo_cliente.idUser,
                "username": nuevo_cliente.username,
                "estado": nuevo_cliente.estado
            }
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp_admistracion.route('/clientes/editar/<int:id>', methods=['POST'])
@admin_required
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
        
        return jsonify({
            "mensaje": "Cliente actualizado correctamente",
            "cliente": {
                "id": cliente.idUser,
                "username": cliente.username,
                "estado": cliente.estado
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp_admistracion.route('/clientes/eliminar/<int:id>', methods=['POST'])
@admin_required
def eliminar_cliente_route(id):
    try:
        cliente = eliminar_cliente(id)
        return jsonify({
            "mensaje": "Cliente eliminado correctamente",
            "cliente": {
                "id": cliente.idUser,
                "username": cliente.username
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp_admistracion.route('/clientes/obtener/<int:id>')
@admin_required
def obtener_cliente(id):
    try:
        cliente = User.query.get_or_404(id)
        if cliente.idRol != 4:
            raise ValueError("El usuario no es un cliente")
            
        return jsonify({
            "id": cliente.idUser,
            "username": cliente.username,
            "estado": cliente.estado,
            "fechaRegistro": cliente.fechaRegistro.strftime('%Y-%m-%d %H:%M:%S') if cliente.fechaRegistro else None,
            "ultimoAcceso": cliente.ultimoAcceso.strftime('%Y-%m-%d %H:%M:%S') if cliente.ultimoAcceso else None
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@bp_admistracion.route('/clientes/pedidos/<int:id>')
@admin_required
def ver_pedidos_cliente(id):
    pedidos = obtener_pedidos_cliente(id)
    cliente = User.query.get_or_404(id)
    
    pedidos_data = []
    for pedido in pedidos:
        detalles = DetallePedido.query.filter_by(idPedido=pedido.idPedidos).all()
        items = []
        for detalle in detalles:
            galleta = Galleta.query.get(detalle.idGalleta)
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
    
    return render_template('admin/pedidos_cliente.html', cliente=cliente, pedidos=pedidos_data)