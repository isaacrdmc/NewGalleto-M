from datetime import datetime
import os
from flask import abort, json, render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
from .services import FACTORES_CONVERSION, UNIDADES_COMPATIBLES, ProveedorService, GalletaService, InsumoService, RecetaService,HorneadoService,CompraService, SolicitudHorneadoService
from .models import Receta, SolicitudHorneado, db, Horneado, Insumo, Merma
from modules.admin.models import DetalleCompraInsumo, Proveedores as Proveedor, TransaccionCompra
from sqlalchemy import desc, func, text
#  ~ Importamos el archvio con el nombre del Blueprint para la sección
from flask_login import login_required, current_user
from . import bp_production
from database.conexion import db
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload  # Añade este import al inicio del archivo

# Servicios
proveedor_service = ProveedorService(db.session)
galleta_service = GalletaService(db.session)
insumo_service = InsumoService(db.session)
receta_service = RecetaService(db.session)
horneado_service = HorneadoService(db.session)
compra_service = CompraService(db.session)
solicitud_horneado_service = SolicitudHorneadoService(db.session)


# Rutas para Proveedor
@bp_production.route('/proveedores', methods=['GET'])
@login_required
def get_all_proveedores():
    proveedores = proveedor_service.get_all_proveedores()
    return jsonify([proveedor.to_dict() for proveedor in proveedores])

@bp_production.route('/proveedor', methods=['POST'])
@login_required
def add_proveedor():
    data = request.get_json()
    nuevo_proveedor = proveedor_service.add_proveedor(
        data['nombre'],
        data['telefono'],
        data['correo'],
        data['direccion'],
        data['productosProveedor']
    )
    if nuevo_proveedor:
        return jsonify(nuevo_proveedor.to_dict()), 201
    return jsonify({"error": "No se pudo agregar el proveedor"}), 400

@bp_production.route('/proveedor/<int:id>', methods=['GET'])
@login_required
def get_proveedor(id):
    proveedor = proveedor_service.get_proveedor(id)
    if proveedor:
        return jsonify(proveedor.to_dict())
    return jsonify({"error": "Proveedor no encontrado"}), 404

# Rutas para Galleta
@bp_production.route('/galletas', methods=['GET'])
@login_required
def get_all_galletas():
    galletas = galleta_service.get_all_galletas()
    return jsonify([galleta.to_dict() for galleta in galletas])

@bp_production.route('/galleta', methods=['POST'])
@login_required
def add_galleta():
    data = request.get_json()
    nueva_galleta = galleta_service.add_galleta(
        data['nombreGalleta'],
        data['precioUnitario'],
        data['cantidadDisponible'],
        data['gramajeGalleta'],
        data['tipoGalleta'],
        data['fechaAnaquel'],
        data['fechaFinalAnaquel']
    )
    if nueva_galleta:
        return jsonify(nueva_galleta.to_dict()), 201
    return jsonify({"error": "No se pudo agregar la galleta"}), 400

@bp_production.route('/galleta/<int:id>', methods=['GET'])
@login_required
def get_galleta(id):
    galleta = galleta_service.get_galleta(id)
    if galleta:
        return jsonify(galleta.to_dict())
    return jsonify({"error": "Galleta no encontrada"}), 404

# Rutas para Insumo
@bp_production.route('/insumos', methods=['GET'])
@login_required
def get_all_insumos():
    insumos = insumo_service.get_all_insumos()
    return jsonify([insumo.to_dict() for insumo in insumos])

@bp_production.route('/insumo', methods=['POST'])
@login_required
def add_insumo():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Datos no proporcionados"}), 400

        nuevo_insumo = insumo_service.add_insumo(
            data.get('nombre'),
            data.get('unidad'),
            data.get('cantidad_disponible'),
            data.get('cantidad_minima')
        )
        
        if nuevo_insumo:
            return jsonify(nuevo_insumo.to_dict()), 201
        return jsonify({"error": "No se pudo agregar el insumo"}), 400
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp_production.route('/insumo/<int:id>', methods=['GET'])
@login_required
def get_insumo(id):
    insumo = insumo_service.get_insumo(id)
    if insumo:
        return jsonify(insumo.to_dict())
    return jsonify({"error": "Insumo no encontrado"}), 404

