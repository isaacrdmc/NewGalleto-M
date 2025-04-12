
# ? Acá es donde configuraremos las acciónes dentro de la sección de admisntrador

# Importamos la conexión
from database.conexion import db
from sqlalchemy import Enum

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


# ~ Tabla para las galletas más vendidas y el tema de los reportes de las ventas y esas cosas

# ~ Tabla para las transacciones de compra
class TransaccionCompra(db.Model):
    __tablename__ = 'transaccionCompra'
    
    idTransaccionCompra = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fechaCompra = db.Column(db.Date, nullable=False)
    totalCompra = db.Column(db.Numeric(10,2))
    idProveedor = db.Column(db.Integer, db.ForeignKey('proveedores.idProveedores'), nullable=False)
    
    proveedor = db.relationship('Proveedores', backref='compras')
    detalles = db.relationship('DetalleCompraInsumo', backref='compra', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.idTransaccionCompra,
            'fecha': self.fechaCompra.isoformat(),
            'total': float(self.totalCompra) if self.totalCompra else None,
            'proveedor': self.proveedor.to_dict() if self.proveedor else None,
            'detalles': [d.to_dict() for d in self.detalles]
        }

# ~ Tabla para los detalles de la compra
class DetalleCompraInsumo(db.Model):
    __tablename__ = 'detalleCompraInsumo'
    __table_args__ = {'extend_existing': True}  # ? Permite sobrescribir la tabla si ya existe
    
    idetalleCompraInsumo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cantCajas = db.Column(db.Integer, nullable=False)
    cantUnidadesXcaja = db.Column(db.Integer, nullable=False)
    cantMermaPorUnidad = db.Column(db.Integer, nullable=False)
    CostoPorCaja = db.Column(db.Numeric(10,2), nullable=False)
    costoUnidadXcaja = db.Column(db.Numeric(10,2), nullable=False)
    unidadInsumo = db.Column(Enum('Gr', 'mL', 'Pz', name='unidad_insumo_enum'), nullable=False)
    fechaRegistro = db.Column(db.Date, nullable=False)
    fechaCaducidad = db.Column(db.Date, nullable=False)
    idCompra = db.Column(db.Integer, db.ForeignKey('transaccionCompra.idTransaccionCompra'), nullable=False)
    idInsumo = db.Column(db.Integer, db.ForeignKey('insumos.idInsumo'), nullable=False)
    
    insumo = db.relationship('Insumo', backref='compras')
    
    def to_dict(self):
        return {
            'id': self.idetalleCompraInsumo,
            'cajas': self.cantCajas,
            'unidades_por_caja': self.cantUnidadesXcaja,
            'merma_por_unidad': self.cantMermaPorUnidad,
            'costo_caja': float(self.CostoPorCaja),
            'costo_unidad': float(self.costoUnidadXcaja),
            'unidad': self.unidadInsumo,
            'fecha_registro': self.fechaRegistro.isoformat(),
            'fecha_caducidad': self.fechaCaducidad.isoformat(),
            'insumo': self.insumo.to_dict() if self.insumo else None
        }


class Notificacion(db.Model):
    __tablename__ = 'notificaciones'
    __table_args__ = {'extend_existing': True}  # ? Permite sobrescribir la tabla si ya existe
    


    id = db.Column('idNotificaciónes', db.Integer, primary_key=True)
    tipo = db.Column('tipoNotificacion', db.Enum(
        'Caducidad Insumo', 
        'Caducidad Galleta', 
        'Bajo Inventario', 
        'Solicitud Produccion', 
        'No hay suficientes inusmos de'), nullable=False)
    mensaje = db.Column('mensajeNotificar', db.String(255))
    fecha_creacion = db.Column('fechaCreacion', db.DateTime, default=db.func.current_timestamp())
    fecha_visto = db.Column('fechaVisto', db.DateTime, nullable=True)
    estado = db.Column('estatus', db.Enum('Nueva', 'Vista', 'Resuelto'), default='Nueva')
    
    # Relaciones
    id_usuario = db.Column('idUsuario', db.Integer, db.ForeignKey('usuarios.idUser'))
    id_insumo = db.Column('idInsumo', db.Integer, db.ForeignKey('insumos.idInsumo'))
    id_galleta = db.Column('idGalleta', db.Integer, db.ForeignKey('galletas.idGalleta'))
    
    usuario = db.relationship('User', backref='notificaciones')
    insumo = db.relationship('Insumo', backref='notificaciones')
    galleta = db.relationship('Galleta', backref='notificaciones')
    
    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'mensaje': self.mensaje,
            'fecha_creacion': self.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_creacion else None,
            'fecha_visto': self.fecha_visto.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_visto else None,
            'estado': self.estado,
            'id_usuario': self.id_usuario,
            'id_insumo': self.id_insumo,
            'id_galleta': self.id_galleta
        }

# ~ Tabla para los logs del sistema
# ? Esta tabla se encarga de almacenar los logs del sistema, como errores, accesos y operaciones realizadas por los usuarios.    
class LogSistema(db.Model):
    __tablename__ = 'logsSistema'
    
    idLog = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipoLog = db.Column(Enum('Error', 'Seguridad', 'Acceso', 'Operacion', name='tipo_log_enum'), nullable=False)
    descripcionLog = db.Column(db.Text, nullable=False)
    fechaHora = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    ipOrigen = db.Column(db.String(45))
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuarios.idUser'))
    
    # Relaciones
    usuario = db.relationship('User', backref='logs')
