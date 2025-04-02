
# ? En esta sección vamos a colocar los formualrios del sistema para enviar los datos a la BD

from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, TextAreaField
from wtforms.validators import DataRequired, Email, Length


# ? Ahora vmos a crear una nueva clas epara poder crear el formulario de los proveedores
class ProveedoresForm(FlaskForm):
    empresa = StringField('Empresa', validators=[DataRequired(), Length(max=30)])
    telefono = StringField('Teléfono', validators=[DataRequired(), Length(max=16)])
    correo = EmailField('Correo', validators=[DataRequired(), Length(max=60)])
    direccion = StringField('Dirección', validators=[DataRequired(), Length(max=120)])
    productos = StringField('Productos', validators=[DataRequired(), Length(max=300)])