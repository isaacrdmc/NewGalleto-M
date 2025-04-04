from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash,check_password_hash
#  ~ Importamos el archvio con el nombre del Blueprint para la sección
from . import bp_ventas

# ? Ahora vamos a definir las rutas necesarias para el bluprint

# ^ Sección del vendedor

# Ruta para el dashboard de ventas
@bp_ventas.route('/ventas')
def ventas():
    if 'username' not in session or session['role'] != 'ventas':
        return redirect(url_for('shared.login'))
    return render_template('ventas/ventas.html')

@bp_ventas.route('/inventario_galletas')
def inventario_galletas():
    if 'username' not in session or session['role'] != 'ventas':
        return redirect(url_for('shared.login'))
    return render_template('ventas/prod_term.html')