from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField
from wtforms.validators import DataRequired, NumberRange

class RecetaForm(FlaskForm):
    nombre = StringField('Nombre de la Receta', validators=[DataRequired()])
    instrucciones = TextAreaField('Instrucciones', validators=[DataRequired()])
    cantidad_producida = IntegerField('Cantidad producida', validators=[
        DataRequired(), 
        NumberRange(min=1, message="Debe producir al menos 1 galleta")
    ])
    galletTipo = IntegerField('Tipo de galleta', validators=[DataRequired()])
    id_galleta = SelectField('Galleta', coerce=int, validators=[DataRequired()])