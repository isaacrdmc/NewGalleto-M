import re
from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify

from modules.admin.forms.proveedores import ProveedoresForm
from modules.admin.models import Proveedores
from ..services import actualizar_proveedor, agregar_proveedor, eliminar_proveedor, obtener_proveedores
from database.conexion import db
#  ~ Importamos el archvio con el nombre del Blueprint para la sección
from ...admin import bp_admistracion


# ? En esta sección ira la parte de las rutas para el CRUD de los proveedores:
    # * Agregar nuevos proveedores a la BD
    # * Mostrar los proveedores de la BD
    # * Modificar los proveedores en la BD
    # * Actualizar nuevos proveedores a la BD

# http://127.0.0.1:5000/production/proveedores




# * Renderiza la página y trae los datos del arreglo
# @bp_admistracion.route('/proveedores', methods=['GET'])
@bp_admistracion.route('/proveedores')
def proveedores():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('shared.login'))
    
    # Obtener la lista de proveedores
    lista_proveedores = obtener_proveedores()

    # * Instanciamos al formulario:
    form = ProveedoresForm()

    # Pasar solo los proveedores al contexto de la plantilla
    return render_template('admin/proveedores.html', proveedor=lista_proveedores, form=form)



# ^ Renderiza la página y trae los datos del arreglo        (R)
@bp_admistracion.route('/proveedores/listar', methods=['GET'])
def listar_proveedores():
    if 'username' not in session or session['role'] != 'admin':
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
def agregar_proveedor():
    try:
        data = request.get_json()

        # Validar los datos enviados
        if not all(key in data for key in ['empresa', 'telefono', 'correo', 'direccion', 'productos']):
            return jsonify({'error': 'Datos incompletos'}), 400
        
        # ? Validación adicional del correo
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data['correo']):
            return jsonify({'error': 'Correo electrónico no válido'}), 400
        
        # ? Validación adicional del teléfono (solo números y algunos caracteres especiales)
        if not re.match(r'^[\d\s()+.-]+$', data['telefono']):
            return jsonify({'error': 'Teléfono no válido. Solo números y los caracteres ()+-.'}), 400
        
        
        # ? Sanitización básica de los campos
        # empresa = re.sub(r'[^\w\sñÑáéíóúÁÉÍÓÚüÜ.,-]', '', data['empresa'])[:30]
        # telefono = re.sub(r'[^\d\s()+.-]', '', data['telefono'])[:16]
        # correo = data['correo'][:60]
        # direccion = re.sub(r'[^\w\sñÑáéíóúÁÉÍÓÚüÜ#.,-]', '', data['direccion'])[:120]
        # productos = re.sub(r'[^\w\sñÑáéíóúÁÉÍÓÚüÜ.,;-]', '', data['productos'])[:300]
        

        # Crear un nuevo proveedor
        nuevo_proveedor = Proveedores(
            nombre=data['empresa'],
            telefono=data['telefono'],
            correo=data['correo'],
            direccion=data['direccion'],
            productosProveedor=data['productos']
        )
        db.session.add(nuevo_proveedor)
        db.session.commit()

        # ? Retornamos el nuevo proveedor en formato JSON
        return jsonify({
            # ? Mensaje de exito (Mensaje importante del 'jsonify')
            "mensaje": "Proveedor agregado",

            # & Datos del proveedor 
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


# ~ Obtener un proveedor:
@bp_admistracion.route('/proveedores/obtener/<int:id>', methods=['GET'])
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