from datetime import datetime
from modules.shared.models import User
from database.conexion import db

class Galleta(db.Model):
    __tablename__ = 'galletas'
    id = db.Column('idGalleta', db.Integer, primary_key=True)
    nombre = db.Column('nombreGalleta', db.String(30), nullable=False)
    precio_unitario = db.Column(db.Numeric(10,2), nullable=False)
    cantidad_disponible = db.Column(db.Integer, nullable=False)
    gramaje = db.Column('gramajeGalleta', db.Numeric(10,2), nullable=False)
    tipo_galleta = db.Column(db.Integer, nullable=False)
    fecha_anaquel = db.Column('fechaAnaquel', db.Date, nullable=False)
    fecha_final_anaquel = db.Column('fechaFinalAnaquel', db.Date, nullable=False)
    
class Pedido(db.Model):
    __tablename__ = 'pedidos'
    
    idPedidos = db.Column(db.Integer, primary_key=True)
    estadoPedido = db.Column(db.String(20), nullable=False, default='Pendiente')
    costoPedido = db.Column(db.Float, nullable=False)
    fechaPedido = db.Column(db.Date, default=datetime.utcnow)
    idCliente = db.Column(db.Integer, db.ForeignKey('usuarios.idUser'), nullable=False)
    
    detalles = db.relationship('DetallePedido', backref='pedido', cascade='all, delete-orphan')

class DetallePedido(db.Model):
    __tablename__ = 'detallePedido'
    
    idDetallePedido = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Integer, nullable=False)
    precioUnitario = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    
    idPedido = db.Column(db.Integer, db.ForeignKey('pedidos.idPedidos'), nullable=False)
    idGalleta = db.Column(db.Integer, db.ForeignKey('galletas.idGalleta'), nullable=False)
    
    # Usa la relación sin definir la clase Galleta aquí
    galleta = db.relationship('Galleta', backref='detalles_pedido')

class VistaDetallesGalletas(db.Model):
    __tablename__ = 'vista_detalles_galletas'
    
    id = db.Column(db.Integer, primary_key=True)
    Galleta = db.Column(db.String(50))
    Forma_Venta = db.Column(db.String(50))
    Cantidad = db.Column(db.String(50))

# class Galleta(db.Model):
#     __tablename__ = 'galletas'
#     __table_args__ = {'extend_existing': True}  # Esto permite redefinir si es necesario
    
#     idGalleta = db.Column(db.Integer, primary_key=True)
#     nombreGalleta = db.Column(db.String(30), nullable=False)
#     precioUnitario = db.Column(db.Float, nullable=False)
#     cantidadDisponible = db.Column(db.Integer, nullable=False)
#     gramajeGalleta = db.Column(db.Float, nullable=False)
#     tipoGalleta = db.Column(db.Integer, nullable=False)
#     fechaAnaquel = db.Column(db.Date, nullable=False)
#     fechaFinalAnaquel = db.Column(db.Date, nullable=False)