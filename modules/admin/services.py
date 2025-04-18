# services.py
from .models import Proveedores, TransaccionCompra, DetalleCompraInsumo, Notificacion
from ..shared.models import User, Rol 
from ..client.models import Pedido, DetallePedido
from ..ventas.models import HistorialVenta, Venta, DetalleVenta
from ..production.models import Merma, Receta, Galleta, Insumo, Horneado, Produccion, IngredienteReceta
from database.conexion import db
from werkzeug.security import generate_password_hash
from sqlalchemy import case, distinct, func
from datetime import datetime, timedelta

# ==============================================
# SECCIÓN DE PROVEEDORES
# ==============================================

def agregar_proveedor(nombre, telefono, correo, direccion, productosProveedor):
    """
    Agrega un nuevo proveedor a la base de datos
    """
    nuevo_proveedor = Proveedores(
        nombre=nombre,
        telefono=telefono,
        correo=correo,
        direccion=direccion,
        productosProveedor=productosProveedor
    )
    db.session.add(nuevo_proveedor)
    db.session.commit()
    return nuevo_proveedor

def obtener_proveedores():
    """
    Obtiene todos los proveedores ordenados por ID descendente
    """
    return Proveedores.query.order_by(Proveedores.idProveedores.desc()).all()

def actualizar_proveedor(proveedor_id, empresa=None, nombre=None, telefono=None, correo=None, direccion=None, productosProveedor=None, productos=None):
    """
    Actualiza los datos de un proveedor existente
    """
    try: 
        proveedor = Proveedores.query.get_or_404(proveedor_id)
        proveedor.nombre = empresa if empresa is not None else nombre
        proveedor.telefono = telefono
        proveedor.correo = correo
        proveedor.direccion = direccion
        proveedor.productosProveedor = productosProveedor if productosProveedor is not None else productos
        db.session.commit()
        return proveedor
    except Exception as e:
        db.session.rollback()
        raise e

def eliminar_proveedor(proveedor_id):
    """
    Elimina un proveedor de la base de datos
    """
    try:
        proveedor = Proveedores.query.get_or_404(proveedor_id)
        db.session.delete(proveedor)
        db.session.commit()
        return proveedor
    except Exception as e:
        db.session.rollback()
        raise e

# ==============================================
# SECCIÓN DE TRANSACCIONES DE COMPRA
# ==============================================

def agregar_transaccion_compra(fecha_compra, total_compra, id_proveedor, detalles):
    """
    Agrega una nueva transacción de compra con sus detalles
    """
    try:
        transaccion = TransaccionCompra(
            fechaCompra=fecha_compra,
            totalCompra=total_compra,
            idProveedor=id_proveedor
        )
        db.session.add(transaccion)
        db.session.flush()  # Para obtener el ID de la transacción
        
        for detalle in detalles:
            nuevo_detalle = DetalleCompraInsumo(
                cantCajas=detalle['cant_cajas'],
                cantUnidadesXcaja=detalle['unidades_por_caja'],
                cantMermaPorUnidad=detalle['merma_por_unidad'],
                CostoPorCaja=detalle['costo_por_caja'],
                costoUnidadXcaja=detalle['costo_unidad'],
                unidadInsumo=detalle['unidad'],
                fechaRegistro=detalle['fecha_registro'],
                fechaCaducidad=detalle['fecha_caducidad'],
                idCompra=transaccion.idTransaccionCompra,
                idInsumo=detalle['id_insumo']
            )
            db.session.add(nuevo_detalle)
            
            # Actualizar stock del insumo
            insumo = Insumo.query.get(detalle['id_insumo'])
            if insumo:
                insumo.cantidadDisponible += (detalle['cant_cajas'] * detalle['unidades_por_caja'])
        
        db.session.commit()
        return transaccion
    except Exception as e:
        db.session.rollback()
        raise e

def obtener_transacciones_compra():
    """
    Obtiene todas las transacciones de compra con sus detalles
    """
    return TransaccionCompra.query.order_by(TransaccionCompra.fechaCompra.desc()).all()

# ==============================================
# SECCIÓN DE RECETAS
# ==============================================

def obtener_recetas():
    """
    Obtiene todas las recetas con información de galletas asociadas
    """
    return [r.to_dict(include_galleta=True) for r in Receta.query.join(Galleta).order_by(Receta.id.desc()).all()]

