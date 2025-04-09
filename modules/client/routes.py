from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import login_required, current_user
from . import bp_clientes
from .services import obtener_detalles_galletas


# ? Ahora vamos a definir las rutas necesarias para el bluprint


# Ruta para el dashboard del cliente
@bp_clientes.route('/portal_cliente')
@login_required
def portal_cliente():
    if current_user.rol.nombreRol not in ['Cliente']:
        flash('No tienes permisos para acceder a esta sección', 'danger')
        return redirect(url_for('shared.index'))
    return render_template('client/portal_cliente.html')

@bp_clientes.route('/perfil')
@login_required
def perfil():
    if current_user.rol.nombreRol not in ['Cliente']:
        return redirect(url_for('shared.index'))
    return render_template('client/perfil_cliente.html')

@bp_clientes.route('/pedidos', endpoint='pedidos_cliente')
def pedidos_cliente():
    """
    Renderiza la página de "Mis Pedidos" con los datos de la vista `vista_detalles_galletas`.
    """
    if current_user.rol.nombreRol not in ['Cliente']:
        return redirect(url_for('shared.index'))
    detalles_galletas = obtener_detalles_galletas()
    return render_template('client/pedidos_cliente.html', detalles_galletas=detalles_galletas)