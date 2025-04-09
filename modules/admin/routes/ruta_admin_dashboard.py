

from flask import current_app, render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask import render_template, jsonify, redirect, url_for
from flask_login import login_required, current_user
from ..services import (
    obtener_ventas_semanales, 
    obtener_top_galletas,
    obtener_estimacion_costos,
    obtener_historial_ventas_semanales,
    obtener_top_presentaciones,
    obtener_ventas_por_dia,
    obtener_distribucion_ventas
)
from ...admin import bp_admistracion

@bp_admistracion.route('/dashboard_admin')
@login_required
def dashboard_admin():
    if current_user.rol.nombreRol != 'Administrador':
        flash('No tienes permisos para acceder a esta sección', 'danger')
        current_app.logger.error(f'Acceso no autorizado a la página del dashboard por el usuario {current_user.username}')
        return redirect(url_for('shared.index'))
    current_app.logger.info(f'Acceso autorizado a la página del dashboard por el usuario {current_user.username}')
    # return render_template('admin/dashboard.html') 
    
    # Obtener datos para el dashboard
    ventas_semanales = obtener_ventas_semanales()
    top_galletas = [dict(row) for row in obtener_top_galletas()] if obtener_top_galletas() else []
    top_presentaciones = [dict(row) for row in obtener_top_presentaciones()] if obtener_top_presentaciones() else []
    estimacion_costos = obtener_estimacion_costos()
    historial_ventas = obtener_historial_ventas_semanales()
    ventas_por_dia = obtener_ventas_por_dia()
    distribucion_ventas = obtener_distribucion_ventas()
    
    return render_template('admin/dashboard.html',
                         ventas_semanales=ventas_semanales,
                         top_galletas=top_galletas,
                         top_presentaciones=top_presentaciones,
                         estimacion_costos=estimacion_costos,
                         historial_ventas=historial_ventas,
                         ventas_por_dia=ventas_por_dia,
                         distribucion_ventas=distribucion_ventas)

@bp_admistracion.route('/dashboard/datos')
@login_required
def obtener_datos_dashboard():
    try:
        ventas_semanales = obtener_ventas_semanales()
        top_galletas = obtener_top_galletas() or []
        top_presentaciones = [dict(row) for row in obtener_top_presentaciones()] if obtener_top_presentaciones() else []
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