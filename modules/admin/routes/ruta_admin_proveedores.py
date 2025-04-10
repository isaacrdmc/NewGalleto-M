import re
from flask import current_app, render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
 
from modules.admin.forms.proveedores import ProveedoresForm
from modules.admin.models import Proveedores
# from services.log_service import LogService
from ..services import actualizar_proveedor, agregar_proveedor, eliminar_proveedor, obtener_proveedores
from database.conexion import db
#  ~ Importamos el archvio con el nombre del Blueprint para la sección
from flask_login import login_required, current_user
from ...admin import bp_admistracion
# from ...logs.log_config import loggerPersonalizado
# from ...logs.log_config import loggerPersonalizado

# * nueva ruta, ruta para el CRUD de los proveedores
@bp_admistracion.route('/agregarProveedor')
@login_required
def agregarProv():
    proveedoresNuevos=agregar_proveedor()
    current_app.logger.warning(f'Intento de acceso no autorizado a la página de clientes por {current_user.username}')
    return render_template('admin/index.html', proveedores=proveedoresNuevos)
 

# * Renderiza la página y trae los datos del arreglo
# @bp_admistracion.route('/proveedores', methods=['GET'])
@bp_admistracion.route('/proveedores')
@login_required
def proveedores():
    if current_user.rol.nombreRol != 'Administrador':
        # 
        current_app.logger.error(f'Acceso no autorizado a la página de proveedores poer el usuario')
        return redirect(url_for('shared.login'))

    # Registrar acceso exitoso
    current_app.logger.info(
        f"Acceso a la sección de proveedores",
        extra={
            'user': current_user.username,
            'tipo_log': 'ACCESS'
        }
    )

    # Obtener la lista de proveedores
    lista_proveedores = obtener_proveedores()
    form = ProveedoresForm()

    return render_template('admin/proveedores.html', proveedor=lista_proveedores, form=form)



# ^ Renderiza la página y trae los datos del arreglo        (R)
@bp_admistracion.route('/proveedores/listar', methods=['GET'])
@login_required
def listar_proveedores():
    if current_user.rol.nombreRol != 'Administrador':
        current_app.logger.error(f'Acceso no autorizado a listar proveedores por el usuario')
        return jsonify({"error": "No autorizado"}), 403

    try:
        # Registrar operación
        current_app.logger.info(
            "Consulta de lista de proveedores",
            extra={
                'user': current_user.username,
                'tipo_log': 'OPERATION'
            }
        )
        
        # Obtener la lista de proveedores
        lista_proveedores = obtener_proveedores()
        if not lista_proveedores:
            current_app.logger.warning(f'No hay proveedores registrados')
            return jsonify({"mensaje": "No hay proveedores registrados"}), 200
        

        current_app.logger.info(f'Acceso a la lista de proveedores por {current_user.username}')
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

        current_app.logger.info(f'Lista de proveedores obtenida por {current_user.username}')
        return jsonify(proveedores_json), 200
    
    except Exception as e:
        # Loguear el error para depuración
        print(f"Error al listar proveedores: {e}")
        current_app.logger.error(f'Error al listar proveedores_ {e}')
        return jsonify({"error": "Error interno del servidor"}), 500






# ^ Agregamos un nuevo porveedor        (C)
@bp_admistracion.route('/proveedores/agregar', methods=['POST'])
@login_required
def agregar_proveedor():
    # ~ Verificamos sus credenciales y gauradmos el log
    if 'username' not in session or session['role'] != 'admin':
        current_app.logger.warning(
            "Intento de acceso no autorizado a la creación de proveedores",
            extra={
                'user': current_user.username if hasattr(current_user, 'username') else None,
                'ip': request.remote_addr,
                'tipo_log': 'SECURITY'
            }
        )
        return jsonify({"error": "No autorizado"}), 403

    try:
        data = request.get_json()

        # Validar los datos enviados
        if not all(key in data for key in ['empresa', 'telefono', 'correo', 'direccion', 'productos']):
            current_app.logger.error(
                "Datos incompletos al intentar agregar proveedor",
                extra={
                    'data': data,
                    'user': current_user.username,
                    'tipo_log': 'ERROR'
                }
            )
            return jsonify({'error': 'Datos incompletos'}), 400
        
        # ? Validación adicional del correo
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data['correo']):
            current_app.logger.error(
                "Correo electrónico inválido al agregar proveedor",
                extra={
                    'correo': data['correo'],
                    'user': current_user.username,
                    'tipo_log': 'ERROR'
                }
            )
            return jsonify({'error': 'Correo electrónico no válido'}), 400
        
        # ? Validación adicional del teléfono (solo números y algunos caracteres especiales)
        if not re.match(r'^[\d\s()+.-]+$', data['telefono']):
            current_app.logger.error(
                "Teléfono inválido al agregar proveedor",
                extra={
                    'telefono': data['telefono'],
                    'user': current_user.username,
                    'tipo_log': 'ERROR'
                }
            )
            return jsonify({'error': 'Teléfono no válido. Solo números y los caracteres ()+-.'}), 400
        

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


        current_app.logger.infor(f'Proveedor {nuevo_proveedor.nombre} agregado correctamente por {current_user.username}')

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
        current_app.logger.error(f'Error al agregar proveedor: {str(e)}')
        return jsonify({"error": str(e)}), 500



