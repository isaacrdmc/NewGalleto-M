from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import bp_clientes
from .services import obtener_detalles_galletas
from .models import Pedido, DetallePedido
from modules.production.models import Galleta  # Importa desde production
from database.conexion import db
from sqlalchemy.sql import text

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
    print("Accediendo a la ruta '/pedidos'")
    print(f"Usuario autenticado: {current_user.is_authenticated}")
    print(f"Rol del usuario: {current_user.rol.nombreRol}")
    
    if len(current_user.rol.nombreRol) > 0:
        print(f"Hay usuario")
    
    if current_user.rol.nombreRol != 'Cliente':
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('shared.index'))
    
    print('intentando hacer query')
    
    # Usar `text()` para envolver el query SQL de los pedidos
    query = text("""
        SELECT p.*, dp.*, g.nombreGalleta 
        FROM pedidos p
        JOIN detallePedido dp ON p.idPedidos = dp.idPedido
        JOIN galletas g ON dp.idGalleta = g.idGalleta
        WHERE p.idCliente = :user_id
        ORDER BY p.fechaPedido DESC
    """)
    
    try:
        print('Intentando recuperar datos')
        print(f'User id: {current_user.idUser}')
        # Ejecutar el query de los pedidos con el parámetro user_id
        pedidos_data = db.session.execute(query, {'user_id': current_user.idUser}).fetchall()
        
        # Verifica los datos obtenidos
        print(f"Pedidos recuperados: {pedidos_data}")
        
        # Procesamiento manual de resultados de los pedidos
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
        
        # Usar `text()` para envolver la consulta de vista_detalles_galletas
        detalles_galletas_query = text("SELECT * FROM vista_detalles_galletas")
        
        # Ejecutar el query de detalles de galletas
        detalles_galletas = db.session.execute(detalles_galletas_query).fetchall()
        
        # Imprimir los detalles de galletas para depuración
        print(f"Detalles de galletas: {detalles_galletas}")
        
        return render_template('client/pedidos_cliente.html',
                            pedidos=pedidos,
                            detalles_galletas=detalles_galletas)
    
    except Exception as e:
        flash(f'Error al cargar pedidos: {str(e)}', 'danger')
        print(f"No jalo el query: {str(e)}")
        return redirect(url_for('cliente.portal_cliente'))