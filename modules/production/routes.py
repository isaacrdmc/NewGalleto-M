from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify

from modules.admin.services import obtener_proveedores
#  ~ Importamos el archvio con el nombre del Blueprint para la sección
from . import bp_production


# ? Ahora vamos a definir las rutas necesarias para el bluprint
 

# ^ Sección de producción


# * Ruta para el dashboard de producción
@bp_production.route('/produccion')
def produccion():
    if 'username' not in session or session['role'] != 'produccion':
        return redirect(url_for('shared.login'))
    return render_template('produccion/produccion.html')

@bp_production.route('/inventario_insumos')
def inventario_insumos():
    if 'username' not in session or session['role'] != 'produccion':
        return redirect(url_for('shared.login'))
    return render_template('produccion/mat_prim.html')