# Rutas para Receta
@bp_production.route('/recetas', methods=['GET'])
@login_required
def get_all_recetas():
    recetas = receta_service.get_all_recetas()
    return jsonify([receta.to_dict() for receta in recetas])

@bp_production.route('/receta', methods=['POST'])
@login_required
def add_receta():
    data = request.get_json()
    nueva_receta = receta_service.add_receta(
        data['nombreReceta'],
        data['instruccionReceta'],
        data['cantGalletasProduction'],
        data['galletTipo'],
        data['idGalleta']
    )
    if nueva_receta:
        return jsonify(nueva_receta.to_dict()), 201
    return jsonify({"error": "No se pudo agregar la receta"}), 400

@bp_production.route('/receta/<int:id>', methods=['GET'])
@login_required
def get_receta(id):
    receta = receta_service.get_receta(id)
    if receta:
        return jsonify(receta.to_dict())
    return jsonify({"error": "Receta no encontrada"}), 404


    

@bp_production.route('/dashboard_produccion')
@login_required
def dashboard_produccion():
    # Obtener producción diaria (galletas producidas hoy)
    produccion_diaria = db.session.query(
        func.sum(Horneado.cantidad_producida)
    ).filter(
        func.date(Horneado.fecha_horneado) == datetime.now().date()
    ).scalar() or 0

    # Obtener lotes pendientes (solicitudes aprobadas no completadas)
    lotes_pendientes = db.session.query(
        func.count(SolicitudHorneado.id)
    ).filter(
        SolicitudHorneado.estado == 'Aprobada'
    ).scalar() or 0

    # Obtener producciones recientes (últimos 5 horneados o solicitudes)
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

# Añadir a routes.py

# Instanciamos el servicio de horneado
horneado_service = HorneadoService(db.session)

@bp_production.route('/historial_horneados')
@login_required
def historial():
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    id_receta = request.args.get('receta')
    
    # Convertir id_receta a entero si existe
    if id_receta:
        try:
            id_receta = int(id_receta)
        except ValueError:
            id_receta = None
    
    # Obtener los horneados filtrados
    horneados = horneado_service.get_horneados_filtrados(fecha_inicio, fecha_fin, id_receta)
    
    # Obtener todas las recetas para el filtro
    recetas = receta_service.get_all_recetas()
    
    # Renderizar el template con los datos
    return render_template(
        'produccion/historial_horneada.html',
        horneados=horneados,
        recetas=recetas
    )

@bp_production.route('/estadisticas_horneado', methods=['GET'])
def estadisticas_horneado():
    # Obtener parámetro de días a consultar (por defecto 30 días)
    dias = request.args.get('dias', 30, type=int)
    
    # Obtener estadísticas
    estadisticas = horneado_service.get_estadisticas_horneado(dias)
    
    # Devolver en formato JSON para ser consumido por ajax
    return jsonify(estadisticas)

@bp_production.route('/horneado', methods=['GET'])
@login_required
def horneado():
    # Obtener todas las recetas para el selector
    recetas = receta_service.get_all_recetas()
    return render_template('produccion/hornear_galleta.html', recetas=recetas)

@bp_production.route('/registrar_horneado', methods=['POST'])
@login_required
def registrar_horneado():
    try:
        # Obtener datos del formulario
        id_receta = request.form.get('id_receta', type=int)
        temperatura = request.form.get('temperatura', type=int)
        tiempo = request.form.get('tiempo', type=int)
        cantidad = request.form.get('cantidad', type=int)
        observaciones = request.form.get('observaciones', '')

        # Validar datos
        if not all([id_receta, temperatura, tiempo, cantidad]):
            flash('Todos los campos son obligatorios excepto observaciones', 'danger')
            return redirect(url_for('production.horneado'))

        id_usuario = current_user.idUser  # ← esta es la manera correcta con Flask-Login

        # Registrar horneado usando el servicio
        resultado = horneado_service.registrar_horneado(
            temperatura,
            tiempo,
            cantidad,
            observaciones,
            id_receta,
            id_usuario
        )

        if resultado:
            flash('Horneado registrado exitosamente', 'success')
        else:
            flash('Error al registrar el horneado', 'danger')

        return redirect(url_for('production.horneado'))

    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('production.horneado'))


