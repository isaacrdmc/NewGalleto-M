
# ? Acá es donde estaremos realizando la soperaciónes lógicas del sistema, como las consultas con la BD

from .models import Proveedores
from database.conexion import db

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
def modificar_proveedores():
    return


# ^ Elminar un porveedor  (D)
def eliminar_proveedor():
    return



# ^ Buscamos un proveedor en específico




# ^ Filtamos un porveedor por sus insumos




