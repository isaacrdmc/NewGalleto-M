from database.conexion import db
from datetime import datetime
from sqlalchemy.sql import func
from modules.shared.models import Rol as Role
from modules.shared.models import User as Usuario
from modules.admin.models import Proveedores as Proveedor

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

class Insumo(db.Model):
    __tablename__ = 'insumos'
    id = db.Column('idInsumo', db.Integer, primary_key=True)
    nombre = db.Column(db.String(40), nullable=False)
    unidad = db.Column('unidadInsumo', db.Enum('Gr', 'mL', 'Pz'), nullable=False)
    cantidad_disponible = db.Column('cantidadDisponible', db.Integer, nullable=False)
    cantidad_minima = db.Column('cantidadMinima', db.Integer, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'unidad': self.unidad,
            'cantidad_disponible': self.cantidad_disponible,
            'cantidad_minima': self.cantidad_minima
        }

class Receta(db.Model):
    __tablename__ = 'recetas'
    
    # Define las columnas y sus tipos
    id = db.Column('idReceta', db.Integer, primary_key=True)
    nombre = db.Column('nombreReceta', db.String(20), nullable=False)
    instrucciones = db.Column('instruccionReceta', db.String(520), nullable=False)
    cantidad_producida = db.Column('cantGalletasProduction', db.Integer, nullable=False)
    galletTipo = db.Column('galletTipo', db.Integer, nullable=False)  # Modificado aquí
    id_galleta = db.Column('idGalleta', db.Integer, db.ForeignKey('galletas.idGalleta'))  # Cambié 'id_galleta' a 'idGalleta'
    
    # Relación con la tabla 'galletas'
    galleta = db.relationship('Galleta', backref='recetas')
    @property
    def cantGalletasProduction(self):
        """Propiedad para mantener compatibilidad con código existente"""
        return self.cantidad_producida



# Añadir al archivo models.py existente

class Horneado(db.Model):
    __tablename__ = 'historialHorneado'
    id = db.Column('idHorneado', db.Integer, primary_key=True)
    fecha_horneado = db.Column('fechaHorneado', db.DateTime, nullable=False)
    temperatura_horno = db.Column('temperaturaHorno', db.Integer, nullable=False)
    tiempo_horneado = db.Column('tiempoHorneado', db.Integer, nullable=False)
    cantidad_producida = db.Column('cantidadProducida', db.Integer, nullable=False)
    observaciones = db.Column('observaciones', db.String(255), nullable=True)
    
    # Relaciones con otras tablas
    id_receta = db.Column('idReceta', db.Integer, db.ForeignKey('recetas.idReceta'), nullable=False)
    id_produccion = db.Column('idProduccion', db.Integer, db.ForeignKey('Produccion.inProduccion'), nullable=True)
    id_usuario = db.Column('idUsuario', db.Integer, db.ForeignKey('usuarios.idUser'), nullable=False)
    
    # Relaciones
    receta = db.relationship('Receta', backref='horneados')
    usuario = db.relationship('User', backref='horneados')
    
    def to_dict(self):
        return {
            'id': self.id,
            'fecha_horneado': self.fecha_horneado.strftime('%Y-%m-%d %H:%M:%S'),
            'temperatura_horno': self.temperatura_horno,
            'tiempo_horneado': self.tiempo_horneado,
            'cantidad_producida': self.cantidad_producida,
            'observaciones': self.observaciones,
            'id_receta': self.id_receta,
            'id_produccion': self.id_produccion,
            'id_usuario': self.id_usuario,
            'nombre_receta': self.receta.nombre if self.receta else None,
            'nombre_usuario': self.usuario.username if self.usuario else None
        }

class Produccion(db.Model):
    __tablename__ = 'Produccion'
    id = db.Column('inProduccion', db.Integer, primary_key=True)
    fecha_produccion = db.Column('fechaProduccion', db.Date, nullable=False)
    gramos_merma = db.Column('gramosMerma', db.Integer, nullable=False)
    mililitros_merma = db.Column('mililitrosMerma', db.Integer, nullable=False)
    piezas_merma = db.Column('piezasMerma', db.Integer, nullable=False)
    produccion_total = db.Column('produccionTotal', db.Integer, nullable=False)
    
    # Relaciones con otras tablas
    id_receta = db.Column('idReceta', db.Integer, db.ForeignKey('recetas.idReceta'), nullable=True)
    id_galleta = db.Column('idGalleta', db.Integer, db.ForeignKey('galletas.idGalleta'), nullable=True)
    
    # Relaciones
    horneados = db.relationship('Horneado', backref='produccion')
    
    def to_dict(self):
        return {
            'id': self.id,
            'fecha_produccion': self.fecha_produccion.strftime('%Y-%m-%d'),
            'gramos_merma': self.gramos_merma,
            'mililitros_merma': self.mililitros_merma,
            'piezas_merma': self.piezas_merma,
            'produccion_total': self.produccion_total,
            'id_receta': self.id_receta,
            'id_galleta': self.id_galleta
        }
        
        
