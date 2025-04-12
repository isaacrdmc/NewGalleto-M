from datetime import datetime
import os
from flask import abort, json, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from .services import FACTORES_CONVERSION, UNIDADES_COMPATIBLES, ProveedorService, GalletaService, InsumoService, RecetaService, HorneadoService, CompraService, SolicitudHorneadoService
from .models import Receta, SolicitudHorneado, Horneado, Insumo, Merma
from modules.admin.models import DetalleCompraInsumo, Proveedores as Proveedor, TransaccionCompra
from sqlalchemy import desc, func, text
from . import bp_production
from database.conexion import db
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload

# Decorador personalizado para validar rol de Producción
def production_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Por favor inicie sesión para acceder a esta página', 'warning')
            return redirect(url_for('shared.login', next=request.url))
        
        if current_user.rol.nombreRol != 'Produccion':
            flash('No tiene permisos para acceder a esta sección', 'danger')
            return redirect(url_for('shared.index'))
        
        return f(*args, **kwargs)
    return decorated_function

# Inicialización de servicios
proveedor_service = ProveedorService(db.session)
galleta_service = GalletaService(db.session)
insumo_service = InsumoService(db.session)
receta_service = RecetaService(db.session)
horneado_service = HorneadoService(db.session)
compra_service = CompraService(db.session)
solicitud_horneado_service = SolicitudHorneadoService(db.session)

# Dashboard de producción
@bp_production.route('/dashboard_produccion')
@production_required
def dashboard_produccion():
    # Obtener producción diaria
    produccion_diaria = db.session.query(
        func.sum(Horneado.cantidad_producida)
    ).filter(
        func.date(Horneado.fecha_horneado) == datetime.now().date()
    ).scalar() or 0

    # Obtener lotes pendientes
    lotes_pendientes = db.session.query(
        func.count(SolicitudHorneado.id)
    ).filter(
        SolicitudHorneado.estado == 'Aprobada'
    ).scalar() or 0

    # Obtener producciones recientes
    producciones_recientes = db.session.query(
        Horneado,
        SolicitudHorneado,
        Receta
    ).outerjoin(
        SolicitudHorneado, Horneado.id == SolicitudHorneado.id_horneado
    ).join(
        Receta, Horneado.id_receta == Receta.id
    ).order_by(
        Horneado.fecha_horneado.desc()
    ).limit(5).all()

    # Preparar datos para la tabla
    producciones_data = []
    for horneado, solicitud, receta in producciones_recientes:
        estado = "Completado"
        if solicitud:
            estado = solicitud.estado
            
        producciones_data.append({
            'id': horneado.id,
            'receta': receta.nombre,
            'cantidad': horneado.cantidad_producida,
            'estado': estado,
            'fecha': horneado.fecha_horneado.strftime('%Y-%m-%d')
        })

    return render_template(
        'produccion/produccion.html',
        produccion_diaria=produccion_diaria,
        lotes_pendientes=lotes_pendientes,
        producciones_recientes=producciones_data,
        now=datetime.now()
    )

# Historial de producción
@bp_production.route('/historial', methods=['GET'])
@production_required
def historial():
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    id_receta = request.args.get('receta')
    
    if id_receta:
        try:
            id_receta = int(id_receta)
        except ValueError:
            id_receta = None
    
    horneados = horneado_service.get_horneados_filtrados(fecha_inicio, fecha_fin, id_receta)
    recetas = receta_service.get_all_recetas()
    
    return render_template(
        'produccion/historial_horneada.html',
        horneados=horneados,
        recetas=recetas
    )

# Estadísticas de horneado
@bp_production.route('/estadisticas_horneado', methods=['GET'])
@production_required
def estadisticas_horneado():
    dias = request.args.get('dias', 30, type=int)
    estadisticas = horneado_service.get_estadisticas_horneado(dias)
    return jsonify(estadisticas)

# Vista para horneado
@bp_production.route('/horneado', methods=['GET'])
@production_required
def horneado():
    recetas = receta_service.get_all_recetas()
    return render_template('produccion/hornear_galleta.html', recetas=recetas)

