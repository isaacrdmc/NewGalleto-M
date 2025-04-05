
# ? Acá es donde configuraremos las acciónes dentro de la sección de admisntrador

# Importamos la conexión
from datetime import datetime
from enum import Enum

from flask_login import UserMixin
from database.conexion import db
 


# ^ Creamos una clase con el nombre de la tabla para poder utilizarl más adelante

# ~ Tabla para los logs de la sección de admin:


# & Clase para la tabla de los roles de los usuarios
class Roles(db.Model):
    __tablename__ = 'roles'

    idRolUsuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombreRol = db.Column(db.String(20), nullable=False, unique=True)

    # * Relación con la tabla de los usuarios
    usuarios = db.relationship('Usuario', backref='rol', lazy=True)
    

# & Clase para la tabla de los usuartios
# 'UserMixin' es una calse que nos permite manejar la sesión de los usuarios 
class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario'
    
    idUser = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellP = db.Column(db.String(40), nullable=False)
    apellM = db.Column(db.String(40), nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    idRol = db.Column(db.Integer, db.ForeignKey('roles.idRolUsuario'), nullable=False)

    # * Relación con la tabla de los Logs del sistema
    logs = db.relationship('LogsSistema', backref='usuario_log', lazy=True)





# Niveles de log personalizados que incluyen los estándares y los específicos del negocio
class LogLevel(Enum):
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'
    SECURITY = 'SECURITY'  # Para eventos específicos de seguridad
    OPERATION = 'OPERATION'  # Para operaciones administrativas

class SystemLog(db.Model):
    """Modelo para registrar logs del sistema en la base de datos"""
    __tablename__ = 'system_logs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    level = db.Column(db.Enum(LogLevel, name='log_level_enum'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    
    # Relación opcional con el usuario
    user = db.relationship('User', backref='logs')
    
    # Datos adicionales en formato JSON
    extra_data = db.Column(db.JSON, nullable=True)

    # ? ???
    def __repr__(self):
        return f'<SystemLog {self.id} [{self.level}] {self.timestamp}>'


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

"""
* Presentación de la empresa (1 diapositiva)
* Descripción del producto o servicio que se ofrece (1 diapositiva)
* Estimación del Costo del Sistema (1 diapositiva)
* Mercado potencial (1 diapositiva)
* Descripción del sistema (2 diapositivas: la primera diapositiva para funciones generales, la segunda diapositiva información general del DASHBORD)
"""

# ~ Tabla para las recetas


# ~ Tabla para los clientes


# ~ Tabla para los usuarios


# ~ Tabla para las galletas más vendidas y el tema de los reportes de las ventas y esas cosas







