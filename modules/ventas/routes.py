from flask import abort, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime

from sqlalchemy import text

from modules.client.models import Pedido
from modules.production.models import Galleta, SolicitudHorneado

from . import bp_ventas
from modules.ventas.services import RecetaService, SolicitudHorneadoService, obtener_historial_ventas
from modules.ventas.models import Venta, DetalleVenta
from modules.ventas.services import obtener_pedidos_clientes
from database.conexion import db
from sqlalchemy.orm import joinedload

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
            "producto": d.galleta.nombre if d.galleta else "Producto desconocido",
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
            idUsuario=current_user.idUser
        )
        db.session.add(nueva_venta)
        db.session.flush()

        for d in detalles:
            forma = d['metodoVenta']
            cant = d['cantidad']
            precio = d['subtotal']
            idGalleta = d['idGalleta']

            detalle = DetalleVenta(
                idVenta=nueva_venta.idVenta,
                idGalleta=idGalleta,
                precioUnitario=precio,
                formaVenta='Por pieza' if forma == 'por pieza' else ('Por peso' if forma == 'Por gramo' else 'por paquete/caja'),
                cantGalletasVendidas=0  # Valor por defecto
            )

            if forma == 'por pieza':
                unidades = int(cant.split(' ')[0])
                detalle.cantGalletasVendidas = unidades
                detalle.cantidadGalletas = unidades
            elif forma == 'Por gramo':
                gramos = int(cant.replace('gr', '').strip())
                detalle.pesoGramos = gramos
                detalle.cantGalletasVendidas = 0  # Asegurar valor
            elif forma == 'Empacado':
                try:
                    if 'Caja' in cant:
                        partes = cant.split('Caja')
                        tipo = partes[1].strip() if len(partes) > 1 else ''
                        gramos = 1000 if '1kg' in tipo else 700
                    else:
                        gramos = 700  # valor por defecto si no se reconoce
                    detalle.pesoGramos = gramos
                    detalle.cantGalletasVendidas = 0
                except Exception as e:
                    raise ValueError(f"No se pudo procesar el campo empacado: {cant} — Error: {e}")
            # Descontar del inventario
            galleta = Galleta.query.get(idGalleta)
            if galleta:
                # Asegúrate de descontar las unidades correctas
                unidades_a_descontar = detalle.cantGalletasVendidas or 0
                if forma == 'Empacado':
                    # Para empaques, calcula unidades basadas en gramos y gramaje
                    gramaje = galleta.gramaje
                    unidades_a_descontar = gramos / gramaje
                galleta.cantidad_disponible -= unidades_a_descontar
                db.session.add(galleta)

            db.session.add(detalle)

        db.session.commit()
        return jsonify({"success": True})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    

# Solicitar horneado
@bp_ventas.route('/solicitar_horneado', methods=['GET'])
@ventas_required
def solicitar_horneado():
    receta_service = RecetaService(db.session)  # Crear instancia pasando la sesión
    recetas = receta_service.get_all_recetas()  # Llamar al método de instancia
    return render_template('ventas/solicitar_horneado.html', recetas=recetas)


# Procesar solicitud de horneado
@bp_ventas.route('/solicitar_horneado', methods=['POST'])
@ventas_required
def procesar_solicitud_horneado():
    try:
        id_receta = request.form.get('id_receta', type=int)
        cantidad_lotes = request.form.get('cantidad_lotes', type=int)
        
        if not all([id_receta, cantidad_lotes]):
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(url_for('ventas.solicitar_horneado'))  # Corregido el endpoint
        
        # Crear instancia del servicio
        horneado_service = SolicitudHorneadoService(db.session)
        
        # Llamar al método de instancia
        resultado = horneado_service.crear_solicitud(
            id_receta=id_receta,
            cantidad_lotes=cantidad_lotes,
            id_usuario=current_user.idUser
        )
        
        if resultado['success']:
            flash('Solicitud de horneado enviada exitosamente', 'success')
            return redirect(url_for('ventas.ver_mis_solicitudes'))  # Corregido el endpoint
        else:
            if 'insumos_faltantes' in resultado:
                flash('No hay suficientes insumos para completar la solicitud', 'danger')
            else:
                flash('Error al enviar la solicitud', 'danger')
            return redirect(url_for('ventas.solicitar_horneado'))  # Corregido el endpoint
    
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('ventas.solicitar_horneado'))  # Corregido el endpoint
    