# Registrar horneado
@bp_production.route('/registrar_horneado', methods=['POST'])
@production_required
def registrar_horneado():
    try:
        id_receta = request.form.get('id_receta', type=int)
        temperatura = request.form.get('temperatura', type=int)
        tiempo = request.form.get('tiempo', type=int)
        cantidad = request.form.get('cantidad', type=int)
        observaciones = request.form.get('observaciones', '')

        if not all([id_receta, temperatura, tiempo, cantidad]):
            flash('Todos los campos son obligatorios excepto observaciones', 'danger')
            return redirect(url_for('production.horneado'))

        resultado = horneado_service.registrar_horneado(
            temperatura,
            tiempo,
            cantidad,
            observaciones,
            id_receta,
            current_user.idUser  # Usar el ID del usuario actual
        )

        if resultado:
            flash('Horneado registrado exitosamente', 'success')
        else:
            flash('Error al registrar el horneado', 'danger')

        return redirect(url_for('production.horneado'))

    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('production.horneado'))

# Gestión de inventario
@bp_production.route('/inventario', methods=['GET'])
@production_required
def inventario():
    insumos = insumo_service.get_all_insumos()
    return render_template('produccion/inventario_insumos.html', inventario=insumos)

# Detalle de insumo
@bp_production.route('/insumo/detalle/<int:id_insumo>', methods=['GET'])
@production_required
def detalle_insumo(id_insumo):
    insumo = insumo_service.get_insumo(id_insumo)
    
    if not insumo:
        flash("Insumo no encontrado", "error")
        return redirect(url_for('production.inventario'))
    
    # Obtener lotes del insumo
    lotes = db.session.query(
        DetalleCompraInsumo,
        TransaccionCompra.fechaCompra,
        Proveedor.nombre.label('proveedor_nombre')
    ).join(
        TransaccionCompra, DetalleCompraInsumo.idCompra == TransaccionCompra.idTransaccionCompra
    ).join(
        Proveedor, TransaccionCompra.idProveedor == Proveedor.idProveedores
    ).filter(
        DetalleCompraInsumo.idInsumo == id_insumo
    ).order_by(
        DetalleCompraInsumo.fechaCaducidad
    ).all()
    
    # Preparar datos de lotes
    lotes_data = []
    lotes_proximos_caducar = []
    fecha_limite = datetime.now().date() + timedelta(days=7)
    
    for lote, fecha_compra, proveedor_nombre in lotes:
        lote_data = {
            'id': lote.idetalleCompraInsumo,
            'cant_cajas': lote.cantCajas,
            'cant_unidades_caja': lote.cantUnidadesXcaja,
            'cant_merma_unidad': lote.cantMermaPorUnidad,
            'costo_caja': float(lote.CostoPorCaja),
            'costo_unidad_caja': float(lote.costoUnidadXcaja),
            'unidad_insumo': lote.unidadInsumo,
            'fecha_registro': lote.fechaRegistro.strftime('%Y-%m-%d'),
            'fecha_caducidad': lote.fechaCaducidad.strftime('%Y-%m-%d'),
            'fecha_compra': fecha_compra.strftime('%Y-%m-%d'),
            'proveedor_nombre': proveedor_nombre,
            'is_expiring_soon': lote.fechaCaducidad <= fecha_limite
        }
        
        lotes_data.append(lote_data)
        
        if lote_data['is_expiring_soon']:
            lotes_proximos_caducar.append(lote_data)
    
    proveedores = proveedor_service.get_all_proveedores()
    
    return render_template('produccion/detalle_insumo.html', 
                         insumo=insumo, 
                         lotes=lotes_data,
                         lotes_proximos_caducar=lotes_proximos_caducar,
                         proveedores=proveedores)

