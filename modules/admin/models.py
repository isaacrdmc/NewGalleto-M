
# ? Acá es donde configuraremos las acciónes dentro de la sección de admisntrador

# Importamos la conexión
from database.conexion import db

# ~ Creamos una clase con el nombre de la tabla para poder utilizarl más adelante
class Proveedores():
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(30), nullable=False)
    telefono = db.Column(db.String(16), nullable=False)
    correo = db.Column(db.String(60), nullable=False)
    direccion = db.Column(db.String(120), nullable=False)
    productosProveedor = db.Column(db.String(300), nullable=False)
    tipoProveedor = db.Column(db.String(34), nullable=False)




"""
idProveedores INT AUTO_INCREMENT PRIMARY KEY,
nombre VARCHAR(30) NOT NULL,		-- Nombre del proveedore
telefono VARCHAR(16) NOT NULL,		-- El número del provvedor
correo VARCHAR(60) NOT NULL,		-- El correo del provvedor
direccion VARCHAR(120) NOT NULL, 	-- La dirección de donde se encuentra el proveedor
productosProveedor VARCHAR(300) NOT NULL,	-- Los tipos de productos que nos vende el proveedor
tipoProveedor VARCHAR(40) NOT NULL	-- Greenitarios, Sanz, etc
"""
