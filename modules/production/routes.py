from datetime import datetime
import os
from flask import abort, json, render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
from .services import ProveedorService, GalletaService, InsumoService, RecetaService,HorneadoService,CompraService
from .models import db, Horneado, Insumo, DetalleCompraInsumo, Merma, TransaccionCompra
from modules.admin.models import Proveedores as Proveedor
from sqlalchemy import desc, func
#  ~ Importamos el archvio con el nombre del Blueprint para la sección
from flask_login import login_required, current_user
from . import bp_production
from database.conexion import db
from datetime import datetime, timedelta

# Servicios
proveedor_service = ProveedorService(db.session)
galleta_service = GalletaService(db.session)
insumo_service = InsumoService(db.session)
receta_service = RecetaService(db.session)
horneado_service = HorneadoService(db.session)
compra_service = CompraService(db.session)


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
    data = request.get_json()
    nuevo_insumo = insumo_service.add_insumo(
        data['nombre'],
        data['unidadInsumo'],  # Este nombre se mantiene igual porque viene del cliente
        data['cantidadDisponible'],  # Este nombre se mantiene igual porque viene del cliente
        data['cantidadMinima']  # Este nombre se mantiene igual porque viene del cliente
    )
    if nuevo_insumo:
        return jsonify(nuevo_insumo.to_dict()), 201
    return jsonify({"error": "No se pudo agregar el insumo"}), 400

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
    if current_user.rol.nombreRol != 'Produccion':
        return redirect(url_for('shared.login'))
    return render_template('produccion/produccion.html')

# Añadir a routes.py

# Instanciamos el servicio de horneado
horneado_service = HorneadoService(db.session)

@bp_production.route('/historial', methods=['GET'])
def historial():
    # Obtener parámetros de filtrado
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

