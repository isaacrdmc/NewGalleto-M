
from flask import Blueprint
from . import routes

# ? Vamos a crear lo blue prints para las rutas dentro de la sección de adminstración
bp_shared = Blueprint('shared', __name__)