def obtener_receta(id_receta):
    """
    Obtiene una receta específica por su ID
    """
    receta = Receta.query.get_or_404(id_receta)
    return receta.to_dict(include_galleta=True)  # Esto ya devuelve un diccionario

def agregar_receta(data, imagen=None):
    """Agrega una nueva receta a la base de datos"""
    # Validar cantidad producida
    if data['cantidad_producida'] < 1:
        raise ValueError("La cantidad producida debe ser al menos 1")
    
    # Validar tipo de galleta
    if data['galletTipo'] < 0:
        raise ValueError("El tipo de galleta no puede ser negativo")
    
    nueva_receta = Receta(
        nombre=data['nombre'],
        instrucciones=data['instrucciones'],
        cantidad_producida=data['cantidad_producida'],
        galletTipo=data['galletTipo'],
        id_galleta=data['id_galleta']
    )
    
    db.session.add(nueva_receta)
    db.session.commit()
    
    if imagen:
        # Solo guardamos la imagen en el sistema de archivos
        guardar_imagen_receta(nueva_receta, imagen, data['nombre'])
    
    return nueva_receta


def actualizar_receta(id_receta, data, imagen=None):
    """
    Actualiza los datos de una receta existente
    """
    receta = Receta.query.get_or_404(id_receta)
    
    receta.nombre = data['nombre']
    receta.instrucciones = data['instrucciones']
    receta.cantidad_producida = data['cantidad_producida']
    receta.galletTipo = data['galletTipo']
    receta.id_galleta = data['id_galleta']
    
    if imagen:
        guardar_imagen_receta(receta, imagen, data['nombre'])
    
    db.session.commit()
    return receta


def guardar_imagen_receta(receta, imagen, nombre_receta):
    from flask import current_app
    import os
    from werkzeug.utils import secure_filename
    
    upload_folder = os.path.join(current_app.root_path, 'static', 'img', 'recetas')
    
    # Debug: Imprime la ruta para verificar
    print(f"Intentando guardar imagen en: {upload_folder}")
    
    # Asegurar que el directorio existe
    os.makedirs(upload_folder, exist_ok=True)
    
    # Generar nombre de archivo seguro
    ext = imagen.filename.split('.')[-1].lower()
    filename = secure_filename(f"receta_{receta.id}.{ext}")
    filepath = os.path.join(upload_folder, filename)
    
    # Debug: Imprime información del archivo
    print(f"Guardando imagen como: {filename}")
    print(f"Ruta completa: {filepath}")
    
    # Guardar la imagen
    imagen.save(filepath)
    
    # Verificar que el archivo se creó
    if os.path.exists(filepath):
        print("Archivo guardado exitosamente")
    else:
        print("Error: El archivo no se guardó correctamente")
    
    return f"/static/img/recetas/{filename}"


def eliminar_receta(id_receta):
    """
    Elimina una receta de la base de datos
    """
    receta = Receta.query.get_or_404(id_receta)
    
    # Eliminar ingredientes asociados primero
    IngredienteReceta.query.filter_by(idReceta=id_receta).delete()
    
    db.session.delete(receta)
    db.session.commit()
    return receta

# ==============================================
# SECCIÓN DE INGREDIENTES DE RECETAS
# ==============================================

def agregar_ingrediente_receta(id_receta, id_insumo, cantidad):
    """
    Agrega un ingrediente a una receta
    """
    ingrediente = IngredienteReceta(
        idReceta=id_receta,
        idInsumo=id_insumo,
        cantidad=cantidad
    )
    db.session.add(ingrediente)
    db.session.commit()
    return ingrediente

def obtener_ingredientes_receta(id_receta):
    """
    Obtiene todos los ingredientes de una receta específica
    """
    return IngredienteReceta.query.filter_by(idReceta=id_receta).all()

def eliminar_ingrediente_receta(id_ingrediente):
    """
    Elimina un ingrediente de una receta
    """
    ingrediente = IngredienteReceta.query.get_or_404(id_ingrediente)
    db.session.delete(ingrediente)
    db.session.commit()
    return ingrediente

# ==============================================
# SECCIÓN DE GALLETAS
# ==============================================

def obtener_galletas():
    """
    Obtiene todas las galletas disponibles
    """
    return Galleta.query.order_by(Galleta.id.desc()).all()