# Registrar compra de insumo
@bp_production.route('/insumo/compra', methods=['POST'])
@production_required
def registrar_compra_insumo():
    try:
        id_insumo = request.form.get('id_insumo', type=int)
        id_proveedor_str = request.form.get('id_proveedor')
        unidad_compra = request.form.get('unidad_compra')
        cant_cajas = request.form.get('cant_cajas', type=int)
        cant_unidades_caja = request.form.get('cant_unidades_caja', type=int)
        costo_caja = request.form.get('costo_caja', type=float)
        fecha_caducidad = request.form.get('fecha_caducidad')
        
        # Validaciones básicas
        if not id_proveedor_str:
            flash('Debe seleccionar un proveedor', 'danger')
            return redirect(url_for('production.detalle_insumo', id_insumo=id_insumo))
        
        if not unidad_compra:
            flash('Debe seleccionar una unidad de compra', 'danger')
            return redirect(url_for('production.detalle_insumo', id_insumo=id_insumo))
            
        id_proveedor = int(id_proveedor_str)
        
        if not all([id_insumo, id_proveedor, cant_cajas, cant_unidades_caja, costo_caja, fecha_caducidad]):
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(url_for('production.detalle_insumo', id_insumo=id_insumo))
        
        # Obtener el insumo
        insumo = insumo_service.get_insumo(id_insumo)
        if not insumo:
            flash('Insumo no encontrado', 'danger')
            return redirect(url_for('production.inventario'))
        
        unidad_base = insumo.unidad
        
        # Validar compatibilidad de unidades
        if unidad_compra not in UNIDADES_COMPATIBLES.get(unidad_base, []):
            unidades_permitidas = ", ".join(UNIDADES_COMPATIBLES[unidad_base])
            flash(f'Unidad de compra no compatible. Para {unidad_base} las unidades permitidas son: {unidades_permitidas}', 'danger')
            return redirect(url_for('production.detalle_insumo', id_insumo=id_insumo))
        
        # Convertir unidades si es necesario
        conversion = 1.0
        if unidad_compra != unidad_base:
            conversion = FACTORES_CONVERSION.get((unidad_compra, unidad_base), 1.0)
            cant_unidades_caja = int(cant_unidades_caja * conversion)
        
        # Registrar la compra
        id_transaccion = compra_service.registrar_compra(id_proveedor)
        
        if not id_transaccion:
            flash('Error al registrar la transacción de compra', 'danger')
            return redirect(url_for('production.detalle_insumo', id_insumo=id_insumo))
        
        # Registrar el detalle de la compra
        cant_merma_unidad = 0
        fecha_registro = datetime.now().date()
        
        resultado = compra_service.agregar_detalle_compra(
            id_transaccion,
            id_insumo,
            cant_cajas,
            cant_unidades_caja,
            cant_merma_unidad,
            costo_caja,
            insumo.unidad,
            fecha_registro,
            datetime.strptime(fecha_caducidad, '%Y-%m-%d').date()
        )
        
        if resultado:
            flash('Compra registrada exitosamente', 'success')
        else:
            flash('Error al registrar el detalle de la compra', 'danger')
        
        return redirect(url_for('production.detalle_insumo', id_insumo=id_insumo))
        
    except Exception as e:
        flash(f'Error inesperado: {str(e)}', 'danger')
        return redirect(url_for('production.detalle_insumo', id_insumo=id_insumo if 'id_insumo' in locals() else 0))

# Registrar merma de insumo
@bp_production.route('/insumo/merma', methods=['POST'])
@production_required
def registrar_merma():
    try:
        id_insumo = request.form.get('id_insumo', type=int)
        id_lote = request.form.get('id_lote', type=int)
        tipoMerma = request.form.get('tipo_merma')
        cantidad_merma = request.form.get('cantidad_merma', type=int)
        unidad_merma = request.form.get('unidad_merma')
        
        # Validar datos
        if not all([id_insumo, tipoMerma, cantidad_merma, unidad_merma]):
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(url_for('production.detalle_insumo', id_insumo=id_insumo))
        
        # Crear registro de merma
        merma = Merma(
            tipoMerma=tipoMerma,
            unidadMerma=unidad_merma,
            cantidadMerma=cantidad_merma,
            fechaMerma=datetime.now().date(),
            idInsumo=id_insumo
        )
        
        # Agregar y guardar la merma
        db.session.add(merma)
        
        # Actualizar cantidad disponible del insumo
        insumo = insumo_service.get_insumo(id_insumo)
        if insumo and insumo.cantidad_disponible >= cantidad_merma:
            insumo.cantidad_disponible -= cantidad_merma
            
            # Si la cantidad llega a estar por debajo del mínimo, crear notificación
            if insumo.cantidad_disponible < insumo.cantidad_minima:
                from .models import Notificacion
                
                notificacion = Notificacion(
                    tipo='Bajo Inventario',
                    mensaje=f'El insumo {insumo.nombre} está por debajo del nivel mínimo requerido',
                    fecha_creacion=datetime.now(),
                    estatus='Nueva',
                    id_insumo=id_insumo
                )
                
                db.session.add(notificacion)
        
        db.session.commit()
        flash('Merma registrada exitosamente', 'success')
        
        return redirect(url_for('production.detalle_insumo', id_insumo=id_insumo))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('production.detalle_insumo', id_insumo=id_insumo if 'id_insumo' in locals() else 0))

