
# ? Acá es donde configuraremos las acciónes dentro de la sección de admisntrador

# Importamos la conexión
from database.conexion import db
 


# ^ Creamos una clase con el nombre de la tabla para poder utilizarl más adelante

# ~ Tabla para los logs de la sección de admin:
# class LogsSistema(db.Model):
#     # ? Nombre de la tabla
#     __tablename__ = 'LogsSistema'

#     # * Columnas de la tabla
#     idLog = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     tipoLog = db.column(db.enmum())


# ~ Tabla para los porveedores
class Proveedores(db.Model):    # ? 
    __tablename__ = 'proveedores'       # Nombre de la tabla

    # Columnas de la tabla 
    idProveedores = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(30), nullable=False)
    telefono = db.Column(db.String(16), nullable=False)
    correo = db.Column(db.String(60), nullable=False)
    direccion = db.Column(db.String(120), nullable=False)
    productosProveedor = db.Column(db.String(300), nullable=False)
    # tipoProveedor = db.Column(db.String(40), nullable=False)

# ~ Tabla para los innsumos (El inventario)


# ~ Tabla para las recetas


# ~ Tabla para los clientes


# ~ Tabla para los usuarios


# ~ Tabla para las galletas más vendidas y el tema de los reportes de las ventas y esas cosas







