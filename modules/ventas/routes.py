from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash,check_password_hash
#  ~ Importamos el archvio con el nombre del Blueprint para la sección
from . import bp_ventas
from modules.ventas.services import obtener_historial_ventas
from modules.ventas.models import Venta

# ? Ahora vamos a definir las rutas necesarias para el bluprint

# ^ Sección del vendedor

# Ruta para el dashboard de ventas
@bp_ventas.route('/prod_ventas')
def prod_ventas():
    if 'username' not in session or session['role'] != 'ventas':
        return redirect(url_for('shared.login'))
    return render_template('ventas/prod_term.html')

@bp_ventas.route('/historial_ventas')
def historial_ventas():
    if 'username' not in session or session['role'] != 'ventas':
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
        detalles.append({
            "producto": d.galleta.nombreGalleta if d.galleta else "Producto desconocido",
            "cantidad": d.cantGalletasVendidas,
            "precio_unitario": float(d.precioUnitario),
            "forma_venta": d.formaVenta,
            "subtotal": float(d.precioUnitario * d.cantGalletasVendidas)
        })

    return jsonify({"success": True, "detalles": detalles})

@bp_ventas.route('/pedidos_clientes')
def pedidos_clientes():
    if 'username' not in session or session['role'] != 'ventas':
        return redirect(url_for('shared.login'))
    return render_template('ventas/pedidos_clientes.html')