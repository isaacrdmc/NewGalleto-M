import re
from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
from modules.admin.forms.proveedores import ProveedoresForm
from modules.admin.models import Proveedores
from modules.admin.routes.ruta_admin_dashboard import admin_required
from ..services import actualizar_proveedor, agregar_proveedor, eliminar_proveedor, obtener_proveedores
from database.conexion import db
#  ~ Importamos el archvio con el nombre del Blueprint para la sección
from flask_login import login_required, current_user
from ...admin import bp_admistracion


# ? En esta sección ira la parte de las rutas para el CRUD de los proveedores:
    # * Agregar nuevos proveedores a la BD
    # * Mostrar los proveedores de la BD
    # * Modificar los proveedores en la BD
    # * Actualizar nuevos proveedores a la BD

# http://127.0.0.1:5000/production/proveedores


# * nueva ruta, ruta para el CRUD de los proveedores
@bp_admistracion.route('/agregarProveedor')
@login_required
def agregarProv():
    proveedoresNuevos=agregar_proveedor()
    return render_template('admin/index.html', proveedores=proveedoresNuevos)
 

# * Renderiza la página y trae los datos del arreglo
# @bp_admistracion.route('/proveedores', methods=['GET'])
@bp_admistracion.route('/proveedores')
@admin_required
def proveedores():
    lista_proveedores = obtener_proveedores()
    form = ProveedoresForm()
    return render_template('admin/proveedores.html', proveedor=lista_proveedores, form=form)



