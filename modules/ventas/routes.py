from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash,check_password_hash
#  ~ Importamos el archvio con el nombre del Blueprint para la sección
from . import bp_ventas
from modules.ventas.services import obtener_historial_ventas
from modules.ventas.models import Venta
from modules.ventas.services import obtener_pedidos_clientes
from modules.ventas.models import Pedido

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
            "producto": d.galleta.nombreGalleta if d.galleta else "Producto desconocido",
            "cantidad": d.cantGalletasVendidas,  # Mantener el valor numérico para cálculos
            "cantidad_formateada": cantidad_formateada,  # Nueva propiedad con formato
            "precio_unitario": float(d.galleta.precioUnitario),
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
    from modules.ventas.models import Galleta

    galletas = Galleta.query.with_entities(Galleta.idGalleta, Galleta.nombreGalleta).all()
    lista = [{"id": g.idGalleta, "nombre": g.nombreGalleta} for g in galletas]
    return jsonify(lista)

@bp_ventas.route('/galleta/<int:id_galleta>')
def obtener_info_galleta(id_galleta):
    from modules.ventas.models import Galleta

    galleta = Galleta.query.get(id_galleta)
    if not galleta:
        return jsonify({"success": False}), 404

    return jsonify({
        "success": True,
        "cantidadDisponible": galleta.cantidadDisponible,
        "gramaje": float(galleta.gramajeGalleta),
        "precio": float(galleta.precioUnitario)
    })
    
@bp_ventas.route('/registrar_venta', methods=['POST'])
def registrar_venta():
    from modules.ventas.models import Venta, DetalleVenta, Galleta
    import datetime

    if 'user_id' not in session:
        return jsonify({"success": False, "message": "No autenticado"}), 401

    data = request.get_json()
    detalles = data.get('detalles')
    total = data.get('total')

    if not detalles or total is None:
        return jsonify({"success": False, "message": "Datos incompletos"}), 400

    try:
        nueva_venta = Venta(
            fechaVentaGalleta=datetime.date.today(),
            totalVenta=total,
            idUsuario=session['user_id']  # Asegúrate que guardas el idUser en sesión
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
                detalle.cantGalletasVendidas = 0  # si quieres usarlo como total
            elif forma == 'Empacado':
                cajas, tipo = cant.split(' Caja ')
                gramos = 1000 if '1kg' in tipo else 700
                detalle.pesoGramos = gramos
                detalle.cantGalletasVendidas = 0

            # Descontar del inventario
            galleta = Galleta.query.get(idGalleta)
            if galleta:
                galleta.cantidadDisponible -= detalle.cantGalletasVendidas or 0
                db.session.add(galleta)

            db.session.add(detalle)

        db.session.commit()
        return jsonify({"success": True})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500