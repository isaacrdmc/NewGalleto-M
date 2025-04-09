from sqlalchemy import Column, Integer, String, Date, DECIMAL, ForeignKey, Enum, Text, DateTime
from sqlalchemy.orm import relationship
from database.conexion import db

class Usuario(db.Model):
    __tablename__ = 'usuario'

    idUser = Column(Integer, primary_key=True)
    nombre = Column(String(10))
    apellP = Column(String(40))
    apellM = Column(String(40))
    contrasena = Column(String(255))
    idRol = Column(Integer, ForeignKey('roles.idRolUsuario'))

    ventas = relationship('Venta', back_populates='usuario')
    historial = relationship('HistorialVenta', back_populates='usuario')
    notificaciones = relationship('Notificacion', back_populates='usuario')
    logs = relationship('LogSistema', back_populates='usuario')


class Rol(db.Model):
    __tablename__ = 'roles'
    idRolUsuario = Column(Integer, primary_key=True)
    nombreRol = Column(String(20))


class Galleta(db.Model):
    __tablename__ = 'galletas'

    idGalleta = Column(Integer, primary_key=True)
    nombreGalleta = Column(String(30))
    precioUnitario = Column(DECIMAL(10,2))
    cantidadDisponible = Column(Integer)
    gramajeGalleta = Column(DECIMAL(10,2))
    tipoGalleta = Column(Integer)
    fechaAnaquel = Column(Date)
    fechaFinalAnaquel = Column(Date)


class DetalleVenta(db.Model):
    __tablename__ = 'detallesVentas'

    idDetalleVenta = Column(Integer, primary_key=True)
    cantGalletasVendidas = Column(Integer)
    precioUnitario = Column(DECIMAL(10,2))
    formaVenta = Column(Enum('Por pieza', 'Por peso', 'por paquete/caja'))
    cantidadGalletas = Column(Integer)
    pesoGramos = Column(DECIMAL(10,2))
    idGalleta = Column(Integer, ForeignKey('galletas.idGalleta'))
    idVenta = Column(Integer, ForeignKey('ventas.idVenta'))  # <- esta es clave

    galleta = relationship('Galleta')
    venta = relationship('Venta', back_populates='detalles')

class Venta(db.Model):
    __tablename__ = 'ventas'

    idVenta = Column(Integer, primary_key=True)
    fechaVentaGalleta = Column(Date)
    totalVenta = Column(DECIMAL(10,2))
    idUsuario = Column(Integer, ForeignKey('usuario.idUser'))

    usuario = relationship('Usuario', back_populates='ventas')
    detalles = relationship('DetalleVenta', back_populates='venta')  # ← relación 1:N real



class HistorialVenta(db.Model):
    __tablename__ = 'historialVenta'

    idHistorialVenta = Column(Integer, primary_key=True)
    fechaModificacion = Column(Date)
    accionRelaizada = Column(String(15))
    idUsuario = Column(Integer, ForeignKey('usuario.idUser'))
    idVenta = Column(Integer, ForeignKey('ventas.idVenta'))

    usuario = relationship('Usuario', back_populates='historial')


class Notificacion(db.Model):
    __tablename__ = 'notificaciones'

    idNotificaciónes = Column(Integer, primary_key=True)
    tipoNotificacion = Column(Enum(
        'Caducidad Insumo', 
        'Caducidad Galleta', 
        'Bajo Inventario', 
        'Solicitud Produccion', 
        'No hay suficientes inusmos de'))
    mensajeNotificar = Column(String(255))
    fechaCreacion = Column(DateTime)
    fechaVisto = Column(DateTime)
    estatus = Column(Enum('Nueva', 'Vista', 'Resuelto'), default='Nueva')
    idUsuario = Column(Integer, ForeignKey('usuario.idUser'))
    idInsumo = Column(Integer, ForeignKey('insumos.idInsumo'))
    idGalleta = Column(Integer, ForeignKey('galletas.idGalleta'))

    usuario = relationship('Usuario', back_populates='notificaciones')


class LogSistema(db.Model):
    __tablename__ = 'logsSistema'

    idLog = Column(Integer, primary_key=True)
    tipoLog = Column(Enum('Error', 'Seguridad', 'Acceso', 'Operacion'))
    descripcionLog = Column(Text)
    fechaHora = Column(DateTime)
    ipOrigen = Column(String(45))
    idUsuario = Column(Integer, ForeignKey('usuario.idUser'))

    usuario = relationship('Usuario', back_populates='logs')
    
class Pedido(db.Model):
    __tablename__ = 'pedidos'

    idPedidos = Column(Integer, primary_key=True)
    fechaPedido = Column(Date)
    estadoPedido = Column(Enum('Pendiente', 'Enviado', 'Entregado', 'Cancelado'), default='Pendiente')
    costoPedido = Column(DECIMAL(10,2))
    idCliente = Column(Integer, ForeignKey('usuario.idUser'))

    cliente = relationship('Usuario')
    detalles = relationship('DetallePedido', back_populates='pedido')


class DetallePedido(db.Model):
    __tablename__ = 'detallePedido'

    idDetallePedido = Column(Integer, primary_key=True)
    cantidad = Column(Integer)
    precioUnitario = Column(DECIMAL(10,2))
    subtotal = Column(DECIMAL(10,2))

    idPedido = Column(Integer, ForeignKey('pedidos.idPedidos'))
    idGalleta = Column(Integer, ForeignKey('galletas.idGalleta'))

    pedido = relationship('Pedido', back_populates='detalles')
    galleta = relationship('Galleta')