# ==============================================
# SECCIÓN DE PRODUCCIÓN
# ==============================================

def agregar_produccion(fecha_produccion, gramos_merma, mililitros_merma, piezas_merma, 
                      produccion_total, id_receta=None, id_galleta=None):
    """
    Registra una nueva producción en el sistema
    """
    produccion = Produccion(
        fechaProduccion=fecha_produccion,
        gramosMerma=gramos_merma,
        mililitrosMerma=mililitros_merma,
        piezasMerma=piezas_merma,
        produccionTotal=produccion_total,
        idReceta=id_receta,
        idGalleta=id_galleta
    )
    db.session.add(produccion)
    db.session.commit()
    return produccion

def obtener_producciones():
    """
    Obtiene todas las producciones registradas
    """
    return Produccion.query.order_by(Produccion.fechaProduccion.desc()).all()

# ==============================================
# SECCIÓN DE HORNEADOS
# ==============================================

def registrar_horneado(fecha_horneado, temperatura_horno, tiempo_horneado, 
                      cantidad_producida, observaciones, id_receta, id_usuario, id_produccion=None):
    """
    Registra un nuevo horneado en el sistema
    """
    horneado = Horneado(
        fechaHorneado=fecha_horneado,
        temperaturaHorno=temperatura_horno,
        tiempoHorneado=tiempo_horneado,
        cantidadProducida=cantidad_producida,
        observaciones=observaciones,
        idReceta=id_receta,
        idUsuario=id_usuario,
        idProduccion=id_produccion
    )
    db.session.add(horneado)
    db.session.commit()
    return horneado

def obtener_horneados_receta(id_receta):
    """
    Obtiene todos los horneados asociados a una receta
    """
    return Horneado.query.filter_by(id_receta=id_receta).order_by(Horneado.fecha_horneado.desc()).all()

# ==============================================
# SECCIÓN DE MERMAS
# ==============================================

def registrar_merma(tipo_merma, unidad_merma, cantidad_merma, fecha_merma, 
                   id_produccion=None, id_insumo=None, id_galleta=None):
    """
    Registra una nueva merma en el sistema
    """
    merma = Merma(
        tipoMerma=tipo_merma,
        unidadMerma=unidad_merma,
        cantidadMerma=cantidad_merma,
        fechaMerma=fecha_merma,
        inProduccion=id_produccion,
        idInsumo=id_insumo,
        idGalleta=id_galleta
    )
    db.session.add(merma)
    db.session.commit()
    return merma

def obtener_mermas():
    """
    Obtiene todas las mermas registradas
    """
    return Merma.query.order_by(Merma.fechaMerma.desc()).all()

# ==============================================
# SECCIÓN DE USUARIOS
# ==============================================

def agregar_usuario(username, password, idRol, estado='Activo'):
    """
    Agrega un nuevo usuario al sistema
    """
    hashed_password = generate_password_hash(password)
    nuevo_usuario = User(
        username=username,
        contrasena=hashed_password,
        idRol=idRol,
        estado=estado
    )
    db.session.add(nuevo_usuario)
    db.session.commit()
    return nuevo_usuario

def obtener_usuarios():
    """
    Obtiene todos los usuarios (excepto clientes)
    """
    return User.query.join(Rol).filter(
        Rol.nombreRol.in_(['Administrador', 'Produccion', 'Ventas'])
    ).order_by(User.idUser.desc()).all()

def actualizar_usuario(user_id, username, idRol, estado, password=None):
    """
    Actualiza los datos de un usuario existente
    """
    usuario = User.query.get_or_404(user_id)
    usuario.username = username
    usuario.idRol = idRol
    usuario.estado = estado
    
    if password:
        usuario.contrasena = generate_password_hash(password)
    
    db.session.commit()
    return usuario

def eliminar_usuario(user_id):
    """
    Elimina un usuario del sistema
    """
    usuario = User.query.get_or_404(user_id)
    db.session.delete(usuario)
    db.session.commit()
    return usuario

def obtener_roles():
    """
    Obtiene los roles disponibles (excepto Cliente)
    """
    return Rol.query.filter(Rol.nombreRol.in_(['Administrador', 'Produccion', 'Ventas'])).all()

# ==============================================
# SECCIÓN DE CLIENTES
# ==============================================

