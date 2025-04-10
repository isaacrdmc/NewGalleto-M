from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import login_required, current_user

from modules.client.models import Pedido
from modules.production.models import Galleta
from . import bp_ventas
from modules.ventas.services import obtener_historial_ventas
from modules.ventas.models import Venta
from modules.ventas.services import obtener_pedidos_clientes


# ? Ahora vamos a definir las rutas necesarias para el bluprint

# ^ Sección del vendedor

# Ruta para el dashboard de ventas
@bp_ventas.route('/prod_ventas')
def ventas():
    if current_user.rol.nombreRol not in ['Ventas']:
        return redirect(url_for('shared.login'))
    return render_template('ventas/prod_term.html')

@bp_ventas.route('/historial_ventas')
def historial_ventas():
    if current_user.rol.nombreRol not in ['Ventas']:
        return redirect(url_for('shared.login'))

    ventas = obtener_historial_ventas()
    return render_template('ventas/historial_ventas.html', ventas=ventas)

@bp_ventas.route('/detalles/<int:id_venta>')
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
            "cantidad": d.cantGalletasVendidas,  # Mantener el valor numérico para cálculos
            "cantidad_formateada": cantidad_formateada,  # Nueva propiedad con formato
            "precio_unitario": float(d.galleta.precio_unitario),
            "forma_venta": d.formaVenta,
            "subtotal": float(d.precioUnitario)
        })

    return jsonify({"success": True, "detalles": detalles})

@bp_ventas.route('/pedidos_clientes')
def pedidos_clientes():
    if 'username' not in session or session['role'] != 'ventas':
        return redirect(url_for('shared.login'))
    
    pedidos = obtener_pedidos_clientes()
    return render_template('ventas/pedidos_clientes.html', pedidos=pedidos)

@bp_ventas.route('/pedidos_clientes/detalles/<int:id_pedido>')
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

@bp_ventas.route('/galletas_disponibles')
def galletas_disponibles():
    
    galletas = Galleta.query.with_entities(Galleta.id, Galleta.nombre).all()
    lista = [{"id": g.id, "nombre": g.nombre} for g in galletas]
    return jsonify(lista)

@bp_ventas.route('/galleta/<int:id_galleta>')
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