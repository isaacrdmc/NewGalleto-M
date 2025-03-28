
# ? Acá es donde estaremos realizando la soperaciónes lógicas del sistema, como las consultas con la BD

from .models import Proveedores
from database.conexion import db

# ~ Seccion de proveedores

# ^ Creamos las operaciones para Proveedores:
def agregar_proveedor(nombre, telefono, correo, direccion, productosProveedor, tipoProveedor):
    nuevo_proveedor = Proveedores(
        nombre=nombre,
        telefono=telefono,
        correo=correo,
        direccion=direccion,
        productosProveedor=productosProveedor,
        tipoProveedor=tipoProveedor
    )
    # * 
    db.session.add(nuevo_proveedor)
    db.session.commit()


# ^ Vemos todos los datos de la tabla
def obtener_proveedores():
    return Proveedores.query.all()
