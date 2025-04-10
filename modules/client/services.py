from modules.production.models import Galleta  # Cambia esta línea
from .models import VistaDetallesGalletas
from flask import current_app
from database.conexion import db

def obtener_detalles_galletas():
    """
    Obtiene los detalles de galletas desde la vista SQL
    Returns:
        list: Lista de objetos VistaDetallesGalletas o lista vacía si hay error
    """
    try:
        detalles = VistaDetallesGalletas.query.order_by(VistaDetallesGalletas.Galleta).all()
        
        # Debug: Verificar los primeros 3 registros
        if detalles and current_app.config.get('DEBUG', False):
            current_app.logger.debug(f"Primeros 3 registros: {[(d.Galleta, d.Forma_Venta, d.Cantidad) for d in detalles[:3]]}")
        
        return detalles
        
    except Exception as e:
        current_app.logger.error(f"Error al consultar vista_detalles_galletas: {str(e)}")
        return []