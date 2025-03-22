# @Isaac Ramírez

from flask import Blueprint

# ? Vamos a crear lo blue prints para las rutas dentro de la sección de adminstración
bp_admistracion = Blueprint('admin', __name__)

# ? AHora importamos las demas rutas para esta sección del sistema




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