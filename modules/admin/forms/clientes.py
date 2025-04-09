# forms/clientes.py
from wtforms import StringField, PasswordField, SelectField, validators
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length

class ClienteForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[
        DataRequired(),
        Length(min=4, max=50),
        validators.Regexp(r'^[a-zA-Z0-9_]+$', message="Solo letras, números y guiones bajos")
    ])
    
    password = PasswordField('Contraseña', validators=[
        DataRequired(),
        Length(min=8),
        validators.Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$',
               message="Debe contener al menos una mayúscula, una minúscula y un número")
    ])
    
    estado = SelectField('Estado', choices=[
        ('Activo', 'Activo'),
        ('Bloqueado', 'Bloqueado')
    ], validators=[DataRequired()])