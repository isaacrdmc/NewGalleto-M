
from flask import Blueprint
# * Archivo con las rutas de la sección
from . import routes    # ~ podemos importar más de uno en este archivo '__init__'

# ? Vamos a crear lo blue prints para las rutas dentro de la sección de adminstración
bp_admistracion = Blueprint('admin', __name__)




"""
modules/
└── ventas/
    ├── __init__.py        # Define el Blueprint
    ├── routes.py          # Define las rutas HTTP
    ├── models.py          # Define los modelos de datos
    
    ├── forms.py           # Define formularios WTForms
    ├── utils.py           # Funciones de utilidad específicas para ventas
    ├── validators.py      # Validaciones personalizadas
    └── services/          # Servicios más complejos
        ├── __init__.py
        ├── facturas.py
        ├── cotizaciones.py
        └── reportes.py
"""