#####################################
# Ruta de inventario
@bp_production.route('/inventario', methods=['GET'])
@login_required
def inventario():
    # Obtener todos los insumos desde el servicio
    insumos = insumo_service.get_all_insumos()
    print(insumos)  # <-- verifica esto en consola
    return render_template('produccion/inventario_insumos.html', inventario=insumos)

# Ruta de detalle de insumo actualizada
@bp_production.route('/insumo/detalle/<int:id_insumo>', methods=['GET'])
@login_required
def detalle_insumo(id_insumo):
    # Obtener el insumo según su ID
    insumo = insumo_service.get_insumo(id_insumo)
    
    if not insumo:
        flash("Insumo no encontrado", "error")
        return redirect(url_for('production.inventario'))
    
    # Obtener los lotes del insumo (detalles de compra)
    lotes = db.session.query(
        DetalleCompraInsumo,
        TransaccionCompra.fechaCompra,
        Proveedor.nombre.label('proveedor_nombre')
    ).join(
        TransaccionCompra, DetalleCompraInsumo.idCompra == TransaccionCompra.idTransaccionCompra
    ).join(
        Proveedor, TransaccionCompra.idProveedor == Proveedor.idProveedores  # Cambiar id por idProveedor
    ).filter(
        DetalleCompraInsumo.idInsumo == id_insumo
    ).order_by(
        DetalleCompraInsumo.fechaCaducidad
    ).all()
    
    # Preparar los datos de lotes para la vista
    lotes_data = []
    lotes_proximos_caducar = []
    
    # Fecha límite para considerar un producto próximo a caducar (7 días)
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
        
        # Si el lote está próximo a caducar, agregarlo a la lista correspondiente
        if lote_data['is_expiring_soon']:
            lotes_proximos_caducar.append(lote_data)
    
    # Obtener todos los proveedores para la lista desplegable de compra
    proveedores = proveedor_service.get_all_proveedores()
    
    # Pasar los datos al template
    return render_template('produccion/detalle_insumo.html', 
                           insumo=insumo, 
                           lotes=lotes_data,
                           lotes_proximos_caducar=lotes_proximos_caducar,
                           proveedores=proveedores)

# Ruta alternativa por nombre (para mantener compatibilidad)
@bp_production.route('/insumo/detalle/nombre/<string:nombre_insumo>', methods=['GET'])
@login_required
def detalle_insumo_por_nombre(nombre_insumo):
    # Obtener el insumo según su nombre
    insumo = insumo_service.get_insumo_por_nombre(nombre_insumo)
    
    if insumo:
        # Redirigir a la ruta por ID
        return redirect(url_for('production.detalle_insumo', id_insumo=insumo.id))
    else:
        flash("Insumo no encontrado", "error")
        return redirect(url_for('production.inventario'))

# Ruta para registrar una nueva compra de insumo
@bp_production.route('/insumo/compra', methods=['POST'])
@login_required
def registrar_compra_insumo():
    try:
        # Obtener datos del formulario
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
        
        unidad_base = insumo.unidad  # gr, ml o pz
        
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
        
        # Registrar la compra (resto del código igual)
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


# Ruta para registrar merma de insumo
@bp_production.route('/insumo/merma', methods=['POST'])
@login_required
def registrar_merma():
    try:
        # Obtener datos del formulario
        id_insumo = request.form.get('id_insumo', type=int)
        id_lote = request.form.get('id_lote', type=int)
        tipoMerma = request.form.get('tipo_merma')
        cantidad_merma = request.form.get('cantidad_merma', type=int)
        unidad_merma = request.form.get('unidad_merma')
        
        # Validar datos
        if not all([id_insumo, tipoMerma, cantidad_merma, unidad_merma]):
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(url_for('production.detalle_insumo', id_insumo=id_insumo))
        
        # Crear un registro de merma
        merma = Merma(
            tipoMerma=tipoMerma,
            unidadMerma=unidad_merma,
            cantidadMerma=cantidad_merma,
            fechaMerma=datetime.now().date(),
            idInsumo=id_insumo
        )
        
        # Agregar y guardar la merma
        db.session.add(merma)
        
        # Actualizar la cantidad disponible del insumo
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
    
    #########################################
    # Añadir al inicio de routes.py, después de los otros servicios

