from modules.ventas.models import Venta
from database.conexion import db
from modules.ventas.models import Pedido

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

def obtener_pedidos_clientes():
    pedidos = Pedido.query.join(Pedido.cliente).all()
    resultado = []

    for pedido in pedidos:
        resultado.append({
            "id": pedido.idPedidos,
            "cliente": f"{pedido.cliente.nombre} {pedido.cliente.apellP}",
            "fecha_pedido": pedido.fechaPedido.strftime('%d/%m/%y'),
            "estado": pedido.estadoPedido,
            "total": float(pedido.costoPedido)
        })

    return resultado