def obtener_clientes():
    """
    Versión simplificada para obtener clientes con sus estadísticas
    """
    clientes = User.query.filter_by(idRol=4).order_by(User.idUser.desc()).all()
    
    resultados = []
    for cliente in clientes:
        # Total de pedidos
        total_pedidos = Pedido.query.filter_by(idCliente=cliente.idUser).count()
        
        # Total de compras (suma de costoPedido)
        total_compras = db.session.query(
            func.coalesce(func.sum(Pedido.costoPedido), 0)
        ).filter_by(idCliente=cliente.idUser).scalar()
        
        resultados.append({
            'idUser': cliente.idUser,
            'username': cliente.username,
            'fechaRegistro': cliente.fechaRegistro,
            'ultimoAcceso': cliente.ultimoAcceso,
            'estado': cliente.estado,
            'total_pedidos': total_pedidos,
            'total_compras': float(total_compras) if total_compras else 0.0
        })
    
    return resultados


def agregar_cliente(username, password):
    """
    Agrega un nuevo cliente al sistema
    """
    hashed_password = generate_password_hash(password)
    nuevo_cliente = User(
        username=username,
        contrasena=hashed_password,
        idRol=4,  # Rol Cliente
        estado='Activo'
    )
    db.session.add(nuevo_cliente)
    db.session.commit()
    return nuevo_cliente

def actualizar_cliente(cliente_id, username, estado):
    """
    Actualiza los datos de un cliente existente
    """
    cliente = User.query.get_or_404(cliente_id)
    if cliente.idRol != 4:
        raise ValueError("El usuario no es un cliente")
    
    cliente.username = username
    cliente.estado = estado
    
    db.session.commit()
    return cliente

def eliminar_cliente(cliente_id):
    """
    Elimina un cliente del sistema
    """
    cliente = User.query.get_or_404(cliente_id)
    if cliente.idRol != 4:
        raise ValueError("El usuario no es un cliente")
    
    db.session.delete(cliente)
    db.session.commit()
    return cliente

# ==============================================
# SECCIÓN DE PEDIDOS
# ==============================================

def crear_pedido(id_cliente, detalles):
    """
    Crea un nuevo pedido con sus detalles
    """
    try:
        total = sum(d['cantidad'] * d['precio_unitario'] for d in detalles)
        
        pedido = Pedido(
            idCliente=id_cliente,
            estadoPedido='Pendiente',
            costoPedido=total
        )
        db.session.add(pedido)
        db.session.flush()  # Para obtener el ID del pedido
        
        for detalle in detalles:
            nuevo_detalle = DetallePedido(
                idPedido=pedido.idPedidos,
                idGalleta=detalle['id_galleta'],
                cantidad=detalle['cantidad'],
                precioUnitario=detalle['precio_unitario'],
                subtotal=detalle['cantidad'] * detalle['precio_unitario']
            )
            db.session.add(nuevo_detalle)
            
            # Actualizar stock de galletas
            galleta = Galleta.query.get(detalle['id_galleta'])
            if galleta:
                galleta.cantidadDisponible -= detalle['cantidad']
        
        db.session.commit()
        return pedido
    except Exception as e:
        db.session.rollback()
        raise e

def obtener_pedidos_cliente(id_cliente):
    """
    Obtiene todos los pedidos de un cliente específico
    """
    return Pedido.query.filter_by(idCliente=id_cliente).order_by(Pedido.fechaPedido.desc()).all()

# ==============================================
# SECCIÓN DE VENTAS (CORREGIDA)
# ==============================================

def registrar_venta(fecha_venta, total_venta, id_usuario, detalles):
    """
    Registra una nueva venta en el sistema
    """
    try:
        # Crear la venta principal
        venta = Venta(
            fechaVentaGalleta=fecha_venta,
            totalVenta=total_venta,
            idUsuario=id_usuario
        )
        db.session.add(venta)
        db.session.flush()  # Para obtener el ID de la venta
        
        # Crear los detalles de venta
        for detalle in detalles:
            nuevo_detalle = DetalleVenta(
                cantGalletasVendidas=detalle['cantidad'],
                precioUnitario=detalle['precio_unitario'],
                formaVenta=detalle['forma_venta'],
                cantidadGalletas=detalle.get('cantidad_galletas'),
                pesoGramos=detalle.get('peso_gramos'),
                idGalleta=detalle['id_galleta'],
                idVenta=venta.idVenta
            )
            db.session.add(nuevo_detalle)
            
            # Actualizar stock de galletas
            galleta = Galleta.query.get(detalle['id_galleta'])
            if galleta:
                galleta.cantidadDisponible -= detalle['cantidad']
        
        db.session.commit()
        return venta
    except Exception as e:
        db.session.rollback()
        raise e
    

