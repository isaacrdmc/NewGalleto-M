
# ? En esta sección vamos a colocar los formualrios del sistema para enviar los datos a la BD
from wtforms import StringField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, Length, Email, Regexp
from flask_wtf import FlaskForm
import re

# from wtforms import StringField, EmailField, TextAreaField, validators
# from wtforms import DataRequired, Email, Length


# ? Ahora vmos a crear una nueva clas epara poder crear el formulario de los proveedores
class ProveedoresForm(FlaskForm):
    empresa = StringField('Empresa', validators=[
                                DataRequired(), 
                                Length(max=80),
                                # ? Validamos que solo se ingresen letras y espacios
                                Regexp(r'^[a-zA-Z0-9\sñÑáéíóúÁÉÍÓÚüÜ.,-]+$')
                            ])
    telefono = StringField('Teléfono', validators=[
                                DataRequired(), 
                                Length(max=16),
                                # ? Validamos que solo se ingresen números y espacios
                                Regexp(r'^[\d\s()+.-]+$')
                            ])
    correo = EmailField('Correo', validators=[
                                DataRequired(), 
                                Length(max=60),
                                # ? Validamos que el correo sea válido
                                Email()
                            ])
    direccion = StringField('Dirección', validators=[
                                DataRequired(), 
                                Length(max=120)
                                # ,
                                # ? Validamos que solo se ingresen letras y espacios
                                # Regexp(r'^[a-zA-Z0-9\sñÑáéíóúÁÉÍÓÚüÜ#.,-]+$')
                            ])
    productos = StringField('Productos', validators=[
                                DataRequired(), 
                                Length(max=300)
                                ,
                                # ? Validamos que solo se ingresen letras, comas y espacios
                                Regexp(r'^[a-zA-Z0-9\sñÑáéíóúÁÉÍÓÚüÜ.;-]+$')
                            ])