# Ver mis solicitudes
@bp_ventas.route('/solicitudes/mis_solicitudes', methods=['GET'])
@ventas_required
def ver_mis_solicitudes():
    # Crear instancia del servicio pasando la sesión de la base de datos
    horneado_service = SolicitudHorneadoService(db.session)
    
    # Llamar al método de instancia correctamente
    solicitudes = horneado_service.get_solicitudes_usuario(current_user.idUser)
    
    return render_template('ventas/mis_solicitudes.html', solicitudes=solicitudes)


# Detalle de solicitud
@bp_ventas.route('/solicitud/detalle/<int:id_solicitud>', methods=['GET'])
@ventas_required
def detalle_solicitud(id_solicitud):
    solicitud = db.session.query(SolicitudHorneado)\
        .options(joinedload(SolicitudHorneado.receta))\
        .get(id_solicitud)
    
    if not solicitud:
        flash('Solicitud no encontrada', 'danger')
        return redirect(url_for('ventas.ver_mis_solicitudes'))
    
    
    # Calcular costos
    receta_service = RecetaService(db.session)  # Create an instance first
    costos = receta_service.calcular_costo_galleta(solicitud.id_receta)  # Then call the method
    


    # Verificar permisos (solicitante o aprobador)
    if solicitud.id_solicitante != current_user.idUser and \
       (solicitud.id_aprobador != current_user.idUser if solicitud.id_aprobador else True) and \
       current_user.rol.nombreRol not in ['Ventas']:
        abort(403)
    
    # Obtener detalles de insumos necesarios
    insumos = db.session.execute(
        text("""
            SELECT 
                i.idInsumo,
                i.nombre as nombre, 
                ir.cantidad as cantidad, 
                i.unidadInsumo as unidadInsumo, 
                i.cantidadDisponible as cantidadDisponible
            FROM ingredientesReceta ir
            JOIN insumos i ON ir.idInsumo = i.idInsumo
            WHERE ir.idReceta = :id_receta
        """),
        {'id_receta': solicitud.id_receta}
    ).fetchall()
    
    # Convertir resultado
    insumos_data = [{
        'id': i.idInsumo,
        'nombre': i.nombre,
        'cantidad': float(i.cantidad),
        'unidadInsumo': i.unidadInsumo,
        'cantidadDisponible': float(i.cantidadDisponible),
        'total_requerido': float(i.cantidad) * solicitud.cantidad_lotes
    } for i in insumos]
    
    return render_template(
        'ventas/detalle_solicitud.html',
        solicitud=solicitud,
        insumos=insumos_data,
        # cantidad_total=solicitud.cantidad_lotes * solicitud.receta.cantidad_producida
        cantidad_total=solicitud.cantidad_lotes * solicitud.receta.cantGalletasProduction,

        costos=costos  # Pasar los costos a la plantilla
    )
    
# Ruta para ver el inventario de galletas
@bp_ventas.route('/inventario-galletas')
@login_required
def inventario_galletas():
    # Obtener todas las galletas con stock > 0, ordenadas por cantidad descendente
    galletas = Galleta.query.filter(Galleta.cantidad_disponible > 0)\
                           .order_by(Galleta.cantidad_disponible.desc())\
                           .all()
    
    # Calcular días restantes para caducidad
    for galleta in galletas:
        dias_restantes = (galleta.fecha_final_anaquel - datetime.now().date()).days
        galleta.dias_restantes = max(0, dias_restantes)
    
    return render_template('ventas/inventario_galletas.html', 
                         galletas=galletas,
                         page_title="Inventario de Galletas")

# API para obtener galletas recién horneadas (últimas 24 horas)
@bp_ventas.route('/api/galletas-horneadas')
@login_required
def obtener_galletas_horneadas():
    # Obtener horneados de las últimas 24 horas
    fecha_limite = datetime.now() - timedelta(hours=24)
    
    horneados_recientes = db.session.query(
        Horneado.id_receta,
        Receta.nombre.label('nombre_galleta'),
        func.sum(Horneado.cantidad_producida).label('cantidad_producida')
    ).join(Receta, Horneado.id_receta == Receta.id)\
     .filter(Horneado.fecha_horneado >= fecha_limite)\
     .group_by(Horneado.id_receta, Receta.nombre)\
     .all()

    # Formatear respuesta
    resultado = []
    for hr in horneados_recientes:
        # Buscar la galleta asociada a esta receta
        galleta = Galleta.query.filter_by(id_receta=hr.id_receta).first()
        if galleta:
            resultado.append({
                'id': galleta.id,
                'nombre': galleta.nombre,
                'cantidad': hr.cantidad_producida,
                'cantidad_agregada': hr.cantidad_producida  # Puedes ajustar este cálculo
            })
    
    return jsonify(resultado)

