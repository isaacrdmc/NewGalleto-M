
# ? Acá es donde estaremos realizando la soperaciónes lógicas del sistema, como las consultas con la BD

from .models import Proveedores
from database.conexion import db






# ~ Seccion de los reportes de las gallletass




# ~ Seccion de proveedores
 
# ^ Agregamos un proveedor  (C)
def agregar_proveedor(nombre, telefono, correo, direccion, productosProveedor, tipoProveedor):
    nuevo_proveedor = Proveedores(
        nombre=nombre,
        telefono=telefono,  # * --------
        correo=correo,  # * --------
        direccion=direccion,  # * --------
        productosProveedor=productosProveedor,
        tipoProveedor=tipoProveedor
    )
    # * 
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
        proveedor = Proveedores.query.get_or_404(proveedor_id)
        proveedor.nombre = empresa
        proveedor.telefono = telefono
        proveedor.correo = correo
        proveedor.direccion = direccion
        proveedor.productosProveedor = productos
        db.session.commit()
        return proveedor
    
    except Exception as e:
        db.session.rollback()
        # raise e


# ^ Elminar un porveedor  (D)
def eliminar_proveedor():
    return



# ^ Buscamos un proveedor en específico




# ? Filtamos un porveedor por sus insumos 





# ~ Seccion de proveedores




# ~ Seccion de los insumos




# ~ Seccion de las recetass




# ~ Seccion de los clientes




# ~ Seccion de los usuairos