# Solicitar horneado
@bp_production.route('/solicitar_horneado', methods=['GET'])
@production_required
def solicitar_horneado():
    recetas = receta_service.get_all_recetas()
    return render_template('ventas/solicitar_horneado.html', recetas=recetas)

# Procesar solicitud de horneado
@bp_production.route('/solicitar_horneado', methods=['POST'])
@production_required
def procesar_solicitud_horneado():
    try:
        id_receta = request.form.get('id_receta', type=int)
        cantidad_lotes = request.form.get('cantidad_lotes', type=int)
        
        if not all([id_receta, cantidad_lotes]):
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(url_for('production.solicitar_horneado'))
        
        resultado = solicitud_horneado_service.crear_solicitud(
            id_receta,
            cantidad_lotes,
            current_user.idUser
        )
        
        if resultado['success']:
            flash('Solicitud de horneado enviada exitosamente', 'success')
            return redirect(url_for('production.ver_mis_solicitudes'))
        else:
            if 'insumos_faltantes' in resultado:
                flash('No hay suficientes insumos para completar la solicitud', 'danger')
            else:
                flash('Error al enviar la solicitud', 'danger')
            return redirect(url_for('production.solicitar_horneado'))
    
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('production.solicitar_horneado'))

# Ver solicitudes pendientes
@bp_production.route('/solicitudes/pendientes', methods=['GET'])
@production_required
def ver_solicitudes_pendientes():
    if current_user.rol.nombreRol not in ['Administrador', 'Produccion']:
        abort(403)
    
    solicitudes = solicitud_horneado_service.get_solicitudes_pendientes()
    return render_template('produccion/solicitudes_pendientes.html', solicitudes=solicitudes)

# Ver mis solicitudes
@bp_production.route('/solicitudes/mis_solicitudes', methods=['GET'])
@production_required
def ver_mis_solicitudes():
    solicitudes = solicitud_horneado_service.get_solicitudes_usuario(current_user.idUser)
    return render_template('ventas/mis_solicitudes.html', solicitudes=solicitudes)

# Aprobar solicitud
@bp_production.route('/solicitud/aprobar/<int:id_solicitud>', methods=['POST'])
@production_required
def aprobar_solicitud(id_solicitud):
    if current_user.rol.nombreRol not in ['Administrador', 'Produccion']:
        abort(403)
    
    resultado = solicitud_horneado_service.aprobar_solicitud(
        id_solicitud,
        current_user.idUser
    )
    
    if resultado['success']:
        flash('Solicitud aprobada exitosamente', 'success')
    else:
        if 'insumos_faltantes' in resultado:
            flash('No hay suficientes insumos para aprobar la solicitud', 'danger')
        else:
            flash('Error al aprobar la solicitud', 'danger')
    
    return redirect(url_for('production.ver_solicitudes_pendientes'))

# Rechazar solicitud
@bp_production.route('/solicitud/rechazar/<int:id_solicitud>', methods=['POST'])
@production_required
def rechazar_solicitud(id_solicitud):
    if current_user.rol.nombreRol not in ['Administrador', 'Produccion']:
        abort(403)
    
    motivo = request.form.get('motivo', 'Sin motivo especificado')
    
    resultado = solicitud_horneado_service.rechazar_solicitud(
        id_solicitud,
        current_user.idUser,
        motivo
    )
    
    if resultado['success']:
        flash('Solicitud rechazada exitosamente', 'success')
    else:
        flash('Error al rechazar la solicitud', 'danger')
    
    return redirect(url_for('production.ver_solicitudes_pendientes'))

