
# ? Acá es donde configuraremos las acciónes dentro de la sección de admisntrador

# Importamos la conexión
from database.conexion import db
from sqlalchemy import Enum

# ^ Creamos una clase con el nombre de la tabla para poder utilizarl más adelante


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

# ~ Tabla para las mermas
class Merma(db.Model):
    __tablename__ = 'merma'
    
    idMerma = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipoMerma = db.Column(db.String(15), nullable=False)
    unidadMerma = db.Column(Enum('Gr', 'mL', 'Pz', name='unidad_merma_enum'), nullable=False)
    cantidadMerma = db.Column(db.Integer, nullable=False)
    fechaMerma = db.Column(db.Date, nullable=False)
    inProduccion = db.Column(db.Integer, db.ForeignKey('Produccion.inProduccion'))
    idInsumo = db.Column(db.Integer, db.ForeignKey('insumos.idInsumo'))
    idGalleta = db.Column(db.Integer, db.ForeignKey('galletas.idGalleta'))
    
    produccion = db.relationship('Produccion', backref='mermas')
    insumo = db.relationship('Insumo', backref='mermas')
    galleta = db.relationship('Galleta', backref='mermas')
    
    def to_dict(self):
        return {
            'id': self.idMerma,
            'tipo': self.tipoMerma,
            'unidad': self.unidadMerma,
            'cantidad': self.cantidadMerma,
            'fecha': self.fechaMerma.isoformat(),
            'produccion_id': self.inProduccion,
            'insumo': self.insumo.to_dict() if self.insumo else None,
            'galleta': self.galleta.to_dict() if self.galleta else None
        }

