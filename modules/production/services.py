from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from .models import Galleta, Insumo, Receta,Horneado, db, TransaccionCompra, DetalleCompraInsumo, Notificacion, Merma
from modules.admin.models import Proveedores as Proveedor
from modules.shared.models import Rol as Role
from modules.shared.models import User as Usuario
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy import func, and_, desc


# Creamos una clase base de servicio
class BaseService:
    def __init__(self, db_session):
        self.db_session = db_session
    
    def add(self, obj):
        try:
            self.db_session.add(obj)
            self.db_session.commit()
            return obj
        except SQLAlchemyError as e:
            self.db_session.rollback()
            print(f"Error al agregar: {e}")
            return None

    def get(self, model, id):
        try:
            return self.db_session.query(model).get(id)
        except SQLAlchemyError as e:
            print(f"Error al obtener el objeto: {e}")
            return None

    def get_all(self, model):
        try:
            return self.db_session.query(model).all()
        except SQLAlchemyError as e:
            print(f"Error al obtener todos los objetos: {e}")
            return []

    def update(self, obj):
        try:
            self.db_session.merge(obj)
            self.db_session.commit()
            return obj
        except SQLAlchemyError as e:
            self.db_session.rollback()
            print(f"Error al actualizar: {e}")
            return None

    def delete(self, obj):
        try:
            self.db_session.delete(obj)
            self.db_session.commit()
            return True
        except SQLAlchemyError as e:
            self.db_session.rollback()
            print(f"Error al eliminar: {e}")
            return False

# Servicio para manejar los proveedores
class ProveedorService(BaseService):
    def __init__(self, db_session):
        super().__init__(db_session)

    def add_proveedor(self, nombre, telefono, correo, direccion, productosProveedor):
        proveedor = proveedor(
            nombre=nombre,
            telefono=telefono,
            correo=correo,
            direccion=direccion,
            productosProveedor=productosProveedor
        )
        return self.add(proveedor)

    def get_proveedor(self, id_proveedor):
        return self.get(Proveedor, id_proveedor)

    def get_all_proveedores(self):
        return self.get_all(Proveedor)

# Servicio para manejar las galletas
class GalletaService(BaseService):
    def __init__(self, db_session):
        super().__init__(db_session)

    def add_galleta(self, nombreGalleta, precioUnitario, cantidadDisponible, gramajeGalleta, tipoGalleta, fechaAnaquel, fechaFinalAnaquel):
        galleta = Galleta(
            nombreGalleta=nombreGalleta,
            precioUnitario=precioUnitario,
            cantidadDisponible=cantidadDisponible,
            gramajeGalleta=gramajeGalleta,
            tipoGalleta=tipoGalleta,
            fechaAnaquel=fechaAnaquel,
            fechaFinalAnaquel=fechaFinalAnaquel
        )
        return self.add(galleta)

    def get_galleta(self, id_galleta):
        return self.get(Galleta, id_galleta)

    def get_all_galletas(self):
        return self.get_all(Galleta)

# Servicio para manejar los insumos
class InsumoService(BaseService):
    def __init__(self, db_session):
        super().__init__(db_session)

    def add_insumo(self, nombre, unidadInsumo, cantidadDisponible, cantidadMinima):
        insumo = Insumo(
            nombre=nombre,
            unidad=unidadInsumo,  # Changed from unidadInsumo to unidad
            cantidad_disponible=cantidadDisponible,  # Changed to use the snake_case attribute name
            cantidad_minima=cantidadMinima  # Changed to use the snake_case attribute name
        )
        return self.add(insumo)

    def get_insumo_por_nombre(self, nombre):
        try:
            return self.db_session.query(Insumo).filter(Insumo.nombre == nombre).first()
        except SQLAlchemyError as e:
            print(f"Error al buscar insumo por nombre: {e}")
            return None
    
    
    def get_insumo(self, id_insumo):
        return self.get(Insumo, id_insumo)

    def get_all_insumos(self):
        return self.get_all(Insumo)

# Servicio para manejar las recetas
class RecetaService(BaseService):
    def __init__(self, db_session):
        super().__init__(db_session)

    def add_receta(self, nombreReceta, instruccionReceta, cantGalletasProduction, galletTipo, idGalleta):
        receta = Receta(
            nombreReceta=nombreReceta,
            instruccionReceta=instruccionReceta,
            cantGalletasProduction=cantGalletasProduction,
            galletTipo=galletTipo,
            idGalleta=idGalleta
        )
        return self.add(receta)

    def get_receta(self, id_receta):
        return self.get(Receta, id_receta)

    def get_all_recetas(self):
        return self.get_all(Receta)


# Añadir al archivo services.py existente

