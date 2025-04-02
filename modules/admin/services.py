
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
    return Proveedores.query.all()


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
def eliminar_proveedor(proveedor_id):
    try:
        # ? Buscar el proveedor por medio del ID
        proveedor = Proveedores.query.get_or_404(proveedor_id)
        
        # ? Guardamos los datos antes de eliminarlos para poder ocnfirmar la eliminación
        proveedor_info = {
            "id": proveedor.idProveedores,
            "nombre": proveedor.nombre
        }
        
        # * Eliminar el proveedor
        db.session.delete(proveedor)
        db.session.commit()
        
        # * Retornar información sobre el proveedor eliminado
        return proveedor_info
    
    except Exception as e:
        # Hacer rollback en caso de error
        db.session.rollback()
        raise e



# ^ Buscamos un proveedor en específico




# ? Filtamos un porveedor por sus insumos 





# ~ Seccion de proveedores




# ~ Seccion de los insumos




# ~ Seccion de las recetass




# ~ Seccion de los clientes




# ~ Seccion de los usuairos


