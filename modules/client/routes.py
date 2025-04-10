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
    
    if current_user.rol.nombreRol != 'Cliente':
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('shared.index'))
    
    try:
        # 1. Obtener pedidos del usuario usando SQL nativo
        pedidos_query = text("""
            SELECT idPedidos, estadoPedido, costoPedido, fechaPedido
            FROM pedidos
            WHERE idCliente = :user_id
            ORDER BY fechaPedido DESC
        """)
        pedidos_data = db.session.execute(pedidos_query, {'user_id': current_user.idUser}).fetchall()
        
        # Procesar los pedidos para el template
        pedidos = []
        for pedido in pedidos_data:
            pedidos.append({
                'id': pedido[0],
                'estado': pedido[1],
                'total': float(pedido[2]),
                'fecha': pedido[3].strftime('%Y-%m-%d')  # Formatear fecha como string
            })
        
        # 2. Obtener detalles usando tu vista SQL personalizada
        detalles_query = text("""
            SELECT 
                v.idUsuario AS 'ID Usuario',
                u.username AS 'Nombre Usuario',
                g.nombreGalleta AS 'Galleta',
                CASE 
                    WHEN dv.formaVenta = 'Por pieza' THEN 'Piezas'
                    WHEN dv.formaVenta = 'Por precio' THEN 'Gramos'
                    WHEN dv.formaVenta = 'Por paquete/caja' THEN 
                        CASE 
                            WHEN g.gramajeGalleta >= 700 THEN 'Caja 1kg'
                            ELSE 'Caja 700g'
                        END
                END AS 'Forma de Venta',
                CASE 
                    WHEN dv.formaVenta = 'Por pieza' THEN CONCAT(dv.cantidadGalletas, ' pz')
                    WHEN dv.formaVenta = 'Por precio' THEN CONCAT(dv.pesoGramos, ' gr')
                    WHEN dv.formaVenta = 'Por paquete/caja' THEN CONCAT(dv.cantidadGalletas, ' ', 
                        CASE 
                            WHEN g.gramajeGalleta >= 700 THEN 'cajas 1kg'
                            ELSE 'cajas 700g'
                        END)
                END AS 'Cantidad'
            FROM 
                detallesVentas dv
            JOIN 
                galletas g ON dv.idGalleta = g.idGalleta
            JOIN
                ventas v ON dv.idDetalleVenta = v.idDetalleVenta
            JOIN
                usuarios u ON v.idUsuario = u.idUser
            WHERE v.idUsuario = :user_id
        """)
        
        detalles_galletas = db.session.execute(detalles_query, {'user_id': current_user.idUser}).fetchall()
        
        print(f"Pedidos recuperados: {pedidos}")
        print(f"Detalles de galletas: {detalles_galletas}")
        
        return render_template('client/pedidos_cliente.html',
                            pedidos=pedidos,
                            detalles_galletas=detalles_galletas)
    
    except Exception as e:
        flash(f'Error al cargar pedidos: {str(e)}', 'danger')
        print(f"Error en la consulta: {str(e)}")
        return redirect(url_for('cliente.portal_cliente'))