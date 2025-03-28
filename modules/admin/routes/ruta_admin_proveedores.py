

from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
from ..services import agregar_proveedor, obtener_proveedores
#  ~ Importamos el archvio con el nombre del Blueprint para la sección
from ...admin import bp_admistracion


# ? En esta sección ira la parte de las rutas para el CRUD de los proveedores:
    # * Agregar nuevos proveedores a la BD
    # * Mostrar los proveedores de la BD
    # * Modificar los proveedores en la BD
    # * Actualizar nuevos proveedores a la BD

# http://127.0.0.1:5000/production/proveedores


# * nueva ruta, ruta para el CRUD de los proveedores
@bp_admistracion.route('/agregarProveedor')
def agregarProv():
    proveedoresNuevos=agregar_proveedor()
    return render_template('admin/index.html', proveedores=proveedoresNuevos)



# * Renderiza la página y trae los datos del arreglo
@bp_admistracion.route('/proveedores')
def proveedores():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('production.login'))
    
    # ~ Obtenemos los datos de la tabla de 'proveedores' de la BD
    proveedores = obtener_proveedores()

    return render_template('admin/proveedores.html', proveedor=proveedores)

# * Agregamos un nuevo porveedor
@bp_admistracion.route('/proveedores/agregar', methods=['POST'])
def agregar_proveedor():
    datos = request.get_json()
    nuevo_proveedor = {
        "id": str(len(proveedor) + 1).zfill(4),  # Generar ID automático
        "empresa": datos['empresa'],
        "telefono": datos['telefono'],
        "correo": datos['correo'],
        "direccion": datos['direccion'],
        "productos": datos['productos']
    }
    proveedor.append(nuevo_proveedor)
    return jsonify({"mensaje": "Proveedor agregado", "proveedor": nuevo_proveedor})

# * Edita los datos del porveedor
@bp_admistracion.route('/proveedores/editar/<id>', methods=['POST'])
def editar_proveedor(id):
    if request.is_json:
        datos = request.get_json()  # Obtener los datos JSON del cuerpo de la solicitud
        for p in proveedor:  # Asegúrate de que el nombre de la lista sea "proveedores"
            if p['id'] == id:
                # Usar los datos del JSON recibido para actualizar el proveedor
                p['empresa'] = datos['empresa']
                p['telefono'] = datos['telefono']
                p['correo'] = datos['correo']
                p['direccion'] = datos['direccion']
                p['productos'] = datos['productos']
                # Retornar el mensaje de éxito junto con el proveedor actualizado
                return jsonify({"mensaje": "Proveedor actualizado correctamente", "proveedor": p})
        # Si no se encontró el proveedor
        return jsonify({"error": "Proveedor no encontrado"}), 404
    else:
        return jsonify({"error": "Tipo de contenido no soportado"}), 415

# * Eliminamos un proveedor
@bp_admistracion.route('/proveedores/eliminar/<id>', methods=['DELETE'])
def eliminar_proveedor(id):
    global proveedor
    proveedor = [p for p in proveedor if p['id'] != id]
    return jsonify({"mensaje": "Proveedor eliminado"})

# * Buscar un proveedor
@bp_admistracion.route('/proveedores/<id>', methods=['GET'])
def obtener_proveedor(id):
    for p in proveedor:
        if p['id'] == id:
            return jsonify(p)
    return jsonify({"error": "Proveedor no encontrado"}), 404


