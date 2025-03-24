from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
#  ~ Importamos el archvio con el nombre del Blueprint para la sección
from . import bp_clientes


# ? Ahora vamos a definir las rutas necesarias para el bluprint


# ^ Sección del cliente

# Ruta para el dashboard del cliente
@bp_clientes.route('/portal_cliente')
def portal_cliente():
    if 'username' not in session or session['role'] != 'cliente':
        return redirect(url_for('cliente.login'))
    return render_template('client/portal_cliente.html')

# Otras rutas...
@bp_clientes.route('/usuarios')
def usuarios():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('cliente.login'))
    return render_template('admin/usuarios.html')


@bp_clientes.route('/clientes')
def clientes():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('cliente.login'))
    return render_template('admin/clientes.html')



