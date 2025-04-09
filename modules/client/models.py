# client/models.py
from database.conexion import db

# ~ Tabla para los pedidos
class Pedido(db.Model):
    __tablename__ = 'pedidos'
    
    idPedidos = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idCliente = db.Column(db.Integer, db.ForeignKey('usuarios.idUser'), nullable=False)
    fechaPedido = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    estadoPedido = db.Column(db.Enum('Pendiente', 'Enviado', 'Entregado', 'Cancelado'), default='Pendiente')
    costoPedido = db.Column(db.Numeric(10,2), nullable=False)
    
    detalles = db.relationship('DetallePedido', backref='pedido', cascade='all, delete-orphan')

# ~ Tabla para los detalles de los pedidos
class DetallePedido(db.Model):
    __tablename__ = 'detallePedido'
    
    idDetallePedido = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idPedido = db.Column(db.Integer, db.ForeignKey('pedidos.idPedidos'), nullable=False)
    idGalleta = db.Column(db.Integer, db.ForeignKey('galletas.idGalleta'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precioUnitario = db.Column(db.Numeric(10,2), nullable=False)
    subtotal = db.Column(db.Numeric(10,2), nullable=False)
    
    galleta = db.relationship('Galleta')