
from flask import Blueprint

# ? Vamos a crear lo blue prints para las rutas dentro de la sección de adminstración
bp_shared = Blueprint('shared', __name__)


# * Archivo con las rutas de la sección
from . import routes    # ~ podemos importar más de uno en este archivo '__init__'