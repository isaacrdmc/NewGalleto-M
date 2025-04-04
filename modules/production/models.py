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
    id = db.Column('idReceta', db.Integer, primary_key=True)
    nombre = db.Column('nombreReceta', db.String(20), nullable=False)
    instrucciones = db.Column('instruccionReceta', db.String(520), nullable=False)
    cantidad_producida = db.Column('cantGalletasProduction', db.Integer, nullable=False)
    tipo_galleta = db.Column(db.Integer, nullable=False)
    id_galleta = db.Column(db.Integer, db.ForeignKey('galletas.idGalleta'))
    galleta = db.relationship('Galleta', backref='recetas')
