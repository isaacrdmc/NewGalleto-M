from flask import render_template, jsonify, redirect, url_for
from flask_login import login_required, current_user
from ..services import (
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

@bp_admistracion.route('/dashboard_admin')
@login_required
def dashboard_admin():
    if current_user.rol.nombreRol != 'Administrador':
        return redirect(url_for('shared.index'))
    
    # Datos existentes
    ventas_semanales = obtener_ventas_semanales()
    top_galletas = [dict(row) for row in obtener_top_galletas()] if obtener_top_galletas() else []
    top_presentaciones = [dict(row) for row in obtener_top_presentaciones()] if obtener_top_presentaciones() else []
    estimacion_costos = obtener_estimacion_costos()
    historial_ventas = obtener_historial_ventas_semanales()
    ventas_por_dia = obtener_ventas_por_dia()
    distribucion_ventas = obtener_distribucion_ventas()
    
    # Nuevos datos de producción
    produccion_semanal = obtener_produccion_semanal()
    eficiencia_produccion = obtener_eficiencia_produccion()
    
    return render_template('admin/dashboard.html',
                         ventas_semanales=ventas_semanales,
                         top_galletas=top_galletas,
                         top_presentaciones=top_presentaciones,
                         estimacion_costos=estimacion_costos,
                         historial_ventas=historial_ventas,
                         ventas_por_dia=ventas_por_dia,
                         distribucion_ventas=distribucion_ventas,
                         produccion_semanal=produccion_semanal,
                         eficiencia_produccion=eficiencia_produccion)

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