def obtener_ventas():
    """
    Obtiene todas las ventas registradas (versión corregida)
    """
    ventas = Venta.query.order_by(Venta.fechaVentaGalleta.desc()).all()
    return [{
        'idVenta': v.idVenta,
        'fecha': v.fechaVentaGalleta,
        'total': float(v.totalVenta),
        'usuario': v.usuario.username if v.usuario else None,
        'cliente': v.cliente.username if v.cliente else None,
        'detalle': v.detalle.to_dict() if v.detalle else None
    } for v in ventas]


def registrar_historial_venta(accion, id_usuario, id_venta):
    """
    Registra un cambio en una venta en el historial
    """
    historial = HistorialVenta(
        accionRelaizada=accion,
        idUsuario=id_usuario,
        idVenta=id_venta
    )
    db.session.add(historial)
    db.session.commit()
    return historial

# ==============================================
# CORRECCIÓN DE REPORTES
# ==============================================

def obtener_ventas_semanales():
    """Obtiene el total de ventas de la última semana"""
    inicio_semana = datetime.now() - timedelta(days=7)
    
    resultado = db.session.query(
        func.sum(Venta.totalVenta).label('total_ventas'),
        func.count(Venta.idVenta).label('cantidad_ventas')
    ).filter(
        Venta.fechaVentaGalleta >= inicio_semana
    ).first()
    
    # Log para depuración
    print(f"Ventas semanales - Total: {resultado.total_ventas}, Cantidad: {resultado.cantidad_ventas}")
    
    return {
        'total_ventas': float(resultado.total_ventas) if resultado.total_ventas else 0.0,
        'cantidad_ventas': resultado.cantidad_ventas or 0
    }


def obtener_top_galletas(limit=3):
    # Corrección en la consulta:
    resultados = db.session.query(
        Galleta.nombre,
        func.sum(DetalleVenta.cantGalletasVendidas).label('cantidad_vendida'),
        func.sum(DetalleVenta.precioUnitario * DetalleVenta.cantGalletasVendidas).label('total_ventas')
    ).join(DetalleVenta, DetalleVenta.idGalleta == Galleta.id
    ).join(Venta, Venta.idVenta == DetalleVenta.idVenta
    ).group_by(Galleta.id
    ).order_by(func.sum(DetalleVenta.cantGalletasVendidas).desc()
    ).limit(limit).all()
    
    return [{
        'nombre': r.nombre,
        'cantidad_vendida': r.cantidad_vendida,
        'total_ventas': float(r.total_ventas) if r.total_ventas else 0.0
    } for r in resultados]

def obtener_top_presentaciones(limit=3):
    """Obtiene las presentaciones más vendidas (por pieza, gramos o paquete/caja)"""
    try:
        # Primero verifica si hay datos en las tablas
        ventas_recientes = db.session.query(Venta).filter(
            Venta.fechaVentaGalleta >= (datetime.now() - timedelta(days=7))
        ).count()
        
        if ventas_recientes == 0:
            return []

        resultados = db.session.query(
            DetalleVenta.formaVenta,
            func.sum(DetalleVenta.precioUnitario * DetalleVenta.cantGalletasVendidas).label('total_ventas'),
            func.sum(DetalleVenta.cantGalletasVendidas).label('cantidad_vendida')
        ).join(Venta, DetalleVenta.idVenta == Venta.idVenta
        ).filter(
            Venta.fechaVentaGalleta >= (datetime.now() - timedelta(days=7))
        ).group_by(DetalleVenta.formaVenta
        ).order_by(func.sum(DetalleVenta.precioUnitario * DetalleVenta.cantGalletasVendidas).desc()
        ).limit(limit).all()
        
        return [{
            'formaVenta': r.formaVenta,
            'total_ventas': float(r.total_ventas) if r.total_ventas else 0.0,
            'cantidad_vendida': r.cantidad_vendida or 0
        } for r in resultados]
    except Exception as e:
        print(f"Error en obtener_top_presentaciones: {str(e)}")
        return []

