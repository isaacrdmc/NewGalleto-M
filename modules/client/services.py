from modules.production.models import Galleta  # Cambia esta línea
from .models import VistaDetallesGalletas
from flask import current_app
from flask_login import current_user
from database.conexion import db
from sqlalchemy.exc import SQLAlchemyError
from .models import Pedido, DetallePedido

 
def obtener_detalles_galletas():
    """Obtiene los detalles de galletas desde la vista SQL"""
    try:
        return VistaDetallesGalletas.query.all()
    except SQLAlchemyError as e:
        current_app.logger.error(f"Error en vista detalles galletas: {str(e)}")
        return []