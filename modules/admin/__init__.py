
from flask import Blueprint, render_template

# ? Vamos a crear lo blue prints para las rutas dentro de la sección de adminstración
bp_admistracion = Blueprint('admin', __name__)

# ? Ahora vamos a definir las rutas necesarias para el bluprint
@bp_admistracion.route('/adminstrador/DashBoad')
def dashboard():
    return 




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