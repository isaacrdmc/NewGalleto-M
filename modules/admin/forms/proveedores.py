from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, TextAreaField
from wtforms.validators import DataRequired, Email, Length

class ProveedorForm(FlaskForm):
    empresa = StringField('Empresa', validators=[DataRequired(), Length(max=30)])
    telefono = StringField('Teléfono', validators=[DataRequired(), Length(max=16)])
    correo = EmailField('Correo', validators=[DataRequired(), Email(), Length(max=60)])
    direccion = StringField('Dirección', validators=[DataRequired(), Length(max=120)])
    productos = StringField('Productos', validators=[DataRequired(), Length(max=300)])
    tipo_proveedor = StringField('Tipo de Proveedor', validators=[DataRequired(), Length(max=40)])