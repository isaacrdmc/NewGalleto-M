# 
from datetime import datetime
from database.conexion import db

class LogSistema(db.Model):
    __tablename__ = 'logsSistema'

    # * Columnas de la tabla
    idLog = db.Column(db.Integr, primary_key=True)
    tipoLog = db.Column(db.Enum(
                    'INFO', 'WARNING', 'ERROR', 
                    'CRITICAL', 'DEBUG', 'SECURITY',
                    name='tipo_log_enum'), nullable=False)
    descripcionLog = db.Column(db.Text, nullable=False)
    fechaHora = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ipOrigen = db.Column(db.String(45))

    
    # ? Relacimos esta tabla con la de los usuarios como en el diagrama
    idUser = db.Column(db.Integer, db.ForeignKey('usuarios.idUser'))
    usuario = db.relationship('User', backref='logs')

    def __repr__(self):
        return f'<log {self.idLog} - {self.tipoLog}>'
    




"""
CREATE TABLE logsSistema (
    idLog INT AUTO_INCREMENT PRIMARY KEY,
    tipoLog ENUM('INFO', 'WARNING', 'ERROR', 'CRITICAL', 'DEBUG', 'SECURITY') NOT NULL,
    descripcionLog TEXT NOT NULL,
    fechaHora DATETIME NOT NULL DEFAULT current_timestamp,
    ipOrigen VARCHAR(45),
    
    idUser INT,
    FOREIGN KEY (idUser) REFERENCES usuarios(idUser)
);

"""