# Completar solicitud
@bp_production.route('/solicitud/completar/<int:id_solicitud>', methods=['GET', 'POST'])
@production_required
def completar_solicitud(id_solicitud):
    solicitud = solicitud_horneado_service.get_solicitud(id_solicitud)
    
    if not solicitud:
        flash('Solicitud no encontrada', 'danger')
        return redirect(url_for('production.ver_mis_solicitudes'))
    
    if (solicitud.id_solicitante != current_user.idUser and 
        current_user.rol.nombreRol not in ['Administrador', 'Produccion']):
        abort(403)
    
    if solicitud.estado != 'Aprobada':
        flash('La solicitud no está aprobada', 'danger')
        return redirect(url_for('production.ver_mis_solicitudes'))
    
    if request.method == 'POST':
        try:
            datos_horneado = {
                'temperatura': request.form.get('temperatura', type=int),
                'tiempo': request.form.get('tiempo', type=int),
                'observaciones': request.form.get('observaciones', '')
            }
            
            if not all([datos_horneado['temperatura'], datos_horneado['tiempo']]):
                flash('Temperatura y tiempo son obligatorios', 'danger')
                return redirect(url_for('production.completar_solicitud', id_solicitud=id_solicitud))
            
            resultado = solicitud_horneado_service.completar_solicitud(
                id_solicitud,
                datos_horneado
            )
            
            if resultado['success']:
                flash('Horneado registrado exitosamente', 'success')
                return redirect(url_for('production.proceso_horneadas'))
            else:
                flash(resultado['message'], 'danger')
        
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('produccion/completar_solicitud.html', solicitud=solicitud)

# Detalle de solicitud
@bp_production.route('/solicitud/detalle/<int:id_solicitud>', methods=['GET'])
@production_required
def detalle_solicitud(id_solicitud):
    solicitud = db.session.query(SolicitudHorneado)\
        .options(joinedload(SolicitudHorneado.receta))\
        .get(id_solicitud)
    
    if not solicitud:
        flash('Solicitud no encontrada', 'danger')
        return redirect(url_for('production.ver_mis_solicitudes'))
    
    
    # Calcular costos
    costos = receta_service.calcular_costo_galleta(solicitud.id_receta)
    


    # Verificar permisos (solicitante o aprobador)
    if solicitud.id_solicitante != current_user.idUser and \
       (solicitud.id_aprobador != current_user.idUser if solicitud.id_aprobador else True) and \
       current_user.rol.nombreRol not in ['Administrador', 'Produccion']:
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
        'produccion/detalle_solicitud.html',
        solicitud=solicitud,
        insumos=insumos_data,
        cantidad_total=solicitud.cantidad_lotes * solicitud.receta.cantidad_producida
        cantidad_total=solicitud.cantidad_lotes * solicitud.receta.cantGalletasProduction,

        costos=costos  # Pasar los costos a la plantilla
    )

# Proceso de horneadas
@bp_production.route('/proceso_horneadas')
@production_required
def proceso_horneadas():
    solicitudes_pendientes = db.session.query(SolicitudHorneado)\
        .options(
            joinedload(SolicitudHorneado.receta),
            joinedload(SolicitudHorneado.solicitante)
        )\
        .filter(SolicitudHorneado.estado == 'Aprobada')\
        .order_by(SolicitudHorneado.fecha_aprobacion.asc())\
        .all()
    
    fecha_inicio = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    horneados_recientes = horneado_service.get_horneados_filtrados(
        fecha_inicio=fecha_inicio,
        id_usuario=current_user.idUser
    )
    
    return render_template(
        'produccion/proceso_horneadas.html',
        solicitudes_pendientes=solicitudes_pendientes,
        horneados_recientes=horneados_recientes
    )

# Detalle de horneado
@bp_production.route('/detalle_horneado/<int:id_horneado>', methods=['GET'])
@production_required
def detalle_horneado(id_horneado):
    origen = request.args.get('origen', 'historial')
    horneado = horneado_service.get_horneado(id_horneado)
    
    if not horneado:
        flash('Horneado no encontrado', 'danger')
        return redirect(url_for('production.historial'))
    
    return render_template('produccion/detalle_horneado.html', horneado=horneado, origen=origen)