# ^ Edita los datos del porveedor        (U)
# @bp_admistracion.route('/proveedores/editar/<int:id>', methods=['PUT'])
@bp_admistracion.route('/proveedores/editar/<int:id>', methods=['POST'])
@login_required
def editar_proveedor(id):
    # ~ Verificamos sus credenciales
    if 'username' not in session or session['role'] != 'admin':
        current_app.logger.warning(
            "Intento de acceso no autorizado a la actualización de proveedores",
            extra={
                'user': current_user.username if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated else None,
                'ip': request.remote_addr,
                'tipo_log': 'SECURITY',
                'proveedor_id': id
            }
        )      # Obtenemos el usuario para registrar jjunto ocn el log
        return jsonify({"error": "No autorizado"}), 403
    
    try:
        # ? Obtenemos el id del usuairo para enviarlo junto con el log:
        proveedor_actual = Proveedores.query.get(id)
        if not proveedor_actual:
            current_app.logger.error(
                "Intento de editar proveedor inexistente",
                extra={
                    'proveedor_id': id,
                    'user': current_user.username if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated else None,
                    'tipo_log': 'ERROR'
                }
            )
            return jsonify({"error": "Proveedor no encontrado#}), 404"})
        
        # * Guardamos el nombre anterior para el log
        nombre_anterior = proveedor_actual.nombre
        


        data = request.get_json()
        
        # Validación básica
        if not all(key in data for key in ['empresa', 'telefono', 'correo']):
            current_app.logger.error(
                "Datos incompletos al intentar modificar proveedor",
                extra={
                    'proveedor_id': id,
                    'data': data,
                    'user': current_user.username,
                    'tipo_log': 'ERROR'
                }
            )
            return jsonify({'error': 'Datos requeridos faltantes'}), 400
        
        # ? Usamos la función de servicio para actualizar el porveedor
        proveedor = actualizar_proveedor(
            proveedor_id=id,
            empresa=data['empresa'],
            telefono=data['telefono'],
            correo=data['correo'],
            direccion=data.get('direccion', ''),  # Usamos get() para campos opcionales
            productos=data.get('productos', '')
        )

        current_app.logger.info(f'Proveedor {proveedor.nombre} editado correctamente por {current_user.username}')
        
        # ? Retornamos al porveedor actualizandolo en fomrato JSON
        return jsonify({
            # ? Mensaje de exito (Mensaje importante del 'jsonify')
            "mensaje": "Proveedor actualizado",  

            # & Datos del proveedor 
            "proveedor": {
                "id": proveedor.idProveedores,
                "nombre": proveedor.nombre,
                "telefono": proveedor.telefono,
                "correo": proveedor.correo,
                'direccion': proveedor.direccion,
                'productos': proveedor.productosProveedor
            }
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error al editar proveedor: {str(e)}')
        return jsonify({"error": str(e)}), 500


# ^ Eliminamos un proveedor        (D)
# @bp_admistracion.route('/proveedores/eliminar/<int:id>', methods=['DELETE'])
@bp_admistracion.route('/proveedores/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_proveedor_route(id):
    try:
        # ? Usamos la función de servicio para eliminar el proveedor
        proveedorEliminar = eliminar_proveedor(id)

        current_app.logger.info(f'Proveedor {proveedorEliminar.nombre} eliminado correctamente po {current_user.username}')

        # * Registramos el log de la operación exitosa
        current_app.logger.info(
            "Proveedor eliminado",
            extra={
                'proveedor_id': id,
                'proveedor_info': proveedo_infor,
                'user': current_user.username,
                'tipo_log': 'OPERATION'
            }
        )

        # ? RETORNAMOS EL MENSAJE DE EXITO
        return jsonify({
            "mensaje": "Proveedor eliminado",       # ? Mensaje de exito (Mensaje importante del 'jsonify')
            "proveedor": {  # & Datos del proveedor eleiminado
                "id": proveedorEliminar.idProveedores,
                "nombre": proveedorEliminar.nombre,
                "telefono": proveedorEliminar.telefono,
                "correo": proveedorEliminar.correo
            }
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error al eliminar proveedor: {str(e)}')
        return jsonify({"error": str(e)}), 500
    


# ^ Buscar un proveedor dentro de la BD        (Otro)@bp_admistracion.route('/proveedores/buscar', methods=['GET'])
def buscar_proveedor_route():
    if 'username' not in session or session['role'] != 'admin':
        current_app.logger.error(f'Acceso no autorizado a la búsqueda de proveedores por el usuario')
        return jsonify({"error": "No autorizado"}), 403
    
    producto = request.args.get('producto', '').strip()

    if not producto:
        current_app.logger.warning(
            "Búsqueda de proveedor sin parámetros",
            extra={
                'user': current_user.username,
                'tipo_log': 'WARNING'
            }
        )
        return jsonify({"error": "No se ha proporcionado un producto a buscar"}), 400
    
    try: 
        proveedores = buscar_proveedor_route(producto)


        # * Validamos la existencia del porveedor
        if not proveedores:
            current_app.logger.warning(f'No se ha encontrado el porveedor {producto} por {current_user.username}')
            return jsonify({"mensaje": f"No se han encontrado proveedores con el {producto}"}), 404

        current_app.logger.infor(f'Proveedor {producto} encontrado por {current_user.username}')
        
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
        
        current_app.logger.info(
            "Búsqueda de proveedores exitosa",
            extra={
                'producto_buscado': producto,
                'resultados': len(proveedores),
                'user': current_user.username,
                'tipo_log': 'INFO'
            }
        )
        
        return jsonify(proveedores_json), 200

    except Exception as e:
        print(f"Error al buscar proveedores: {e}")
        current_app.logger.error(f'Error al buscar proveedores: {str(e)}')
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500



# ~ Obtener un proveedor:
@bp_admistracion.route('/proveedores/obtener/<int:id>', methods=['GET'])
# def obtener_proveedor_route(id):
def obtener_proveedor(id):
    try:
        proveedor = Proveedores.query.get_or_404(id)

        current_app.logger.info(f'Proveedor {proveedor.nombre} obtenido correctamente por {current_user.username}')

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