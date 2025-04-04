from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
#  ~ Importamos el archvio con el nombre del Blueprint para la sección
from . import bp_clientes


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