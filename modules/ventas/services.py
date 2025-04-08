from modules.ventas.models import Venta
from database.conexion import db

def obtener_historial_ventas():
    ventas = Venta.query.join(Venta.usuario).all()

    resultado = []
    for venta in ventas:
        cantidad = sum(det.cantGalletasVendidas for det in venta.detalles) if venta.detalles else 0

        resultado.append({
            "id": venta.idVenta,
            "responsable": f"{venta.usuario.nombre} {venta.usuario.apellP}",
            "fecha": venta.fechaVentaGalleta.strftime('%d/%m/%y'),
            "detalles": cantidad,
            "total": float(venta.totalVenta)
        })

    return resultado