class HorneadoService(BaseService):
    def __init__(self, db_session):
        super().__init__(db_session)
    
    def registrar_horneado(self, temperatura_horno, tiempo_horneado, cantidad_producida, observaciones, id_receta, id_usuario):
        """
        Registra un nuevo horneado utilizando el procedimiento almacenado sp_RegistrarHorneado
        """
        try:
            result = self.db_session.execute(
                text("""
                    CALL sp_RegistrarHorneado(:temperatura, :tiempo, :cantidad, :observaciones, :id_receta, :id_usuario)
                """),
                {
                    'temperatura': temperatura_horno,
                    'tiempo': tiempo_horneado,
                    'cantidad': cantidad_producida,
                    'observaciones': observaciones,
                    'id_receta': id_receta,
                    'id_usuario': id_usuario
                }
            )
            self.db_session.commit()
            return True
        except SQLAlchemyError as e:
            self.db_session.rollback()
            print(f"Error al registrar horneado: {e}")
            return False
    
    def get_horneado(self, id_horneado):
        return self.get(Horneado, id_horneado)
    
    def get_all_horneados(self):
        return self.get_all(Horneado)
    
    def get_horneados_filtrados(self, fecha_inicio=None, fecha_fin=None, id_receta=None):
        """
        Obtiene horneados con filtros opcionales de fecha y receta
        """
        try:
            query = self.db_session.query(Horneado).order_by(Horneado.fecha_horneado.desc())
            
            if fecha_inicio:
                query = query.filter(Horneado.fecha_horneado >= fecha_inicio)
            
            if fecha_fin:
                # Ajustamos fecha_fin para incluir todo el día
                fecha_fin_completa = datetime.strptime(fecha_fin, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(Horneado.fecha_horneado < fecha_fin_completa)
            
            if id_receta:
                query = query.filter(Horneado.id_receta == id_receta)
            
            return query.all()
        except SQLAlchemyError as e:
            print(f"Error al obtener horneados filtrados: {e}")
            return []
    
    def get_estadisticas_horneado(self, dias=30):
        """
        Obtiene estadísticas de horneado de los últimos X días
        """
        try:
            fecha_limite = datetime.now() - timedelta(days=dias)
            
            # Total de horneados en el período
            total_horneados = self.db_session.query(func.count(Horneado.id)).filter(
                Horneado.fecha_horneado >= fecha_limite
            ).scalar()
            
            # Total de galletas producidas en el período
            total_galletas = self.db_session.query(func.sum(Horneado.cantidad_producida)).filter(
                Horneado.fecha_horneado >= fecha_limite
            ).scalar() or 0
            
            # Galletas por tipo/receta
            galletas_por_receta = self.db_session.query(
                Receta.nombre,
                func.sum(Horneado.cantidad_producida).label('total')
            ).join(Receta, Horneado.id_receta == Receta.id).filter(
                Horneado.fecha_horneado >= fecha_limite
            ).group_by(Receta.nombre).all()
            
            # Horneados por día (para gráficas)
            horneados_por_dia = self.db_session.query(
                func.date(Horneado.fecha_horneado).label('fecha'),
                func.sum(Horneado.cantidad_producida).label('total')
            ).filter(
                Horneado.fecha_horneado >= fecha_limite
            ).group_by(func.date(Horneado.fecha_horneado)).all()
            
            return {
                'total_horneados': total_horneados,
                'total_galletas': total_galletas,
                'galletas_por_receta': [{'nombre': r[0], 'total': r[1]} for r in galletas_por_receta],
                'horneados_por_dia': [{'fecha': r[0].strftime('%Y-%m-%d'), 'total': r[1]} for r in horneados_por_dia]
            }
        except SQLAlchemyError as e:
            print(f"Error al obtener estadísticas de horneado: {e}")
            return {
                'total_horneados': 0,
                'total_galletas': 0,
                'galletas_por_receta': [],
                'horneados_por_dia': []
            }
            
            
###########################################

class CompraService:
    def __init__(self, db_session):
        self.db_session = db_session
    
    def get_all_proveedores(self):
        """
        Obtiene todos los proveedores registrados
        """
        try:
            return self.db_session.query(Proveedor).order_by(Proveedor.nombre).all()
        except SQLAlchemyError as e:
            print(f"Error al obtener proveedores: {e}")
            return []
    
    def get_proveedor(self, id_proveedor):
        """
        Obtiene un proveedor por su ID
        """
        try:
            return self.db_session.query(Proveedor).get(id_proveedor)
        except SQLAlchemyError as e:
            print(f"Error al obtener proveedor: {e}")
            return None
    
    def get_all_insumos(self):
        """
        Obtiene todos los insumos registrados
        """
        try:
            return self.db_session.query(Insumo).order_by(Insumo.nombre).all()
        except SQLAlchemyError as e:
            print(f"Error al obtener insumos: {e}")
            return []
    
    def registrar_compra(self, id_proveedor, fecha_compra=None):
        if fecha_compra is None:
            fecha_compra = datetime.now().date()

        try:
            # Inicializar la variable de salida
            self.db_session.execute(text("SET @id_transaccion = 0"))
            
            # Llamada al procedimiento almacenado
            self.db_session.execute(
                text("CALL RegistrarCompraInsumo(:p_idProveedor, :p_fechaCompra, @id_transaccion)"),
                {
                    'p_idProveedor': id_proveedor,
                    'p_fechaCompra': fecha_compra
                }
            )

            # Obtener el valor de la variable de salida
            id_transaccion = self.db_session.execute(text("SELECT @id_transaccion")).scalar()
            
            # Verificar que se haya obtenido un ID válido
            if not id_transaccion:
                print("No se pudo obtener un ID de transacción válido")
                return None
                
            self.db_session.commit()
            return id_transaccion
        except SQLAlchemyError as e:
            self.db_session.rollback()
            print(f"Error al registrar compra: {e}")
            return None

            
            

    
    def agregar_detalle_compra(self, id_compra, id_insumo, cant_cajas, cant_unidades_caja, 
                      cant_merma_unidad, costo_caja, unidad_insumo, 
                      fecha_registro=None, fecha_caducidad=None):
        if fecha_registro is None:
            fecha_registro = datetime.now().date()

        try:
            # Asegurarnos de que unidad_insumo sea un string
            unidad_str = str(unidad_insumo)
            
            # Validar que sea uno de los valores válidos
            if unidad_str not in ['Gr', 'mL', 'Pz']:
                print(f"Error: Unidad de insumo inválida: {unidad_str}")
                return False
                
            # Llamar al procedimiento almacenado
            self.db_session.execute(
                text("""CALL AgregarDetalleCompraInsumo(
                    :p_idCompra, :p_idInsumo, :p_cantCajas, :p_cantUnidadesXcaja, 
                    :p_cantMermaPorUnidad, :p_CostoPorCaja, :p_unidadInsumo, 
                    :p_fechaRegistro, :p_fechaCaducidad)"""),
                {
                    'p_idCompra': id_compra,
                    'p_idInsumo': id_insumo,
                    'p_cantCajas': cant_cajas,
                    'p_cantUnidadesXcaja': cant_unidades_caja,
                    'p_cantMermaPorUnidad': cant_merma_unidad,
                    'p_CostoPorCaja': costo_caja,
                    'p_unidadInsumo': unidad_str,
                    'p_fechaRegistro': fecha_registro,
                    'p_fechaCaducidad': fecha_caducidad
                }
            )
            self.db_session.commit()
            print(f"Detalle de compra registrado exitosamente para insumo {id_insumo}.")
            return True
        except SQLAlchemyError as e:
            self.db_session.rollback()
            print(f"Error al agregar detalle de compra para insumo {id_insumo}: {e}")
            return False

    
    def get_compras(self, limit=100):
        """
        Obtiene las últimas compras realizadas
        """
        try:
            return self.db_session.query(TransaccionCompra)\
                .order_by(TransaccionCompra.fecha_compra.desc())\
                .limit(limit).all()
        except SQLAlchemyError as e:
            print(f"Error al obtener compras: {e}")
            return []
    
    def get_compra(self, id_compra):
        """
        Obtiene una compra por su ID
        """
        try:
            return self.db_session.query(TransaccionCompra).get(id_compra)
        except SQLAlchemyError as e:
            print(f"Error al obtener compra: {e}")
            return None
    
    def get_detalles_compra(self, id_compra):
        """
        Obtiene los detalles de una compra
        """
        try:
            return self.db_session.query(DetalleCompraInsumo)\
                .filter(DetalleCompraInsumo.id_compra == id_compra)\
                .all()
        except SQLAlchemyError as e:
            print(f"Error al obtener detalles de compra: {e}")
            return []
    
    def get_notificaciones(self, estatus=None, limit=10):
        """
        Obtiene las notificaciones del sistema
        """
        try:
            query = self.db_session.query(Notificacion).order_by(Notificacion.fecha_creacion.desc())
            
            if estatus:
                query = query.filter(Notificacion.estatus == estatus)
            
            return query.limit(limit).all()
        except SQLAlchemyError as e:
            print(f"Error al obtener notificaciones: {e}")
            return []
    
    def marcar_notificacion_vista(self, id_notificacion):
        """
        Marca una notificación como vista
        """
        try:
            notificacion = self.db_session.query(Notificacion).get(id_notificacion)
            if notificacion:
                notificacion.estatus = 'Vista'
                notificacion.fecha_visto = datetime.now()
                self.db_session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.db_session.rollback()
            print(f"Error al marcar notificación como vista: {e}")
            return False
    
    def resolver_notificacion(self, id_notificacion):
        """
        Marca una notificación como resuelta
        """
        try:
            notificacion = self.db_session.query(Notificacion).get(id_notificacion)
            if notificacion:
                notificacion.estatus = 'Resuelto'
                self.db_session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.db_session.rollback()
            print(f"Error al resolver notificación: {e}")
            return False
    
    def obtener_mermas(self, tipo_merma=None, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene las mermas registradas con filtros opcionales
        """
        try:
            query = self.db_session.query(Merma).order_by(Merma.fecha_merma.desc())
            
            if tipo_merma:
                query = query.filter(Merma.tipo_merma == tipo_merma)
            
            if fecha_inicio:
                query = query.filter(Merma.fecha_merma >= fecha_inicio)
            
            if fecha_fin:
                query = query.filter(Merma.fecha_merma <= fecha_fin)
            
            return query.all()
        except SQLAlchemyError as e:
            print(f"Error al obtener mermas: {e}")
            return []