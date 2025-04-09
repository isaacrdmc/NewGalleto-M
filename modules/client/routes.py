from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import login_required, current_user
from . import bp_clientes

@bp_clientes.route('/portal_cliente')
@login_required
def portal_cliente():
    if current_user.rol.nombreRol not in ['Cliente', 'Administrador']:
        flash('No tienes permisos para acceder a esta sección', 'danger')
        return redirect(url_for('shared.index'))
    return render_template('client/portal_cliente.html')

@bp_clientes.route('/perfil')
@login_required
def perfil():
    if current_user.rol.nombreRol != 'Cliente':
        flash('No tienes permisos para acceder a esta sección', 'danger')
        return redirect(url_for('shared.index'))
    return render_template('client/perfil_cliente.html')