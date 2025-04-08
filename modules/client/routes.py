from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
#  ~ Importamos el archvio con el nombre del Blueprint para la sección
from . import bp_clientes
from .services import obtener_detalles_galletas


# ? Ahora vamos a definir las rutas necesarias para el bluprint


# Ruta para el dashboard del cliente
@bp_clientes.route('/portal_cliente')
def portal_cliente():
    if 'username' not in session or session['role'] != 'cliente':
        return redirect(url_for('shared.login'))
    return render_template('client/portal_cliente.html')


@bp_clientes.route('/perfil')
def perfil():
    if 'username' not in session or session['role'] != 'cliente':
        return redirect(url_for('admin.login'))
    return render_template('client/perfil_cliente.html')

@bp_clientes.route('/pedidos', endpoint='pedidos_cliente')
def pedidos_cliente():
    """
    Renderiza la página de "Mis Pedidos" con los datos de la vista `vista_detalles_galletas`.
    """
    if 'username' not in session or session['role'] != 'cliente':
        return redirect(url_for('admin.login'))
    detalles_galletas = obtener_detalles_galletas()
    return render_template('client/pedidos_cliente.html', detalles_galletas=detalles_galletas)