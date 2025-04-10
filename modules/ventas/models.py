# ventas/models.py
from database.conexion import db
from sqlalchemy import Enum


# Tablas de la base de datos para ventas y detalles de ventas
class Venta(db.Model):
    __tablename__ = 'ventas'
    
    idVenta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fechaVentaGalleta = db.Column(db.Date, nullable=False)
    totalVenta = db.Column(db.Numeric(10,2), nullable=False)
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuarios.idUser'), nullable=False)
    
    # Relaciones
    usuario = db.relationship('User', foreign_keys=[idUsuario])
    detalles = db.relationship('DetalleVenta', backref='venta', cascade='all, delete-orphan')

class DetalleVenta(db.Model):
    __tablename__ = 'detallesVentas'
    
    idDetalleVenta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cantGalletasVendidas = db.Column(db.Integer, nullable=False)
    precioUnitario = db.Column(db.Numeric(10,2), nullable=False)
    formaVenta = db.Column(Enum('Por pieza', 'Por peso', 'por paquete/caja', name='forma_venta_enum'), nullable=False)
    cantidadGalletas = db.Column(db.Integer)
    pesoGramos = db.Column(db.Numeric(10,2))
    idGalleta = db.Column(db.Integer, db.ForeignKey('galletas.idGalleta'), nullable=False)
    idVenta = db.Column(db.Integer, db.ForeignKey('ventas.idVenta'), nullable=False)
    
    # Relaciones
    galleta = db.relationship('Galleta')
    # La relación con Venta ahora es a través de backref

    def to_dict(self):
        return {
            'id': self.idDetalleVenta,
            'cantidad': self.cantGalletasVendidas,
            'precio': float(self.precioUnitario),
            'forma_venta': self.formaVenta,
            'cantidad_galletas': self.cantidadGalletas,
            'peso': float(self.pesoGramos) if self.pesoGramos else None,
            'galleta': self.galleta.to_dict() if self.galleta else None,
            'venta': self.venta.idVenta if self.venta else None  # Referencia a la venta
        }


# Tabla para almacenar la información de las facturas
class Factura(db.Model):
    __tablename__ = 'facturacion'
    
    idFactura = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fechaFactura = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    totalCompra = db.Column(db.Numeric(10,2), nullable=False)
    impuestos = db.Column(db.Numeric(10,2), default=0.00)
    metodoPago = db.Column(db.String(50), nullable=False)
    idUser = db.Column(db.Integer, db.ForeignKey('usuarios.idUser'))
    idVenta = db.Column(db.Integer, db.ForeignKey('ventas.idVenta'))
    
    # Relaciones
    usuario = db.relationship('User', backref='facturas')
    venta = db.relationship('Venta', backref='facturas')


# Tabla para almacenar el historial de ventas
class HistorialVenta(db.Model):
    __tablename__ = 'historialVenta'
    
    idHistorialVenta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fechaModificacion = db.Column(db.Date, server_default=db.func.current_date())
    accionRelaizada = db.Column(db.String(15))
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuarios.idUser'))
    idVenta = db.Column(db.Integer, db.ForeignKey('ventas.idVenta'))
    
    # Relaciones
    usuario = db.relationship('User', backref='historial_ventas')
    venta = db.relationship('Venta', backref='historial')