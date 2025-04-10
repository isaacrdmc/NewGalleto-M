from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import bp_clientes
from .services import obtener_detalles_galletas
from .models import Pedido, DetallePedido
from modules.production.models import Galleta  # Importa desde production
from database.conexion import db

# Ruta para el dashboard del cliente
@bp_clientes.route('/portal_cliente')
@login_required
def portal_cliente():
    if current_user.rol.nombreRol not in ['Cliente']:
        flash('No tienes permisos para acceder a esta sección', 'danger')
        return redirect(url_for('shared.index'))
    return render_template('client/portal_cliente.html')

# Ruta para el perfil del cliente
@bp_clientes.route('/perfil')
@login_required
def perfil():
    if current_user.rol.nombreRol not in ['Cliente']:
        return redirect(url_for('shared.login'))
    return render_template('client/perfil_cliente.html', usuario=current_user)

@bp_clientes.route('/pedidos')
@login_required
def pedidos_cliente():
    if current_user.rol.nombreRol != 'Cliente':
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('shared.index'))
    
    try:
        # Consulta directa SQL compatible
        query = """
        SELECT p.*, dp.*, g.nombreGalleta 
        FROM pedidos p
        JOIN detallePedido dp ON p.idPedidos = dp.idPedido
        JOIN galletas g ON dp.idGalleta = g.idGalleta
        WHERE p.idCliente = :user_id
        ORDER BY p.fechaPedido DESC
        """
        pedidos_data = db.session.execute(query, {'user_id': current_user.idUser}).fetchall()
        
        # Procesamiento manual de resultados
        pedidos = []
        for pedido_data in pedidos_data:
            pedido = {
                'id': pedido_data[0],
                'fecha': pedido_data[3],
                'estado': pedido_data[1],
                'total': pedido_data[2],
                'detalles': []
            }
            pedidos.append(pedido)
        
        # Consulta para la vista de galletas
        detalles_galletas = db.session.execute("SELECT * FROM vista_detalles_galletas").fetchall()
        
        return render_template('client/pedidos_cliente.html',
                            pedidos=pedidos,
                            detalles_galletas=detalles_galletas)
    
    except Exception as e:
        flash(f'Error al cargar pedidos: {str(e)}', 'danger')
        return redirect(url_for('cliente.portal_cliente'))