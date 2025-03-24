from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
#  ~ Importamos el archvio con el nombre del Blueprint para la sección
from . import bp_production


# ? Ahora vamos a definir las rutas necesarias para el bluprint



# ^ Sección de producción

# Ruta para el dashboard de producción
@bp_production.route('/produccion')
def produccion():
    if 'username' not in session or session['role'] != 'produccion':
        return redirect(url_for('login'))
    return render_template('produccion/produccion.html')

@bp_production.route('/proveedores')
def proveedores():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('admin/proveedores.html', proveedor=proveedor)

@bp_production.route('/proveedores/agregar', methods=['POST'])
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

@bp_production.route('/proveedores/<id>', methods=['GET'])
def obtener_proveedor(id):
    for p in proveedor:
        if p['id'] == id:
            return jsonify(p)
    return jsonify({"error": "Proveedor no encontrado"}), 404

@bp_production.route('/proveedores/editar/<id>', methods=['POST'])
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

@bp_production.route('/proveedores/eliminar/<id>', methods=['DELETE'])
def eliminar_proveedor(id):
    global proveedor
    proveedor = [p for p in proveedor if p['id'] != id]
    return jsonify({"mensaje": "Proveedor eliminado"})

@bp_production.route('/recetas')
def recetas():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('admin/recetas.html')

# Ruta para gestionar insumos
@bp_production.route('/insumos')
def insumos():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('admin/insumos.html', insumo=insumo)

@bp_production.route('/inventario_insumos')
def inventario_insumos():
    if 'username' not in session or session['role'] != 'produccion':
        return redirect(url_for('login'))
    return render_template('produccion/mat_prim.html')

@bp_production.route('/inventario_galletas')
def inventario_galletas():
    if 'username' not in session or session['role'] != 'ventas':
        return redirect(url_for('login'))
    return render_template('ventas/prod_term.html')


