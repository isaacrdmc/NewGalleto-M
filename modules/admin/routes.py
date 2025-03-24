

from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
#  ~ Importamos el archvio con el nombre del Blueprint para la sección
from . import bp_admistracion


# ? Ahora vamos a definir las rutas necesarias para el bluprint


# ^ Sección del adminstrador

@bp_admistracion.route('/adminstrador/DashBoad')
def dashboard():
    return 

@bp_admistracion.route('/usuarios')
def usuarios():
    return render_template('admin/usuarios.html')

# Ruta para el dashboard del administrador
@bp_admistracion.route('/dashboard_admin')
def dashboard_admin():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('admin/dashboard.html')

@bp_admistracion.route('/insumos/<id>', methods=['GET'])
def obtener_insumo(id):
    for i in insumo:
        if i['id'] == id:
            return jsonify(i)
    return jsonify({"error": "Insumo no encontrado"}), 404

@bp_admistracion.route('/insumos/editar/<id>', methods=['POST'])
def editar_insumo(id):
    if request.is_json:
        datos = request.get_json()  # Obtener los datos JSON del cuerpo de la solicitud
        for i in insumo:  # Asegúrate de que el nombre de la lista sea "insumos"
            if i['id'] == id:
                # Usar los datos del JSON recibido para actualizar el insumo
                i['lote'] = datos['lote']
                i['producto'] = datos['producto']
                i['cantidad'] = datos['cantidad']
                i['fechaCaducidad'] = datos['fechaCaducidad']
                i['mermas'] = datos['mermas']
                # Retornar el mensaje de éxito junto con el insumo actualizado
                return jsonify({"mensaje": "Insumo actualizado correctamente", "insumo": i})
        # Si no se encontró el insumo
        return jsonify({"error": "Insumo no encontrado"}), 404
    else:
        return jsonify({"error": "Tipo de contenido no soportado"}), 415

@bp_admistracion.route('/insumos/eliminar/<id>', methods=['DELETE'])
def eliminar_insumo(id):
    global insumo
    insumo = [i for i in insumo if i['id'] != id]
    return jsonify({"mensaje": "Insumo eliminado"})

@bp_admistracion.route('/perfil')
def perfil():
    if 'username' not in session or session['role'] != 'cliente':
        return redirect(url_for('login'))
    return render_template('client/perfil_cliente.html')