@bp_production.route('/detalle_horneado/<int:id_horneado>', methods=['GET'])
def detalle_horneado(id_horneado):
    # Obtener el horneado por ID
    horneado = horneado_service.get_horneado(id_horneado)
    
    if not horneado:
        flash('Horneado no encontrado', 'danger')
        return redirect(url_for('production.historial'))
    
    # Renderizar template con los detalles
    return render_template('produccion/detalle_horneado.html', horneado=horneado)


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
        TransaccionCompra.fecha_compra,
        Proveedor.nombre.label('proveedor_nombre')
    ).join(
        TransaccionCompra, DetalleCompraInsumo.id_compra == TransaccionCompra.id
    ).join(
        Proveedor, TransaccionCompra.id_proveedor == Proveedor.idProveedores  # Cambiar id por idProveedor
    ).filter(
        DetalleCompraInsumo.id_insumo == id_insumo
    ).order_by(
        DetalleCompraInsumo.fecha_caducidad
    ).all()
    
    # Preparar los datos de lotes para la vista
    lotes_data = []
    lotes_proximos_caducar = []
    
    # Fecha límite para considerar un producto próximo a caducar (7 días)
    fecha_limite = datetime.now().date() + timedelta(days=7)
    
    for lote, fecha_compra, proveedor_nombre in lotes:
        lote_data = {
            'id': lote.id,
            'cant_cajas': lote.cant_cajas,
            'cant_unidades_caja': lote.cant_unidades_caja,
            'cant_merma_unidad': lote.cant_merma_unidad,
            'costo_caja': float(lote.costo_caja),
            'costo_unidad_caja': float(lote.costo_unidad_caja),
            'unidad_insumo': lote.unidad_insumo,
            'fecha_registro': lote.fecha_registro.strftime('%Y-%m-%d'),
            'fecha_caducidad': lote.fecha_caducidad.strftime('%Y-%m-%d'),
            'fecha_compra': fecha_compra.strftime('%Y-%m-%d'),
            'proveedor_nombre': proveedor_nombre,
            'is_expiring_soon': lote.fecha_caducidad <= fecha_limite
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
        # Log para depuración
        print("==== Iniciando registro de compra de insumo ====")
        print(f"Datos del formulario: {request.form}")
        
        # Obtener datos del formulario
        id_insumo = request.form.get('id_insumo', type=int)
        id_proveedor_str = request.form.get('id_proveedor')  # Primero obtén como string
        cant_cajas = request.form.get('cant_cajas', type=int)
        cant_unidades_caja = request.form.get('cant_unidades_caja', type=int)
        costo_caja = request.form.get('costo_caja', type=float)
        fecha_caducidad = request.form.get('fecha_caducidad')
        
        # Validar que id_proveedor tenga un valor
        if not id_proveedor_str:
            flash('Debe seleccionar un proveedor', 'danger')
            return redirect(url_for('production.detalle_insumo', id_insumo=id_insumo))
        
        # Convertir id_proveedor a entero después de validar que no esté vacío
        id_proveedor = int(id_proveedor_str)
        
        # Resto de tu validación
        if not all([id_insumo, id_proveedor, cant_cajas, cant_unidades_caja, costo_caja, fecha_caducidad]):
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(url_for('production.detalle_insumo', id_insumo=id_insumo))
        
        # Obtener el insumo para conocer su unidad de medida
        insumo = insumo_service.get_insumo(id_insumo)
        if not insumo:
            flash('Insumo no encontrado', 'danger')
            return redirect(url_for('production.inventario'))
        
        # Depuración - mostrar valor de la unidad
        print(f"Unidad del insumo: {insumo.unidad}, tipo: {type(insumo.unidad)}")
        
        # Crear o obtener una transacción de compra
        print(f"Llamando a registrar_compra con proveedor ID: {id_proveedor}")
        id_transaccion = compra_service.registrar_compra(id_proveedor)
        print(f"ID de transacción obtenido: {id_transaccion}")
        
        if not id_transaccion:
            flash('Error al registrar la transacción de compra', 'danger')
            return redirect(url_for('production.detalle_insumo', id_insumo=id_insumo))
        
        # Registrar el detalle de la compra
        cant_merma_unidad = 0  # Asumimos un 0% de merma por unidad inicialmente
        fecha_registro = datetime.now().date()
        
        print(f"Llamando a agregar_detalle_compra con ID transacción: {id_transaccion}")
        # IMPORTANTE: Corregir la forma en que pasas los parámetros
        resultado = compra_service.agregar_detalle_compra(
            id_transaccion,
            id_insumo,
            cant_cajas,
            cant_unidades_caja,
            cant_merma_unidad,
            costo_caja,
            insumo.unidad,  # Sin comentario aquí
            fecha_registro,
            datetime.strptime(fecha_caducidad, '%Y-%m-%d').date()
        )
        
        print(f"Resultado de agregar_detalle_compra: {resultado}")
        
        # Confirmación de éxito o error
        if resultado:
            flash('Compra registrada exitosamente', 'success')
        else:
            flash('Error al registrar el detalle de la compra', 'danger')
            print("Error al registrar el detalle de la compra.")  # Depuración
        
        return redirect(url_for('production.detalle_insumo', id_insumo=id_insumo))

    except Exception as e:
        # Capturar cualquier error inesperado
        print(f"Excepción capturada: {str(e)}")  # Debug
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
        tipo_merma = request.form.get('tipo_merma')
        cantidad_merma = request.form.get('cantidad_merma', type=int)
        unidad_merma = request.form.get('unidad_merma')
        
        # Validar datos
        if not all([id_insumo, tipo_merma, cantidad_merma, unidad_merma]):
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(url_for('production.detalle_insumo', id_insumo=id_insumo))
        
        # Crear un registro de merma
        merma = Merma(
            tipo_merma=tipo_merma,
            unidad_merma=unidad_merma,
            cantidad_merma=cantidad_merma,
            fecha_merma=datetime.now().date(),
            id_insumo=id_insumo
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
                    tipo_notificacion='Bajo Inventario',
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