@bp_production.route('/solicitar_horneado', methods=['GET'])
@login_required
def solicitar_horneado():
    # Obtener todas las recetas para el selector
    recetas = receta_service.get_all_recetas()
    return render_template('ventas/solicitar_horneado.html', recetas=recetas)

@bp_production.route('/solicitar_horneado', methods=['POST'])
@login_required
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
            return redirect(url_for('production.ver_mis_solicitudes'))  # Redirigir a la lista de solicitudes
        else:
            if 'insumos_faltantes' in resultado:
                flash('No hay suficientes insumos para completar la solicitud', 'danger')
            else:
                flash('Error al enviar la solicitud', 'danger')
            return redirect(url_for('production.solicitar_horneado'))
    
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('production.solicitar_horneado'))
    
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('production.solicitar_horneado'))

@bp_production.route('/solicitudes/pendientes', methods=['GET'])
@login_required
def ver_solicitudes_pendientes():
    if current_user.rol.nombreRol not in ['Administrador', 'Produccion']:
        abort(403)
    
    solicitudes = solicitud_horneado_service.get_solicitudes_pendientes()
    return render_template('produccion/solicitudes_pendientes.html', solicitudes=solicitudes)

@bp_production.route('/solicitudes/mis_solicitudes', methods=['GET'])
@login_required
def ver_mis_solicitudes():
    print(f"Usuario actual ID: {current_user.idUser}")  # Debug
    solicitudes = solicitud_horneado_service.get_solicitudes_usuario(current_user.idUser)
    print(f"Solicitudes a enviar a template: {len(solicitudes)}")  # Debug
    return render_template('ventas/mis_solicitudes.html', solicitudes=solicitudes)

@bp_production.route('/solicitud/aprobar/<int:id_solicitud>', methods=['POST'])
@login_required
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

@bp_production.route('/solicitud/rechazar/<int:id_solicitud>', methods=['POST'])
@login_required
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

@bp_production.route('/solicitud/completar/<int:id_solicitud>', methods=['GET', 'POST'])
@login_required
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

@bp_production.route('/solicitud/detalle/<int:id_solicitud>', methods=['GET'])
@login_required
def detalle_solicitud(id_solicitud):
    # Consulta optimizada que carga la receta en la misma consulta
    solicitud = db.session.query(SolicitudHorneado)\
        .options(joinedload(SolicitudHorneado.receta))\
        .get(id_solicitud)
    
    if not solicitud:
        flash('Solicitud no encontrada', 'danger')
        return redirect(url_for('production.ver_mis_solicitudes'))
    
    # Verificar permisos (solicitante o aprobador)
    if solicitud.id_solicitante != current_user.idUser and \
       (solicitud.id_aprobador != current_user.idUser if solicitud.id_aprobador else True) and \
       current_user.rol.nombreRol not in ['Administrador', 'Produccion']:
        abort(403)
    
    # Obtener detalles de insumos necesarios con información completa
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
    
    # Convertir el resultado a una lista de diccionarios para facilitar el acceso en la plantilla
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
    )
@bp_production.route('/proceso_horneadas')
@login_required
def proceso_horneadas():
    # Obtener solicitudes aprobadas pendientes de completar
    solicitudes_pendientes = db.session.query(SolicitudHorneado)\
        .options(
            joinedload(SolicitudHorneado.receta),
            joinedload(SolicitudHorneado.solicitante)
        )\
        .filter(SolicitudHorneado.estado == 'Aprobada')\
        .order_by(SolicitudHorneado.fecha_aprobacion.asc())\
        .all()
    
    # Obtener horneados recientes del usuario (últimos 7 días)
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
    
@bp_production.route('/detalle_horneado/<int:id_horneado>', methods=['GET'])
def detalle_horneado(id_horneado):
    # Obtener el horneado por ID
    origen = request.args.get('origen', 'historial')  # Por defecto, vuelve a historial
    horneado = horneado_service.get_horneado(id_horneado)
    
    if not horneado:
        flash('Horneado no encontrado', 'danger')
        return redirect(url_for('production.historial'))
    
    # Renderizar template con los detalles
    return render_template('produccion/detalle_horneado.html', horneado=horneado, origen=origen)