# 
from datetime import datetime
from database.conexion import db

class LogSistema(db.Model):
    __tablename__ = 'logsSistema'

    # * Columnas de la tabla
    idLog = db.Column(db.Integer, primary_key=True)
    tipoLog = db.Column(db.Enum(
                    'NOTSET', 'DEBUG', 'INFO', 'WARNING', 
                    'ERROR', 'CRITICAL', 'SECURITY',
                    name='tipo_log_enum'), nullable=False)
    descripcionLog = db.Column(db.Text, nullable=False)
    fechaHora = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ipOrigen = db.Column(db.String(45))

    
    # ? Relacimos esta tabla con la de los usuarios como en el diagrama
    idUser = db.Column(db.Integer, db.ForeignKey('usuarios.idUser'))
    usuario = db.relationship('User', backref='logs')

    def __repr__(self):
        return f'<log {self.idLog} - {self.tipoLog}>'