from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    
    idPedidos = db.Column(db.Integer, primary_key=True)
    estadoPedido = db.Column(db.Enum('Pendiente', 'Enviado', 'Entregado', 'Cancelado'))
    costoPedido = db.Column(db.Numeric(10,2))
    fechaPedido = db.Column(db.Date, default=datetime.now())
    
    # Relaciones
    detalles = db.relationship('DetallePedido', backref='pedido')
    cliente = db.relationship('Usuario', backref='pedidos')

class DetallePedido(db.Model):
    __tablename__ = 'detallePedido'
    
    idDetallePedido = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Integer)
    precioUnitario = db.Column(db.Numeric(10,2))
    
    # Claves foráneas
    idPedido = db.Column(db.Integer, db.ForeignKey('pedidos.idPedidos'))
    idGalleta = db.Column(db.Integer, db.ForeignKey('galletas.idGalleta'))
    
    # Relación
    galleta = db.relationship('Galleta')

class VistaDetallesGalletas(db.Model):
    __tablename__ = 'vista_detalles_galletas'
    galleta = db.Column(db.String(50), primary_key=True)  # Columna 'Galleta'
    forma_venta = db.Column(db.String(50))               # Columna 'Forma de Venta'
    cantidad = db.Column(db.String(50))                 # Columna 'Cantidad'