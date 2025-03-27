from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify

from modules.admin.services import obtener_proveedores
#  ~ Importamos el archvio con el nombre del Blueprint para la sección
from . import bp_production


# ? Ahora vamos a definir las rutas necesarias para el bluprint



# ^ Sección de producción

proveedor = [
    {"id": "0001", "empresa": "19 Hermanos", "telefono": "477-724-5893", 
     "correo": "queso@gmail.com", "direccion": "Paseo de los Insurgentes 362", 
     "productos": "Leche y queso"},
    {"id": "0002", "empresa": "Skibidi", "telefono": "477-123-4567", 
     "correo": "skibidi@gmail.com", "direccion": "Avenida Central 123", 
     "productos": "Bebidas"}
]


insumo = [
    {"id": 1, "lote": 1, "producto": "Huevo", "cantidad": 100, "fechaCaducidad": "2024-11-20", "mermas": 5},
    {"id": 2, "lote": 2, "producto": "Leche", "cantidad": 50, "fechaCaducidad": "2024-11-10", "mermas": 10}
]


# Ruta para el dashboard de producción
@bp_production.route('/produccion')
def produccion():
    if 'username' not in session or session['role'] != 'produccion':
        return redirect(url_for('production.login'))
    return render_template('produccion/produccion.html')





# * Renderiza la página y trae los datos del arreglo
@bp_production.route('/proveedores')
def proveedores():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('production.login'))
    
    # ~ Obtenemos los datos de la tabla de 'proveedores' de la BD
    proveedores = obtener_proveedores()

    return render_template('admin/proveedores.html', proveedor=proveedores)

# * Agregamos un nuevo porveedor
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

# * Edita los datos del porveedor
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

# * Eliminamos un proveedor
@bp_production.route('/proveedores/eliminar/<id>', methods=['DELETE'])
def eliminar_proveedor(id):
    global proveedor
    proveedor = [p for p in proveedor if p['id'] != id]
    return jsonify({"mensaje": "Proveedor eliminado"})

# * Buscar un proveedor
@bp_production.route('/proveedores/<id>', methods=['GET'])
def obtener_proveedor(id):
    for p in proveedor:
        if p['id'] == id:
            return jsonify(p)
    return jsonify({"error": "Proveedor no encontrado"}), 404













@bp_production.route('/recetas')
def recetas():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('production.login'))
    return render_template('admin/recetas.html')

# Ruta para gestionar insumos dentro del archivo rutas de la carpeta producción
@bp_production.route('/insumos')
def insumos():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('production.login'))
    return render_template('admin/insumos.html', insumo=insumo)


@bp_production.route('/insumos/eliminar/<id>', methods=['DELETE'])
def eliminar_insumo(id):
    global insumo
    insumo = [i for i in insumo if i['id'] != id]
    return jsonify({"mensaje": "Insumo eliminado"})


@bp_production.route('/inventario_insumos')
def inventario_insumos():
    if 'username' not in session or session['role'] != 'produccion':
        return redirect(url_for('production.login'))
    return render_template('produccion/mat_prim.html')

@bp_production.route('/inventario_galletas')
def inventario_galletas():
    if 'username' not in session or session['role'] != 'ventas':
        return redirect(url_for('production.login'))
    return render_template('ventas/prod_term.html')



@bp_production.route('/insumos/<id>', methods=['GET'])
def obtener_insumo(id):
    for i in insumo:
        if i['id'] == id:
            return jsonify(i)
    return jsonify({"error": "Insumo no encontrado"}), 404

@bp_production.route('/insumos/editar/<id>', methods=['POST'])
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