# ^ Renderiza la página y trae los datos del arreglo        (R)
@bp_admistracion.route('/proveedores/listar', methods=['GET'])
@admin_required
def listar_proveedores():
    if current_user.rol.nombreRol != 'Administrador':
        return jsonify({"error": "No autorizado"}), 403

    try:
        # * Obtener la lista de proveedores
        lista_proveedores = obtener_proveedores()
        if not lista_proveedores:
            return jsonify({"mensaje": "No hay proveedores registrados"}), 200
        
        # ? Convertimos la lista de proveedores a un fomrato de tipo JSON
        proveedores_json = [
            {
                "id": p.idProveedores,
                "nombre": p.nombre,
                "telefono": p.telefono,
                "correo": p.correo,
                "direccion": p.direccion,
                "productosProveedor": p.productosProveedor
            }
            for p in lista_proveedores
        ]
        return jsonify(proveedores_json), 200
    
    except Exception as e:
        # Loguear el error para depuración
        print(f"Error al listar proveedores: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


# ^ Agregamos un nuevo porveedor        (C)
@bp_admistracion.route('/proveedores/agregar', methods=['POST'])
@admin_required
def agregar_proveedor():
    try:
        data = request.get_json()

        if not all(key in data for key in ['empresa', 'telefono', 'correo', 'direccion', 'productos']):
            return jsonify({'error': 'Datos incompletos'}), 400
        
        # Validación de correo electrónico
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data['correo']):
            return jsonify({'error': 'Correo electrónico no válido'}), 400
        
        # Validación de teléfono
        if not re.match(r'^[\d\s()+.-]+$', data['telefono']):
            return jsonify({'error': 'Teléfono no válido. Solo números y los caracteres ()+-.'}), 400
        
        nuevo_proveedor = Proveedores(
            nombre=data['empresa'],
            telefono=data['telefono'],
            correo=data['correo'],
            direccion=data['direccion'],
            productosProveedor=data['productos']
        )
        db.session.add(nuevo_proveedor)
        db.session.commit()

        return jsonify({
            "mensaje": "Proveedor agregado",
            "proveedor": {
                "id": nuevo_proveedor.idProveedores,
                "empresa": nuevo_proveedor.nombre,
                "telefono": nuevo_proveedor.telefono,
                "correo": nuevo_proveedor.correo,
                "direccion": nuevo_proveedor.direccion,
                "productos": nuevo_proveedor.productosProveedor
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



# ^ Edita los datos del porveedor        (U)
# @bp_admistracion.route('/proveedores/editar/<int:id>', methods=['PUT'])
@bp_admistracion.route('/proveedores/editar/<int:id>', methods=['POST'])
@admin_required
def editar_proveedor(id):
    try:
        data = request.get_json()
        
        # Validación básica
        if not all(key in data for key in ['empresa', 'telefono', 'correo']):
            return jsonify({'error': 'Datos requeridos faltantes'}), 400
        
        # Usamos la función de servicio para actualizar el porveedor
        proveedor = actualizar_proveedor(
            proveedor_id=id,
            empresa=data['empresa'],
            telefono=data['telefono'],
            correo=data['correo'],
            direccion=data.get('direccion', ''),  # Usamos get() para campos opcionales
            productos=data.get('productos', '')
        )
        
        # ? Retornamos al porveedor actualizandolo en fomrato JSON
        return jsonify({
            # ? Mensaje de exito (Mensaje importante del 'jsonify')
            "mensaje": "Proveedor actualizado",  

            # & Datos del proveedor 
            "proveedor": {
                "id": proveedor.idProveedores,
                "nombre": proveedor.nombre,
                "telefono": proveedor.telefono,
                "correo": proveedor.correo
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ^ Eliminamos un proveedor        (D)
@bp_admistracion.route('/proveedores/eliminar/<int:id>', methods=['POST'])
@admin_required
def eliminar_proveedor_route(id):
    try:
        # ? Usamos la función de servicio para eliminar el proveedor
        proveedorEliminar = eliminar_proveedor(id)

        # * Retornamos el mensaje de exito
        return jsonify({
            # ? Mensaje de exito (Mensaje importante del 'jsonify')
            "mensaje": "Proveedor eliminado",   

            # & Datos del proveedor eleiminado
            "proveedor": {
                "id": proveedorEliminar.idProveedores,
                "nombre": proveedorEliminar.nombre,
                "telefono": proveedorEliminar.telefono,
                "correo": proveedorEliminar.correo
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    


# ^ Buscar un proveedor dentro de la BD        (Otro)
@bp_admistracion.route('/proveedores/buscar', methods=['GET'])
@admin_required
def buscar_proveedor_route():
    if 'username' not in session or session['role'] != 'admin':
        return jsonify({"error": "No autorizado"}), 403
    
    # * la respuesa la almacenamos en una variable
    producto = request.args.get('producto', '').strip()

    # ? Validmos al proveedor
    if not producto:
        return jsonify({"error": "No se ha proporiconado un producto a buscar"}), 400
    
    try: 
        # ? Usamos la función de servicio para buscar el proveedor
        proveedores = buscar_proveedor_route(producto)

        # * Validamos la existencia del porveedor
        if not proveedores:
            return jsonify({"mensaje": f"No se han encontrado proveedores con el {producto}"}), 404

        # ? Entregamos al ista de los porveedore en formato JSON
        proveedores_json = [
            {
                "id": p.idProveedores,
                "nombre": p.nombre,
                "telefono": p.telefono,
                "correo": p.correo,
                "direccion": p.direccion,
                "productosProveedor": p.productosProveedor
            }
            for p in proveedores
        ]
        
        return jsonify(proveedores_json), 200

    except Exception as e:
        print(f"Error al buscar proveedores: {e}")
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500



# ~ Obtener un proveedor:
@bp_admistracion.route('/proveedores/obtener/<int:id>', methods=['GET'])
@admin_required
def obtener_proveedor(id):
    try:
        proveedor = Proveedores.query.get_or_404(id)
        return jsonify({
            "idProveedores": proveedor.idProveedores,
            "nombre": proveedor.nombre,
            "telefono": proveedor.telefono,
            "correo": proveedor.correo,
            "direccion": proveedor.direccion,
            "productosProveedor": proveedor.productosProveedor
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500