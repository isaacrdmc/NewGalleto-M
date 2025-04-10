# ventas/models.py
from database.conexion import db
from sqlalchemy import Enum


# Tablas de la base de datos para ventas y detalles de ventas
class Venta(db.Model):
    __tablename__ = 'ventas'
    
    idVenta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fechaVentaGalleta = db.Column(db.Date, nullable=False)  # Cambiado de TIMESTAMP a Date
    totalVenta = db.Column(db.Numeric(10,2), nullable=False)  # Cambiado de total a totalVenta
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuarios.idUser'), nullable=False)
    idDetalleVenta = db.Column(db.Integer, db.ForeignKey('detallesVentas.idDetalleVenta'), nullable=False)  # Relación inversa
    
    # Relaciones (ajustadas)
    detalle = db.relationship('DetalleVenta', backref='venta', uselist=False)  # One-to-one
    usuario = db.relationship('User', foreign_keys=[idUsuario])

class DetalleVenta(db.Model):
    __tablename__ = 'detallesVentas'
    
    idDetalleVenta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cantGalletasVendidas = db.Column(db.Integer, nullable=False)
    precioUnitario = db.Column(db.Numeric(10,2), nullable=False)
    formaVenta = db.Column(Enum('Por pieza', 'Por precio', 'por paquete/caja', name='forma_venta_enum'), nullable=False)
    cantidadGalletas = db.Column(db.Integer)
    pesoGramos = db.Column(db.Numeric(10,2))
    idGalleta = db.Column(db.Integer, db.ForeignKey('galletas.idGalleta'))
    
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