def obtener_estimacion_costos():
    """
    Obtiene estimación de costos vs ganancias de la última semana
    """
    inicio_semana = datetime.now() - timedelta(days=7)
    
    # Total compras de insumos
    compras = db.session.query(
        func.sum(TransaccionCompra.totalCompra).label('total_compras')
    ).filter(
        TransaccionCompra.fechaCompra >= inicio_semana
    ).first()
    
    # Total ventas
    ventas = db.session.query(
        func.sum(Venta.totalVenta).label('total_ventas')
    ).filter(
        Venta.fechaVentaGalleta >= inicio_semana
    ).first()
    
    # Total mermas
    mermas = db.session.query(
        func.sum(Merma.cantidadMerma * DetalleCompraInsumo.costoUnidadXcaja).label('valor_mermas')
    ).join(DetalleCompraInsumo, Merma.idInsumo == DetalleCompraInsumo.idInsumo
    ).filter(
        Merma.fechaMerma >= inicio_semana
    ).first()
    
    return {
        'compras': float(compras.total_compras) if compras.total_compras else 0.0,
        'ventas': float(ventas.total_ventas) if ventas.total_ventas else 0.0,
        'mermas': float(mermas.valor_mermas) if mermas.valor_mermas else 0.0,
        'ganancia': (float(ventas.total_ventas) if ventas.total_ventas else 0.0) - 
                   (float(compras.total_compras) if compras.total_compras else 0.0) - 
                   (float(mermas.valor_mermas) if mermas.valor_mermas else 0.0)
    }

def obtener_historial_ventas_semanales(semanas=4):
    """
    Obtiene el historial de ventas de las últimas N semanas
    """
    semanas_labels = []
    ventas_data = []
    
    for i in range(semanas, 0, -1):
        inicio_semana = datetime.now() - timedelta(weeks=i)
        fin_semana = inicio_semana + timedelta(days=6)
        
        total = db.session.query(
            func.sum(Venta.totalVenta).label('total_ventas')
        ).filter(
            Venta.fechaVentaGalleta.between(inicio_semana, fin_semana)
        ).first()
        
        semanas_labels.append(f"Semana {semanas - i + 1}")
        ventas_data.append(float(total.total_ventas) if total.total_ventas else 0.0)
    
    return {
        'semanas': semanas_labels,
        'datos': ventas_data
    }

def obtener_ventas_por_dia(dias=7):
    """Obtiene las ventas por día de la última semana"""
    fecha_inicio = datetime.now() - timedelta(days=dias)
    
    resultados = db.session.query(
        func.date(Venta.fechaVentaGalleta).label('fecha'),
        func.sum(Venta.totalVenta).label('total')
    ).filter(
        Venta.fechaVentaGalleta >= fecha_inicio
    ).group_by(
        func.date(Venta.fechaVentaGalleta)
    ).order_by(
        func.date(Venta.fechaVentaGalleta)
    ).all()
    
    # Rellenar días faltantes con cero
    fechas = [(datetime.now() - timedelta(days=i)).date() for i in range(dias, 0, -1)]
    datos = {r.fecha: float(r.total) for r in resultados}
    
    return {
        'fechas': [f.strftime('%Y-%m-%d') for f in fechas],
        'datos': [float(datos.get(f, 0)) for f in fechas]
    }

def obtener_distribucion_ventas():
    """Obtiene la distribución de ventas por tipo de galleta"""
    resultados = db.session.query(
        Galleta.nombre.label('nombre'),
        func.sum(DetalleVenta.cantGalletasVendidas).label('cantidad'),
        func.sum(DetalleVenta.precioUnitario * DetalleVenta.cantGalletasVendidas).label('total')
    ).join(DetalleVenta, DetalleVenta.idGalleta == Galleta.id
    ).join(Venta, Venta.idVenta == DetalleVenta.idVenta
    ).filter(
        Venta.fechaVentaGalleta >= (datetime.now() - timedelta(days=30))
    ).group_by(Galleta.nombre
    ).order_by(func.sum(DetalleVenta.precioUnitario * DetalleVenta.cantGalletasVendidas).desc()
    ).limit(5).all()
    
    return {
        'nombres': [r.nombre for r in resultados],
        'cantidades': [r.cantidad for r in resultados],
        'totales': [float(r.total) if r.total else 0.0 for r in resultados]
    }


