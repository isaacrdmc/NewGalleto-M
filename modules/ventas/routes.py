from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import login_required, current_user
from . import bp_ventas

@bp_ventas.route('/ventas')
@login_required
def ventas():
    if current_user.rol.nombreRol != 'Ventas':
        flash('No tienes permisos para acceder a esta sección', 'danger')
        return redirect(url_for('shared.index'))
    return render_template('ventas/ventas.html')

@bp_ventas.route('/inventario_galletas')
@login_required
def inventario_galletas():
    if current_user.rol.nombreRol != 'Ventas':
        flash('No tienes permisos para acceder a esta sección', 'danger')
        return redirect(url_for('shared.index'))
    return render_template('ventas/prod_term.html')