###################################################

class TransaccionCompra(db.Model):
    __tablename__ = 'transaccionCompra'
    
    id = db.Column('idTransaccionCompra', db.Integer, primary_key=True)
    fecha_compra = db.Column('fechaCompra', db.Date, nullable=False)
    total_compra = db.Column('totalCompra', db.Numeric(10, 2))

    # Clave foránea correctamente definida con 'idProveedor' (correspondiente a la columna en la tabla proveedores)
    id_proveedor = db.Column('idProveedor', db.Integer, db.ForeignKey('proveedores.idProveedores'), nullable=False)
    proveedor = db.relationship('Proveedores', backref='transacciones')
    
    detalles = db.relationship('DetalleCompraInsumo', backref='transaccion', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'fecha_compra': self.fecha_compra.strftime('%Y-%m-%d'),
            'total_compra': float(self.total_compra) if self.total_compra else 0,
            'proveedor': self.proveedor.nombre if self.proveedor else None,
            'detalles': [detalle.to_dict() for detalle in self.detalles]
        }



class DetalleCompraInsumo(db.Model):
    __tablename__ = 'detalleCompraInsumo'
    id = db.Column('idetalleCompraInsumo', db.Integer, primary_key=True)
    cant_cajas = db.Column('cantCajas', db.Integer, nullable=False)
    cant_unidades_caja = db.Column('cantUnidadesXcaja', db.Integer, nullable=False)
    cant_merma_unidad = db.Column('cantMermaPorUnidad', db.Integer, nullable=False)
    costo_caja = db.Column('CostoPorCaja', db.Numeric(10, 2), nullable=False)
    costo_unidad_caja = db.Column('costoUnidadXcaja', db.Numeric(10, 2), nullable=False)
    unidad_insumo = db.Column('unidadInsumo', db.Enum('Gr', 'mL', 'Pz'), nullable=False)
    fecha_registro = db.Column('fechaRegistro', db.Date, nullable=False)
    fecha_caducidad = db.Column('fechaCaducidad', db.Date, nullable=False)
    
    # Relaciones
    id_compra = db.Column('idCompra', db.Integer, db.ForeignKey('transaccionCompra.idTransaccionCompra'), nullable=False)
    id_insumo = db.Column('idInsumo', db.Integer, db.ForeignKey('insumos.idInsumo'), nullable=False)
    insumo = db.relationship('Insumo', backref='compras')
    
    def to_dict(self):
        return {
            'id': self.id,
            'cant_cajas': self.cant_cajas,
            'cant_unidades_caja': self.cant_unidades_caja,
            'cant_merma_unidad': self.cant_merma_unidad,
            'costo_caja': float(self.costo_caja),
            'costo_unidad_caja': float(self.costo_unidad_caja),
            'unidad_insumo': self.unidad_insumo,
            'fecha_registro': self.fecha_registro.strftime('%Y-%m-%d'),
            'fecha_caducidad': self.fecha_caducidad.strftime('%Y-%m-%d'),
            'nombre_insumo': self.insumo.nombre if self.insumo else None
        }