def obtener_produccion_semanal():
    """Obtiene datos de producción de la última semana"""
    inicio_semana = datetime.now() - timedelta(days=7)
    
    resultados = db.session.query(
        func.date(Produccion.fechaProduccion).label('fecha'),
        func.sum(Produccion.produccionTotal).label('total_producido'),
        func.sum(Produccion.gramosMerma + Produccion.mililitrosMerma + Produccion.piezasMerma).label('total_merma')
    ).filter(
        Produccion.fechaProduccion >= inicio_semana
    ).group_by(
        func.date(Produccion.fechaProduccion)
    ).order_by(
        func.date(Produccion.fechaProduccion)
    ).all()
    
    return {
        'fechas': [r.fecha.strftime('%Y-%m-%d') for r in resultados],
        'producido': [r.total_producido for r in resultados],
        'merma': [r.total_merma for r in resultados]
    }


def obtener_eficiencia_produccion():
    """Calcula la eficiencia de producción por tipo de galleta"""
    try:
        # Primero verifica si hay datos de producción
        produccion_reciente = db.session.query(Produccion).filter(
            Produccion.fechaProduccion >= (datetime.now() - timedelta(days=7))
        ).count()
        
        if produccion_reciente == 0:
            return []

        resultados = db.session.query(
            Galleta.nombre,
            func.sum(Produccion.produccionTotal).label('total_producido'),
            func.sum(
                case(
                    (Produccion.gramosMerma > 0, Produccion.gramosMerma),
                    (Produccion.mililitrosMerma > 0, Produccion.mililitrosMerma),
                    (Produccion.piezasMerma > 0, Produccion.piezasMerma),
                    else_=0
                )
            ).label('total_merma'),
            (func.sum(Produccion.produccionTotal) / 
             (func.sum(Produccion.produccionTotal) + 
              func.sum(
                  case(
                      (Produccion.gramosMerma > 0, Produccion.gramosMerma),
                      (Produccion.mililitrosMerma > 0, Produccion.mililitrosMerma),
                      (Produccion.piezasMerma > 0, Produccion.piezasMerma),
                      else_=0
                  )
              )) * 100).label('eficiencia')
        ).join(Produccion, Produccion.idGalleta == Galleta.id
        ).filter(
            Produccion.fechaProduccion >= (datetime.now() - timedelta(days=7))
        ).group_by(Galleta.nombre
        ).having(
            (func.sum(Produccion.produccionTotal) + 
             func.sum(
                 case(
                     (Produccion.gramosMerma > 0, Produccion.gramosMerma),
                     (Produccion.mililitrosMerma > 0, Produccion.mililitrosMerma),
                     (Produccion.piezasMerma > 0, Produccion.piezasMerma),
                     else_=0
                 )
             )) > 0
        ).order_by(func.sum(Produccion.produccionTotal).desc()
        ).limit(5).all()
        
        return [{
            'galleta': r.nombre,
            'producido': r.total_producido or 0,
            'merma': r.total_merma or 0,
            'eficiencia': float(r.eficiencia) if r.eficiencia is not None else 0.0
        } for r in resultados]
    except Exception as e:
        print(f"Error en obtener_eficiencia_produccion: {str(e)}")
        return []


def obtener_notificaciones_recientes(limit=5, usuario_id=None):
    """Obtiene las notificaciones más recientes no vistas"""
    query = Notificacion.query.filter(
        Notificacion.estado == 'Nueva'
    )
    
    if usuario_id:
        query = query.filter(Notificacion.id_usuario == usuario_id)
    
    return query.order_by(
        Notificacion.fecha_creacion.desc()
    ).limit(limit).all()

def crear_notificacion(tipo, mensaje, id_usuario=None, id_insumo=None, id_galleta=None):
    """Crea una nueva notificación en el sistema"""
    notificacion = Notificacion(
        tipo=tipo,
        mensaje=mensaje,
        id_usuario=id_usuario,
        id_insumo=id_insumo,
        id_galleta=id_galleta
    )
    db.session.add(notificacion)
    db.session.commit()
    return notificacion

def marcar_notificacion_como_vista(notificacion_id):
    """Marca una notificación como vista"""
    notificacion = Notificacion.query.get(notificacion_id)
    if notificacion:
        notificacion.estado = 'Vista'
        notificacion.fecha_visto = db.func.current_timestamp()
        db.session.commit()
    return notificacion

