from flask import render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime

from modules.client.models import Pedido
from modules.production.models import Galleta
from . import bp_ventas
from modules.ventas.services import obtener_historial_ventas
from modules.ventas.models import Venta, DetalleVenta
from modules.ventas.services import obtener_pedidos_clientes
from database.conexion import db

# Decorador personalizado para validar rol de Ventas
def ventas_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Por favor inicie sesión para acceder a esta página', 'warning')
            return redirect(url_for('shared.login', next=request.url))
        
        if current_user.rol.nombreRol != 'Ventas':
            flash('No tiene permisos para acceder a esta sección', 'danger')
            return redirect(url_for('shared.index'))
        
        return f(*args, **kwargs)
    return decorated_function

# Ruta para el dashboard de ventas
@bp_ventas.route('/prod_ventas')
@ventas_required
def ventas():
    return render_template('ventas/prod_term.html')

# Ruta para el historial de ventas
@bp_ventas.route('/historial_ventas')
@ventas_required
def historial_ventas():
    ventas = obtener_historial_ventas()
    return render_template('ventas/historial_ventas.html', ventas=ventas)

# Ruta para obtener detalles de una venta específica
@bp_ventas.route('/detalles/<int:id_venta>')
@ventas_required
def obtener_detalles_venta(id_venta):
    venta = Venta.query.get(id_venta)

    if not venta or not venta.detalles:
        return jsonify({"success": False, "mensaje": "Venta no encontrada o sin detalles"}), 404

    detalles = []
    for d in venta.detalles:
        # Formateo de cantidad según forma de venta
        if d.formaVenta == "Por pieza":
            cantidad_formateada = f"{d.cantGalletasVendidas} galletas"
        elif d.formaVenta == "Por peso":
            cantidad_formateada = f"{d.pesoGramos}gr"
        elif d.formaVenta in ["Por paquete/caja", "por paquete/caja"]:
            if d.pesoGramos == 1000:
                cantidad_formateada = "Caja de 1kg"
            elif d.pesoGramos == 700:
                cantidad_formateada = "Caja de 700gr"
            else:
                cantidad_formateada = f"Paquete de {d.pesoGramos}gr"
        else:
            cantidad_formateada = str(d.cantGalletasVendidas)

        detalles.append({
            "producto": d.galleta.nombre if d.galleta else "Producto desconocido",
            "cantidad": d.cantGalletasVendidas,
            "cantidad_formateada": cantidad_formateada,
            "precio_unitario": float(d.galleta.precio_unitario),
            "forma_venta": d.formaVenta,
            "subtotal": float(d.precioUnitario)
        })

    return jsonify({"success": True, "detalles": detalles})

# Ruta para ver pedidos de clientes
@bp_ventas.route('/pedidos_clientes')
@ventas_required
def pedidos_clientes():
    pedidos = obtener_pedidos_clientes()
    return render_template('ventas/pedidos_clientes.html', pedidos=pedidos)

# Ruta para detalles de un pedido específico
@bp_ventas.route('/pedidos_clientes/detalles/<int:id_pedido>')
@ventas_required
def obtener_detalles_pedido(id_pedido):
    pedido = Pedido.query.get(id_pedido)

    if not pedido or not pedido.detalles:
        return jsonify({"success": False, "mensaje": "Pedido no encontrado o sin detalles"}), 404

    detalles = []
    for d in pedido.detalles:
        detalles.append({
            "producto": d.galleta.nombreGalleta if d.galleta else "Producto desconocido",
            "cantidad": d.cantidad,
            "precio_unitario": float(d.precioUnitario),
            "subtotal": float(d.subtotal)
        })

    return jsonify({"success": True, "detalles": detalles})

# Ruta para obtener galletas disponibles
@bp_ventas.route('/galletas_disponibles')
@ventas_required
def galletas_disponibles():
    galletas = Galleta.query.with_entities(Galleta.id, Galleta.nombre).all()
    lista = [{"id": g.id, "nombre": g.nombre} for g in galletas]
    return jsonify(lista)

# Ruta para obtener información de una galleta específica
@bp_ventas.route('/galleta/<int:id_galleta>')
@ventas_required
def obtener_info_galleta(id_galleta):
    galleta = Galleta.query.get(id_galleta)
    if not galleta:
        return jsonify({"success": False}), 404

    return jsonify({
        "success": True,
        "cantidadDisponible": galleta.cantidad_disponible,
        "gramaje": float(galleta.gramaje),
        "precio": float(galleta.precio_unitario)
    })
    
# Ruta para registrar una nueva venta
@bp_ventas.route('/registrar_venta', methods=['POST'])
@ventas_required
def registrar_venta():
    from modules.ventas.models import Venta, DetalleVenta
    import datetime

    data = request.get_json()
    detalles = data.get('detalles')
    total = data.get('total')

    if not detalles or total is None:
        return jsonify({"success": False, "message": "Datos incompletos"}), 400

    try:
        nueva_venta = Venta(
            fechaVentaGalleta=datetime.date.today(),
            totalVenta=total,
            idUsuario=current_user.idUser  # Usamos el ID del usuario actual
        )
        db.session.add(nueva_venta)
        db.session.flush()  # Para obtener nueva_venta.idVenta

        for d in detalles:
            forma = d['metodoVenta']
            cant = d['cantidad']
            precio = d['subtotal']
            idGalleta = d['idGalleta']

            detalle = DetalleVenta(
                idVenta=nueva_venta.idVenta,
                idGalleta=idGalleta,
                precioUnitario=precio,
                formaVenta='Por pieza' if forma == 'Por unidad' else ('Por peso' if forma == 'Por gramo' else 'por paquete/caja'),
            )

            if forma == 'Por unidad':
                unidades = int(cant.split(' ')[0])
                detalle.cantGalletasVendidas = unidades
                detalle.cantidadGalletas = unidades
            elif forma == 'Por gramo':
                gramos = int(cant.replace('gr', '').strip())
                detalle.pesoGramos = gramos
                detalle.cantGalletasVendidas = 0
            elif forma == 'Empacado':
                cajas, tipo = cant.split(' Caja ')
                gramos = 1000 if '1kg' in tipo else 700
                detalle.pesoGramos = gramos
                detalle.cantGalletasVendidas = 0

            # Descontar del inventario
            galleta = Galleta.query.get(idGalleta)
            if galleta:
                galleta.cantidad_disponible -= detalle.cantGalletasVendidas or 0
                db.session.add(galleta)

            db.session.add(detalle)

        db.session.commit()
        return jsonify({"success": True})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500