class Notificacion(db.Model):
    __tablename__ = 'notificaciones'
    id = db.Column('idNotificaciónes', db.Integer, primary_key=True)
    tipo_notificacion = db.Column('tipoNotificacion', db.Enum(
        'Caducidad Insumo', 
        'Caducidad Galleta', 
        'Bajo Inventario', 
        'Solicitud Produccion', 
        'No hay suficientes inusmos de'), nullable=False)
    mensaje = db.Column('mensajeNotificar', db.String(255))
    fecha_creacion = db.Column('fechaCreacion', db.DateTime, nullable=False, default=datetime.now)
    fecha_visto = db.Column('fechaVisto', db.DateTime)
    estatus = db.Column(db.Enum('Nueva', 'Vista', 'Resuelto'), nullable=False, default='Nueva')
    
    # Relaciones
    id_usuario = db.Column('idUsuario', db.Integer, db.ForeignKey('usuarios.idUser'))
    id_insumo = db.Column('idInsumo', db.Integer, db.ForeignKey('insumos.idInsumo'))
    id_galleta = db.Column('idGalleta', db.Integer, db.ForeignKey('galletas.idGalleta'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'tipo_notificacion': self.tipo_notificacion,
            'mensaje': self.mensaje,
            'fecha_creacion': self.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'),
            'fecha_visto': self.fecha_visto.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_visto else None,
            'estatus': self.estatus
        }

class Merma(db.Model):
    __tablename__ = 'merma'
    id = db.Column('idMerma', db.Integer, primary_key=True)
    tipo_merma = db.Column('tipoMerma', db.String(15), nullable=False)
    unidad_merma = db.Column('unidadMerma', db.Enum('Gr', 'mL', 'Pz'), nullable=False)
    cantidad_merma = db.Column('cantidadMerma', db.Integer, nullable=False)
    fecha_merma = db.Column('fechaMerma', db.Date, nullable=False)
    
    # Relaciones
    id_produccion = db.Column('inProduccion', db.Integer, db.ForeignKey('Produccion.inProduccion'))
    id_insumo = db.Column('idInsumo', db.Integer, db.ForeignKey('insumos.idInsumo'))
    id_galleta = db.Column('idGalleta', db.Integer, db.ForeignKey('galletas.idGalleta'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'tipo_merma': self.tipo_merma,
            'unidad_merma': self.unidad_merma,
            'cantidad_merma': self.cantidad_merma,
            'fecha_merma': self.fecha_merma.strftime('%Y-%m-%d')
        }
        
#################################
# Añadir al final de models.py

class SolicitudHorneado(db.Model):
    __tablename__ = 'solicitudes_horneado'
    
    id = db.Column('idSolicitud', db.Integer, primary_key=True)
    fecha_solicitud = db.Column('fechaSolicitud', db.DateTime, nullable=False, default=datetime.now)
    cantidad_lotes = db.Column('cantidadLotes', db.Integer, nullable=False)
    estado = db.Column(db.Enum('Pendiente', 'Aprobada', 'Rechazada', 'Completada'), nullable=False, default='Pendiente')
    motivo_rechazo = db.Column('motivoRechazo', db.String(255), nullable=True)
    fecha_aprobacion = db.Column('fechaAprobacion', db.DateTime, nullable=True)
    fecha_completado = db.Column('fechaCompletado', db.DateTime, nullable=True)
    
    # Relaciones
    id_receta = db.Column('idReceta', db.Integer, db.ForeignKey('recetas.idReceta'), nullable=False)
    id_solicitante = db.Column('idSolicitante', db.Integer, db.ForeignKey('usuarios.idUser'), nullable=False)
    id_aprobador = db.Column('idAprobador', db.Integer, db.ForeignKey('usuarios.idUser'), nullable=True)
    id_horneado = db.Column('idHorneado', db.Integer, db.ForeignKey('historialHorneado.idHorneado'), nullable=True)
    
    # Relaciones ORM
    receta = db.relationship('Receta', backref='solicitudes')
    solicitante = db.relationship('User', foreign_keys=[id_solicitante], backref='solicitudes_enviadas')
    aprobador = db.relationship('User', foreign_keys=[id_aprobador], backref='solicitudes_aprobadas')
    horneado = db.relationship('Horneado', backref='solicitud')
    
    def to_dict(self):
        return {
            'id': self.id,
            'fecha_solicitud': self.fecha_solicitud.strftime('%Y-%m-%d %H:%M:%S'),
            'cantidad_lotes': self.cantidad_lotes,
            'estado': self.estado,
            'motivo_rechazo': self.motivo_rechazo,
            'fecha_aprobacion': self.fecha_aprobacion.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_aprobacion else None,
            'fecha_completado': self.fecha_completado.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_completado else None,
            'id_receta': self.id_receta,
            'nombre_receta': self.receta.nombre if self.receta else None,
            'id_solicitante': self.id_solicitante,
            'nombre_solicitante': self.solicitante.username if self.solicitante else None,
            'id_aprobador': self.id_aprobador,
            'nombre_aprobador': self.aprobador.username if self.aprobador else None,
            'id_horneado': self.id_horneado
        }