def obtener_recomendacion_producto():
    """Obtiene la galleta más rentable para recomendar su venta"""
    try:
        # Primero verificar si hay datos básicos
        if not db.session.query(Galleta).count():
            return None

        # Consulta optimizada para obtener galletas con mejor margen
        subquery = db.session.query(
            IngredienteReceta.idReceta,
            func.sum(DetalleCompraInsumo.costoUnidadXcaja * IngredienteReceta.cantidad).label('costo_total')
        ).join(DetalleCompraInsumo, DetalleCompraInsumo.idInsumo == IngredienteReceta.idInsumo
        ).group_by(IngredienteReceta.idReceta).subquery()

        resultados = db.session.query(
            Galleta.nombre,
            Galleta.cantidad_disponible,
            Galleta.precio_unitario,
            (Galleta.precio_unitario - func.coalesce(subquery.c.costo_total, 0) / Receta.cantidad_producida).label('margen_absoluto'),
            func.count(DetalleVenta.idDetalleVenta).label('demanda_semanal')
        ).outerjoin(Receta, Receta.id_galleta == Galleta.id
        ).outerjoin(subquery, subquery.c.idReceta == Receta.id
        ).outerjoin(DetalleVenta, DetalleVenta.idGalleta == Galleta.id
        ).outerjoin(Venta, Venta.idVenta == DetalleVenta.idVenta
        ).filter(
            Venta.fechaVentaGalleta >= (datetime.now() - timedelta(days=7)),
            Galleta.cantidad_disponible > 0
        ).group_by(Galleta.id, Receta.cantidad_producida, subquery.c.costo_total
        ).order_by(
            (Galleta.precio_unitario - func.coalesce(subquery.c.costo_total, 0) / Receta.cantidad_producida).desc()
        ).first()

        if resultados:
            margen_porcentaje = (resultados.margen_absoluto / resultados.precio_unitario) * 100 if resultados.precio_unitario else 0
            return {
                'nombre': resultados.nombre,
                'margen': float(margen_porcentaje),
                'inventario': resultados.cantidad_disponible,
                'demanda_semanal': resultados.demanda_semanal or 0
            }
        
        # Si no hay resultados, intentar una consulta más simple
        galleta = db.session.query(Galleta).filter(
            Galleta.cantidad_disponible > 0
        ).order_by(
            Galleta.precio_unitario.desc()
        ).first()
        
        if galleta:
            return {
                'nombre': galleta.nombre,
                'margen': 30.0,  # Valor por defecto si no se puede calcular
                'inventario': galleta.cantidad_disponible,
                'demanda_semanal': 0  # Valor por defecto
            }
            
        return None
    except Exception as e:
        print(f"Error en obtener_recomendacion_producto: {str(e)}")
        # Registrar el error en logs
        crear_notificacion('Error Sistema', f'Error al calcular recomendación: {str(e)}')
        return None
        

def obtener_costos_produccion():
    """Obtiene los costos de producción por lote para cada tipo de galleta"""
    try:
        # Verificar si hay datos suficientes
        galletas_con_receta = db.session.query(Galleta.id).join(Receta).count()
        if galletas_con_receta == 0:
            return []

        resultados = db.session.query(
            Galleta.nombre,
            (func.coalesce(
                func.sum(DetalleCompraInsumo.costoUnidadXcaja * IngredienteReceta.cantidad), 0
            ) / Receta.cantidad_producida).label('costo_lote')
        ).join(Receta, Receta.id_galleta == Galleta.id
        ).join(IngredienteReceta, IngredienteReceta.idReceta == Receta.id
        ).join(DetalleCompraInsumo, DetalleCompraInsumo.idInsumo == IngredienteReceta.idInsumo
        ).group_by(Galleta.id, Receta.cantidad_producida
        ).order_by(Galleta.nombre
        ).all()

        # Depuración: Imprimir resultados para verificar
        print("Resultados de costos de producción:", resultados)
        
        return [{
            'nombre': r.nombre,
            'costo': float(r.costo_lote) if r.costo_lote else 0.0
        } for r in resultados if r.costo_lote is not None]
    except Exception as e:
        print(f"Error en obtener_costos_produccion: {str(e)}")
        # Registrar el error en logs
        crear_notificacion('Error Sistema', f'Error al calcular costos de producción: {str(e)}')
        return []
    