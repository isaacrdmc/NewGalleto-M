

from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
from ..services import agregar_proveedor, obtener_proveedores
#  ~ Importamos el archvio con el nombre del Blueprint para la sección
from ...admin import bp_admistracion


# ? En esta sección ira la parte de las rutas para el CRUD de los insumos que es el inventario:
    # * Agregar nuevos proveedores a la BD
    # * Mostrar los proveedores de la BD
    # * Modificar los proveedores en la BD
    # * Actualizar nuevos proveedores a la BD

    # * Alerta de los que nos quedan pocos


# http://127.0.0.1:5000/production/insumos



 


# Ruta para gestionar insumos dentro del archivo rutas de la carpeta producción
@bp_admistracion.route('/insumos')
def insumos():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('production.login'))
    return render_template('admin/insumos.html', insumo=insumo)


@bp_admistracion.route('/insumos/eliminar/<id>', methods=['DELETE'])
def eliminar_insumo(id):
    global insumo
    insumo = [i for i in insumo if i['id'] != id]
    return jsonify({"mensaje": "Insumo eliminado"})


@bp_admistracion.route('/inventario_insumos')
def inventario_insumos():
    if 'username' not in session or session['role'] != 'produccion':
        return redirect(url_for('production.login'))
    return render_template('produccion/mat_prim.html')

@bp_admistracion.route('/inventario_galletas')
def inventario_galletas():
    if 'username' not in session or session['role'] != 'ventas':
        return redirect(url_for('production.login'))
    return render_template('ventas/prod_term.html')


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


@bp_admistracion.route('/insumos/agregar', methods=['POST'])
def agregar_insumo():
    datos = request.get_json()
    nuevo_insumo = {
        "id": str(len(insumo) + 1).zfill(4),  # Generar ID automático
        "lote": datos['lote'],
        "producto": datos['producto'],
        "cantidad": datos['cantidad'],
        "fechaCaducidad": datos['fechaCaducidad'],
        "mermas": datos['mermas']
    }
    insumo.append(nuevo_insumo)
    return jsonify({"mensaje": "Insumo agregado", "insumo": nuevo_insumo})

