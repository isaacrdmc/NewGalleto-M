from .models import VistaDetallesGalletas

def obtener_detalles_galletas():
    """
    Consulta la vista `vista_detalles_galletas` y devuelve los datos.
    """
    try:
        print("Consultando la vista 'vista_detalles_galletas'...")
        # Realiza la consulta a la vista
        detalles = VistaDetallesGalletas.query.all()
        print("Detalles de galletas obtenidos:")
        print(detalles)

        return detalles
    except Exception as e:
        # Manejo de errores en caso de que ocurra un problema con la consulta
        print(f"Error al consultar la vista 'vista_detalles_galletas': {e}")
        return []