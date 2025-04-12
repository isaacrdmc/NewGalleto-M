from functools import wraps
from flask import flash, render_template, jsonify, redirect, request, url_for
from flask_login import login_required, current_user
from ..services import (
    obtener_costos_produccion,
    obtener_recomendacion_producto,
    obtener_ventas_semanales, 
    obtener_top_galletas,
    obtener_estimacion_costos,
    obtener_historial_ventas_semanales,
    obtener_top_presentaciones,
    obtener_ventas_por_dia,
    obtener_distribucion_ventas, 
    obtener_produccion_semanal, 
    obtener_eficiencia_produccion, 
    obtener_notificaciones_recientes, 
    marcar_notificacion_como_vista
)
from ...admin import bp_admistracion

# Decorador personalizado para validar rol de Administrador
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Por favor inicie sesión para acceder a esta página', 'warning')
            return redirect(url_for('shared.login', next=request.url))
        
        if current_user.rol.nombreRol != 'Administrador':
            flash('No tiene permisos para acceder a esta sección', 'danger')
            return redirect(url_for('shared.index'))
        
        return f(*args, **kwargs)
    return decorated_function

@bp_admistracion.route('/dashboard_admin')
@admin_required
def dashboard_admin():
    # Datos para el dashboard
    ventas_semanales = obtener_ventas_semanales()
    top_galletas = [dict(row) for row in obtener_top_galletas()] if obtener_top_galletas() else []
    recomendacion_producto = obtener_recomendacion_producto()
    estimacion_costos = obtener_estimacion_costos()
    historial_ventas = obtener_historial_ventas_semanales()
    ventas_por_dia = obtener_ventas_por_dia()
    distribucion_ventas = obtener_distribucion_ventas()
    produccion_semanal = obtener_produccion_semanal()
    eficiencia_produccion = obtener_eficiencia_produccion()
    costos_produccion = obtener_costos_produccion()
    
    return render_template('admin/dashboard.html',
                         ventas_semanales=ventas_semanales,
                         top_galletas=top_galletas,
                         recomendacion_producto=recomendacion_producto,
                         estimacion_costos=estimacion_costos,
                         historial_ventas=historial_ventas,
                         ventas_por_dia=ventas_por_dia,
                         distribucion_ventas=distribucion_ventas,
                         produccion_semanal=produccion_semanal,
                         eficiencia_produccion=eficiencia_produccion,
                         costos_produccion=costos_produccion)

@bp_admistracion.route('/dashboard/datos')
@login_required
def obtener_datos_dashboard():
    try:
        ventas_semanales = obtener_ventas_semanales()
        top_galletas = obtener_top_galletas() or []  # Manejar caso None
        top_presentaciones = obtener_top_presentaciones() or []  # Manejar caso None
        estimacion_costos = obtener_estimacion_costos()
        historial_ventas = obtener_historial_ventas_semanales()
        ventas_por_dia = obtener_ventas_por_dia()
        distribucion_ventas = obtener_distribucion_ventas()
        
        return jsonify({
            'ventas_semanales': ventas_semanales,
            'top_galletas': top_galletas,
            'top_presentaciones': top_presentaciones,
            'estimacion_costos': estimacion_costos,
            'historial_ventas': historial_ventas,
            'ventas_por_dia': ventas_por_dia,
            'distribucion_ventas': distribucion_ventas
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@bp_admistracion.route('/notificaciones')
@login_required
def obtener_notificaciones():
    notificaciones = obtener_notificaciones_recientes(usuario_id=current_user.idUser)
    return jsonify([{
        'id': notif.id,
        'tipo': notif.tipo,
        'mensaje': notif.mensaje,
        'fecha': notif.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S') if notif.fecha_creacion else None,
        'estado': notif.estado
    } for notif in notificaciones])

@bp_admistracion.route('/notificaciones/marcar_vista/<int:notificacion_id>', methods=['POST'])
@login_required
def marcar_notificacion_vista(notificacion_id):
    notificacion = marcar_notificacion_como_vista(notificacion_id)
    if notificacion:
        return jsonify({'success': True, 'message': 'Notificación marcada como vista'})
    return jsonify({'success': False, 'message': 'Notificación no encontrada'}), 404