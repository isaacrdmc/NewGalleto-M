
# ? Acá es donde configuraremos las acciónes dentro de la sección de admisntrador

# Importamos la conexión
from enum import Enum

from flask_login import UserMixin
from database.conexion import db
 


# ^ Creamos una clase con el nombre de la tabla para poder utilizarl más adelante

# ~ Tabla para los logs de la sección de admin:

# & Clase para los logs del sistema
class TipoLog(Enum):
    Error = 'Error'
    Seguridad = 'Seguridad'
    Acceso = 'Acceso'
    Operacion = 'Operacion'

# & Clase para la tabla de los roles de los usuarios
class Roles(db.Model):
    __tablename__ = 'roles'

    idRolUsuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombreRol = db.Column(db.String(20), nullable=False)
    

# & Clase para la tabla de los usuartios

# 'UserMixin' es una calse que nos permite manejar la sesión de los usuarios 
class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario'

    # *
    idUser = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(20), nullable=False)
    apellP = db.Column(db.String(40), nullable=False)
    apellM = db.Column(db.String(40), nullable=False)
    contrasena = db.Column(db.Strin(255), nullable=False)
    nombreRol = db.Column(db.String(20), nullable=False)

    # * Relación con la tabla de los Logs del sistema
    logs = db.relationship('LogsSistema', backeref='usuario', lazy=True)


# & Clase para la tabla de los logs del sistema
class LogsSistema(db.Model):
    # ? Nombre de la tabla
    __tablename__ = 'LogsSistema'

    # * Columnas de la tabla
    idLog = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipoLog = db.column(db.enmum('Error', 'Seguridad', 'Acceso', 'Operacion'), nullable=False)
    descripcionLog = db.Column(db.Text, nullable=False)
    fechaHora = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp()) # * Fecha y hora actual
    ipOrigen = db.Column(db.String(45), nullable=True) # * Obtenemos la ip del ciente
    
    # 
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuario.idIser'), nullable=False) # * Obtenemos el id del usuario que hizo la acción



"""
CREATE TABLE roles (
	idRolUsuario INT AUTO_INCREMENT PRIMARY KEY,
    nombreRol VARCHAR(20) NOT NULL			-- Especificamos el rol del usuario que puede ser Admin, Cliente, Vendendor o Productor
);

CREATE TABLE usuario(
	idUser INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(10) NOT NULL,		-- Sú nombre
    apellP VARCHAR(40) not null,		-- Sú apellido paterno
    apellM VARCHAR(40) not null,		-- Sú apellido materno
    contrasena VARCHAR(255) NOT NULL,		-- La contrseña cifrada para mayor seguridad
    nombreRol VARCHAR(20) NOT NULL			-- Especificamos el rol del usuario que puede ser Admin, Cliente, Vendendor o Productor
    
    /*idRol INT NOT NULL,
    FOREIGN KEY (idRol) REFERENCES roles(idRolUsuario)*/
);

CREATE TABLE logsSistema (
	idLog INT AUTO_INCREMENT PRIMARY KEY,
    tipoLog ENUM('Error', 'Seguridad', 'Acceso', 'Operacion') NOT NULL,		-- El tipo de log que vamos a manejar
    descripcionLog TEXT NOT NULL,		-- Breve descripción del log
    fechaHora DATETIME NOT NULL DEFAULT current_timestamp,		-- Fecha en la que ocurrio el registro del Log
    ipOrigen VARCHAR(45),		-- NO se que onada acá
    
    idUsuario INT,
    FOREIGN KEY (idUsuario) REFERENCES usuario(idUser)
);
"""


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







