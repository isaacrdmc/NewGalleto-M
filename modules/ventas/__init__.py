
from flask import Blueprint
# * Archivo con las rutas de la sección
from . import routes    # ~ podemos importar más de uno en este archivo '__init__'

# ? Vamos a crear lo blue prints para las rutas dentro de la sección de adminstración
bp_ventas = Blueprint('ventas', __name__)

