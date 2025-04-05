
# ? Acá es donde estaremos realizando la soperaciónes lógicas del sistema, como las consultas con la BD

from flask import request, session
from .models import Proveedores
from database.conexion import db

"""
# ~ Sección para los logs del sistema

# Registro d elos logs al sistema
def registrar_log(tipo_log, descripcion_log, ip_origen):
    
    # * Primero obtenemos la IP del usuario
    ip_origen = request.remote_addr

    # * Ahora creamos el nuevo log:
    nuevo_log = LogsSistema(
        tipoLog=tipo_log,
        descripcionLog=descripcion_log,
        ipOrigen=ip_origen,
        idUsuario=session['idUser'] # * Obtenemos el id del usuario que se encuntra logeado
    )

    # ? Guardamos el nuevo log dentro de la Base de datos
    db.session.add(nuevo_log)  # * Agregamos el nuevo log a la base de datos
    db.session.commit()



# Nos traemos los logs del sistema
def obtener_logs(usuario_id=None, tipo_Log=None, limite=100):
    # ? De primeras nos traemos todos los logs del sistema
    query = LogsSistema.query.order_by(LogsSistema.fechaHora.desc())

    # ? Si se le pase un ID de un usuario mostraremos los logs de este:
    if usuario_id:
        query = query.filter_by(idUsuario=usuario_id)
    
    # ? Si se le pasa un tipo de log, mostraremos los logs de este
    if tipo_Log:
        query = query.filter_by(tipo_Log=tipo_Log)

    # * Retornamos solo 100 logs por defecto, pero podemos modiicar la cantidad de los que queremos ver
    return query.limit(limite).all()


"""


# ~ Seccion de los reportes de las gallletass




# ~ Seccion de proveedores

# ^ Agregamos un proveedor  (C)
def agregar_proveedor(nombre, telefono, correo, direccion, productosProveedor, tipoProveedor):
    # ? Acá es donde crearemos al nuevo proveedor
    nuevo_proveedor = Proveedores(
        nombre=nombre,
        telefono=telefono,  # * --------
        correo=correo,  # * --------
        direccion=direccion,  # * --------
        productosProveedor=productosProveedor,
        tipoProveedor=tipoProveedor
    )
    # * Agregamos al nuevo proveedor a la Base de datos
    db.session.add(nuevo_proveedor)
    db.session.commit()

# ^ Leemos todos los datos de la tabla  (R)
def obtener_proveedores():
    # ? Ordena los datos que se van a mostrar por el producto????
    # return Proveedores.query.order_by(Proveedores.idProveedores.desc()).all()
    
    # ? Ordena los datos que se van a mostrar de fomra aecendente
    # return Proveedores.query.order_by(Proveedores.idProveedores.asc()).all()
    
    # ? Ordena los datos que se van a mostrar de fomra decendente
    return Proveedores.query.order_by(Proveedores.idProveedores.desc()).all()

# ^ Modificar un porveedore  (U)
def actualizar_proveedor(proveedor_id, empresa, telefono, correo, direccion, productos):
    try: 
        # ? En esta sección es donde actualizaremos los datos del cliente
        proveedor = Proveedores.query.get_or_404(proveedor_id)
        proveedor.nombre = empresa
        proveedor.telefono = telefono
        proveedor.correo = correo
        proveedor.direccion = direccion
        proveedor.productosProveedor = productos
        db.session.commit() # * Acá es donde guardamos los cambios en la base de datos
        return proveedor
    
    except Exception as e:
        # ? Si hay un error, hacemos un rollback para deshacer los cambios
        db.session.rollback()
        # raise e

# ^ Elminar un porveedor  (D)
def eliminar_proveedor(proveedor_id):
    try:
        # ? Ahoara vamos a eliminara  un proveedor del sistema
        proveedorEliminar = Proveedores.query.get_or_404(proveedor_id)


        db.session.delete(proveedorEliminar)   # * Eliminamos al proveedor
        db.session.commit()  # * Guardamos los cambios en la base de datos
        
        
        return proveedorEliminar
    except Exception as e:
        # ? Si hay un error, hacemos un rollback para deshacer los cambios
        db.session.rollback()


# # ^ Buscamos un proveedor en específico
# def buscar_proveedore_productos(producto_buscar):
#     # ? Acá es donde buscamos un proveedor por su producto, con que coincida uno de los porudcto 
#     # Algo así como esta consulta de  MySQL:
#     # SELECT *
#     # FROM proveedores 
#     # WHERE productosProveedor LIKE '%Chocolate%';

#     return Proveedores.query.filter(Proveedores.productosProveedor.like(f'%{producto_buscar}%')).all()






# ~ Seccion de proveedores




# ~ Seccion de los insumos




# ~ Seccion de las recetass




# ~ Seccion de los clientes




# ~ Seccion de los usuairos


