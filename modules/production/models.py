from database.conexion import db
from datetime import datetime
from sqlalchemy.sql import func


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
    id_usuario = db.Column('idUsuario', db.Integer, db.ForeignKey('usuario.idUser'), nullable=False)
    
    # Relaciones
    receta = db.relationship('Receta', backref='horneados')
    usuario = db.relationship('Usuario', backref='horneados')
    
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
            'nombre_usuario': f"{self.usuario.nombre} {self.usuario.apellP}" if self.usuario else None
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

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column('idUser', db.Integer, primary_key=True)
    nombre = db.Column(db.String(10), nullable=False)
    apellP = db.Column(db.String(40), nullable=False)
    apellM = db.Column(db.String(40), nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    
    id_rol = db.Column('idRol', db.Integer, db.ForeignKey('roles.idRolUsuario'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'apellP': self.apellP,
            'apellM': self.apellM,
            'id_rol': self.id_rol
        }
        
