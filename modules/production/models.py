# production/models.py
from database.conexion import db
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy import Enum

# Tabla de galletas
class Galleta(db.Model):
    __tablename__ = 'galletas'
    id = db.Column('idGalleta', db.Integer, primary_key=True)
    nombre = db.Column('nombreGalleta', db.String(30), nullable=False)
    precio_unitario = db.Column('precioUnitario', db.Numeric(10,2), nullable=False)
    cantidad_disponible = db.Column('cantidadDisponible', db.Integer, nullable=False)
    gramaje = db.Column('gramajeGalleta', db.Numeric(10,2), nullable=False)
    tipo_galleta = db.Column('tipoGalleta', db.Integer, nullable=False)
    fecha_anaquel = db.Column('fechaAnaquel', db.Date, nullable=False)
    fecha_final_anaquel = db.Column('fechaFinalAnaquel', db.Date, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'precio': float(self.precio_unitario),
            'gramaje': float(self.gramaje),
            'cantidad': self.cantidad_disponible,
            'tipo': self.tipo_galleta,
            'fecha_caducidad': self.fecha_final_anaquel.strftime('%Y-%m-%d'),
        }


# Tabla de insumos
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

# Tabla de recetas
class Receta(db.Model):
    __tablename__ = 'recetas'
    
    # Define las columnas y sus tipos
    id = db.Column('idReceta', db.Integer, primary_key=True)
    nombre = db.Column('nombreReceta', db.String(50), nullable=False)
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

    @property
    def imagen_url(self):
        """Propiedad calculada para obtener la URL de la imagen"""
        from flask import current_app
        import os
        
        # Buscar imagen específica de la receta
        upload_folder = os.path.join(current_app.root_path, 'static', 'img', 'recetas')
        if os.path.exists(upload_folder):
            for ext in ['jpg', 'jpeg', 'png', 'gif']:
                filename = f"{self.id}_{self.nombre.lower().replace(' ', '_')}.{ext}"
                filepath = os.path.join(upload_folder, filename)
                if os.path.exists(filepath):
                    return f"/static/img/recetas/{filename}"
        
        # Si no tiene imagen específica, usar la de la galleta asociada
        if self.galleta:
            galleta_img = f"/static/img/{self.galleta.nombre.lower().replace(' ', '_')}.png"
            galleta_path = os.path.join(current_app.root_path, 'static', 'img', f"{self.galleta.nombre.lower().replace(' ', '_')}.png")
            if os.path.exists(galleta_path):
                return galleta_img
        
        # Si no hay nada, usar imagen por defecto
        return '/static/img/receta.jpg'

    def to_dict(self, include_galleta=True):
        data = {
            'id': self.id,
            'nombre': self.nombre,
            'instrucciones': self.instrucciones,
            'cantidad_producida': self.cantidad_producida,
            'galletTipo': self.galletTipo,
            'id_galleta': self.id_galleta,
            'imagen_url': self.imagen_url  # Usamos la propiedad
        }
    
        if include_galleta and self.galleta:
            data['galleta'] = self.galleta.to_dict()
    
        return data

# Tabla del historial del horneado
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

# Tabla de produccion
class Produccion(db.Model):
    __tablename__ = 'Produccion'
    
    inProduccion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fechaProduccion = db.Column(db.Date, nullable=False)
    gramosMerma = db.Column(db.Integer, nullable=False)
    mililitrosMerma = db.Column(db.Integer, nullable=False)
    piezasMerma = db.Column(db.Integer, nullable=False)
    produccionTotal = db.Column(db.Integer, nullable=False)
    idReceta = db.Column(db.Integer, db.ForeignKey('recetas.idReceta'))
    idGalleta = db.Column(db.Integer, db.ForeignKey('galletas.idGalleta'))
    
    receta = db.relationship('Receta', backref='producciones')
    galleta = db.relationship('Galleta', backref='producciones')
    
    def to_dict(self):
        return {
            'id': self.inProduccion,
            'fecha_produccion': self.fechaProduccion.strftime('%Y-%m-%d'),
            'gramos_merma': self.gramosMerma,
            'mililitros_merma': self.mililitrosMerma,
            'piezas_merma': self.piezasMerma,
            'produccion_total': self.produccionTotal,
            'id_receta': self.idReceta,
            'id_galleta': self.idGalleta
        }

# Tabla de ingredientes de la receta
class IngredienteReceta(db.Model):
    __tablename__ = 'ingredientesReceta'
    
    idIngredientesResetas = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cantidad = db.Column(db.Integer, nullable=False)
    idInsumo = db.Column(db.Integer, db.ForeignKey('insumos.idInsumo'), nullable=False)
    idReceta = db.Column(db.Integer, db.ForeignKey('recetas.idReceta'), nullable=False)
    
    insumo = db.relationship('Insumo')
    
    def to_dict(self):
        return {
            'id': self.idIngredientesResetas,
            'id_receta': self.idReceta,
            'id_insumo': self.idInsumo,
            'cantidad': self.cantidad,
            'insumo': self.insumo.to_dict() if self.insumo else None
        }
        

# Tabla de solicitudes de horneado
class SolicitudHorneado(db.Model):
    __tablename__ = 'solicitudes_horneado'
    
    idSolicitud = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idReceta = db.Column(db.Integer, db.ForeignKey('recetas.idReceta'), nullable=False)
    cantidadLotes = db.Column(db.Integer, nullable=False)
    idSolicitante = db.Column(db.Integer, db.ForeignKey('usuarios.idUser'), nullable=False)
    idAprobador = db.Column(db.Integer, db.ForeignKey('usuarios.idUser'))
    estado = db.Column(Enum('Pendiente', 'Aprobada', 'Rechazada', 'Completada', name='estado_solicitud_enum'), default='Pendiente')
    motivoRechazo = db.Column(db.String(255))
    fechaSolicitud = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    fechaAprobacion = db.Column(db.DateTime)
    fechaCompletado = db.Column(db.DateTime)
    idHorneado = db.Column(db.Integer, db.ForeignKey('historialHorneado.idHorneado'))
    
    # Relaciones
    receta = db.relationship('Receta', backref='solicitudes')
    solicitante = db.relationship('User', foreign_keys=[idSolicitante], backref='solicitudes_enviadas')
    aprobador = db.relationship('User', foreign_keys=[idAprobador], backref='solicitudes_aprobadas')
    horneado = db.relationship('Horneado', backref='solicitud')


    