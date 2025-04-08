# __init__.py de shared
from flask import Blueprint

bp_shared = Blueprint('shared', __name__)

# Importar rutas después de definir el blueprint para evitar circular imports
from . import routes