
from flask import Blueprint
from . import routes

# ? Vamos a crear lo blue prints para las rutas dentro de la sección de adminstración
bp_clientes = Blueprint('cliente', __name__)

