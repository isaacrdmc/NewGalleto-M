from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo
from flask_wtf import FlaskForm

class UsuarioForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[
        DataRequired(),
        Length(min=4, max=50),
        Regexp(r'^[a-zA-Z0-9_]+$', message="Solo letras, números y guiones bajos")
    ])
    
    password = PasswordField('Contraseña', validators=[
        DataRequired(),
        Length(min=8),
        Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
               message="Debe contener al menos una mayúscula, una minúscula, un número y un carácter especial")
    ])
    
    confirm_password = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(),
        EqualTo('password', message='Las contraseñas deben coincidir')
    ])
    
    rol = SelectField('Rol', choices=[], validators=[DataRequired()])  # Las choices se llenarán dinámicamente
    
    estado = SelectField('Estado', choices=[
        ('Activo', 'Activo'),
        ('Bloqueado', 'Bloqueado'),
        ('Inactivo', 'Inactivo')
    ], validators=[DataRequired()])