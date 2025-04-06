
# ? Acá es donde estaremos realizando la soperaciónes lógicas del sistema, como las consultas con la BD

from .models import Proveedores
from database.conexion import db






# ~ Seccion de los reportes de las gallletass




# ~ Sección de los logs del sistema


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
        tipoProveedor=tipoProveedor,  # * --------
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


