from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from .models import Galleta, Insumo, Receta,Horneado,Usuario, db
from modules.admin.models import Proveedores
from datetime import datetime, timedelta
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
        proveedor = Proveedores(
            nombre=nombre,
            telefono=telefono,
            correo=correo,
            direccion=direccion,
            productosProveedor=productosProveedor
        )
        return self.add(proveedor)

    def get_proveedor(self, id_proveedor):
        return self.get(Proveedores, id_proveedor)

    def get_all_proveedores(self):
        return self.get_all(Proveedores)

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
            # Usamos SQLAlchemy para ejecutar el procedimiento almacenado
            result = self.db_session.execute(
                """
                CALL sp_RegistrarHorneado(:temperatura, :tiempo, :cantidad, :observaciones, :id_receta, :id_usuario)
                """,
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