# Ruta para actualizar el inventario desde el horno
@bp_ventas.route('/actualizar-inventario', methods=['POST'])
@login_required
def actualizar_inventario():
    try:
        data = request.get_json()
        
        # Obtener galletas horneadas recientemente (últimas 24 horas)
        fecha_limite = datetime.now() - timedelta(hours=24)
        horneados = Horneado.query.filter(Horneado.fecha_horneado >= fecha_limite).all()
        
        # Actualizar inventario para cada galleta
        for horneado in horneados:
            galleta = Galleta.query.filter_by(id_receta=horneado.id_receta).first()
            if galleta:
                galleta.cantidad_disponible += horneado.cantidad_producida
                db.session.add(galleta)
        
        # Registrar acción en el historial
        from modules.admin.models import HistorialAcciones
        historial = HistorialAcciones(
            accion="Actualización de inventario desde horno",
            modulo="Ventas",
            id_usuario=current_user.id,
            fecha=datetime.now()
        )
        db.session.add(historial)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Inventario actualizado correctamente',
            'galletas_actualizadas': len(horneados)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al actualizar inventario: {str(e)}'
        }), 500

# Ruta para buscar galletas (API)
@bp_ventas.route('/api/buscar-galletas')
@login_required
def buscar_galletas():
    query = request.args.get('q', '').lower()
    tipo = request.args.get('tipo', 'all')
    stock = request.args.get('stock', 'all')
    
    # Construir consulta base
    galletas_query = Galleta.query.filter(Galleta.cantidad_disponible > 0)
    
    # Aplicar filtros
    if query:
        galletas_query = galletas_query.filter(
            or_(
                Galleta.nombre.ilike(f'%{query}%'),
                Galleta.descripcion.ilike(f'%{query}%')
            )
        )
    
    if tipo != 'all':
        galletas_query = galletas_query.filter_by(tipo_galleta=tipo)
    
    if stock != 'all':
        if stock == 'low':
            galletas_query = galletas_query.filter(Galleta.cantidad_disponible < 50)
        elif stock == 'medium':
            galletas_query = galletas_query.filter(
                and_(
                    Galleta.cantidad_disponible >= 50,
                    Galleta.cantidad_disponible <= 100
                )
            )
        elif stock == 'high':
            galletas_query = galletas_query.filter(Galleta.cantidad_disponible > 100)
    
    # Ejecutar consulta y formatear resultados
    galletas = galletas_query.all()
    resultados = []
    
    for galleta in galletas:
        resultados.append({
            'id': galleta.id,
            'nombre': galleta.nombre,
            'imagen_url': galleta.imagen_url or url_for('static', filename='img/default-cookie.png'),
            'cantidad': galleta.cantidad_disponible,
            'precio': float(galleta.precio_unitario),
            'gramaje': float(galleta.gramaje),
            'tipo': galleta.tipo_galleta,
            'caducidad': galleta.fecha_final_anaquel.strftime('%d/%m/%Y'),
            'dias_restantes': (galleta.fecha_final_anaquel - datetime.now().date()).days
        })
    
    return jsonify(resultados)

# Ruta para detalles de una galleta
@bp_ventas.route('/galleta/<int:id_galleta>')
@login_required
def detalle_galleta(id_galleta):
    galleta = Galleta.query.get_or_404(id_galleta)
    
    # Calcular estadísticas de ventas recientes
    ventas_recientes = db.session.query(
        func.sum(DetalleVenta.cantGalletasVendidas).label('total_vendido')
    ).join(Venta).filter(
        DetalleVenta.idGalleta == id_galleta,
        Venta.fechaVentaGalleta >= (datetime.now() - timedelta(days=7))
    ).scalar() or 0
    
    return render_template('ventas/detalle_galleta.html',
                         galleta=galleta,
                         ventas_semana=ventas_recientes,
                         page_title=f"Detalles de {galleta.nombre}")