from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify

from modules.admin.forms.proveedores import ProveedoresForm
from modules.admin.models import Proveedores
from ..services import agregar_proveedor, obtener_proveedores
from database.conexion import db
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
@bp_admistracion.route('/proveedores', methods=['GET'])
def proveedores():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('production.login'))
    
    # Obtener la lista de proveedores
    lista_proveedores = obtener_proveedores()

    # * Instanciamos al formulario:
    form = ProveedoresForm()

    # Pasar solo los proveedores al contexto de la plantilla
    return render_template('admin/proveedores.html', proveedor=lista_proveedores, form=form)





# * Agregamos un nuevo porveedor
@bp_admistracion.route('/proveedores/agregar', methods=['POST'])
def agregar_proveedor():
    try:

        # * 
        data = request.get_json()

        # * Validamos los datos que se envian:
        if not all(key in data for key  in ['', '', '']):
            return jsonify({'error':'Datos incompletos'}), 400

        # Obtenemos los datos del formuario
        nuevo_Proveedor = Proveedores(
            nombre=data['empresa'],
            telefono=data['telefono'],
            correo=data['correo'],
            direccion=data['direccion'],
            poductos=data['productos']
        )
        # * 
        db.session.add(nuevo_Proveedor)
        db.session.commit()



        #  * Instanciamos la clase del formulario para poder utilizarla dentro del sistema
        # form = ProveedoresForm()

        # ? Verificamos si el formulario  es valido
        # if form.validate_on_submit():
        #     # Obtenemos los datos del formuario
        #     nuevo_Proveedor = Proveedores(
        #         nombre=form.empresa.data,
        #         telefono=form.telefono.data,
        #         correo=form.correo.data,
        #         direccion=form.direccion.data,
        #         poductos=form.productos.data
        #     )
        # # * 
        # db.session.add(nuevo_Proveedor)
        # db.session.commit()




        # ? Si el formulairo es valido y se guarda en la Bd, mostramos el mensaje de exito
        return jsonify({
                "mensaje": "Proveedor agregado", 
                "proveedor": {
                    "id":  nuevo_Proveedor.idProveedores,
                    "empresa":  nuevo_Proveedor.nombre,
                    "telpefono":  nuevo_Proveedor.telefono,
                    "correo":  nuevo_Proveedor.correo,
                    "direccion":  nuevo_Proveedor.direccion,
                    "productos":  nuevo_Proveedor.productosProveedor
                }
            }), 201
    

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
    # ? Si hay errores en la validación mostrmaos que sucedio
    # errors = {field.name: field.errors for field in form if field.errors}
    # return jsonify({"errors": errors}), 400}














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


