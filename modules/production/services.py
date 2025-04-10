from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from .models import Galleta, Insumo, Receta, Horneado, Produccion, IngredienteReceta, db
from modules.shared.models import User, Rol
from modules.admin.models import Proveedores
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy import func, and_, desc

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
        return self.get(Proveedores, id_proveedor)

    def get_all_proveedores(self):
        return self.get_all(Proveedores)

class GalletaService(BaseService):
    def __init__(self, db_session):
        super().__init__(db_session)

    def add_galleta(self, nombre, precio_unitario, cantidad_disponible, gramaje, tipo_galleta, fecha_anaquel, fecha_final_anaquel):
        galleta = Galleta(
            nombre=nombre,
            precio_unitario=precio_unitario,
            cantidad_disponible=cantidad_disponible,
            gramaje=gramaje,
            tipo_galleta=tipo_galleta,
            fecha_anaquel=fecha_anaquel,
            fecha_final_anaquel=fecha_final_anaquel
        )
        return self.add(galleta)

    def get_galleta(self, id_galleta):
        return self.get(Galleta, id_galleta)

    def get_all_galletas(self):
        return self.get_all(Galleta)

class InsumoService(BaseService):
    def __init__(self, db_session):
        super().__init__(db_session)

    def add_insumo(self, nombre, unidad, cantidad_disponible, cantidad_minima):
        insumo = Insumo(
            nombre=nombre,
            unidad=unidad,
            cantidad_disponible=cantidad_disponible,
            cantidad_minima=cantidad_minima
        )
        return self.add(insumo)

    def get_insumo(self, id_insumo):
        return self.get(Insumo, id_insumo)

    def get_insumo_por_nombre(self, nombre):
        try:
            return self.db_session.query(Insumo).filter(Insumo.nombre == nombre).first()
        except SQLAlchemyError as e:
            print(f"Error al buscar insumo por nombre: {e}")
            return None

    def get_all_insumos(self):
        return self.get_all(Insumo)

class RecetaService(BaseService):
    def __init__(self, db_session):
        super().__init__(db_session)

    def add_receta(self, nombre, instrucciones, cantidad_producida, galletTipo, id_galleta):
        receta = Receta(
            nombre=nombre,
            instrucciones=instrucciones,
            cantidad_producida=cantidad_producida,
            galletTipo=galletTipo,
            id_galleta=id_galleta
        )
        return self.add(receta)

    def get_receta(self, id_receta):
        return self.get(Receta, id_receta)

    def get_all_recetas(self):
        return self.db_session.query(Receta).join(Galleta).order_by(Receta.id.desc()).all()

class HorneadoService(BaseService):
    def __init__(self, db_session):
        super().__init__(db_session)
    
    def registrar_horneado(self, temperatura_horno, tiempo_horneado, cantidad_producida, observaciones, id_receta, id_usuario):
        try:
            horneado = Horneado(
                fecha_horneado=datetime.now(),
                temperatura_horno=temperatura_horno,
                tiempo_horneado=tiempo_horneado,
                cantidad_producida=cantidad_producida,
                observaciones=observaciones,
                id_receta=id_receta,
                id_usuario=id_usuario
            )
            return self.add(horneado)
        except Exception as e:
            print(f"Error al registrar horneado: {e}")
            return None
    
    def get_horneado(self, id_horneado):
        return self.get(Horneado, id_horneado)
    
    def get_all_horneados(self):
        return self.get_all(Horneado)
    
    def get_horneados_filtrados(self, fecha_inicio=None, fecha_fin=None, id_receta=None):
        try:
            query = self.db_session.query(Horneado).order_by(Horneado.fecha_horneado.desc())
            
            if fecha_inicio:
                query = query.filter(Horneado.fecha_horneado >= fecha_inicio)
            
            if fecha_fin:
                fecha_fin_completa = datetime.strptime(fecha_fin, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(Horneado.fecha_horneado < fecha_fin_completa)
            
            if id_receta:
                query = query.filter(Horneado.id_receta == id_receta)
            
            return query.all()
        except SQLAlchemyError as e:
            print(f"Error al obtener horneados filtrados: {e}")
            return []
    
    def get_estadisticas_horneado(self, dias=30):
        try:
            fecha_limite = datetime.now() - timedelta(days=dias)
            
            total_horneados = self.db_session.query(func.count(Horneado.id)).filter(
                Horneado.fecha_horneado >= fecha_limite
            ).scalar()
            
            total_galletas = self.db_session.query(func.sum(Horneado.cantidad_producida)).filter(
                Horneado.fecha_horneado >= fecha_limite
            ).scalar() or 0
            
            galletas_por_receta = self.db_session.query(
                Receta.nombre,
                func.sum(Horneado.cantidad_producida).label('total')
            ).join(Receta, Horneado.id_receta == Receta.id).filter(
                Horneado.fecha_horneado >= fecha_limite
            ).group_by(Receta.nombre).all()
            
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

class ProduccionService(BaseService):
    def __init__(self, db_session):
        super().__init__(db_session)
    
    def agregar_produccion(self, fecha_produccion, gramos_merma, mililitros_merma, piezas_merma, produccion_total, id_receta=None, id_galleta=None):
        produccion = Produccion(
            fechaProduccion=fecha_produccion,
            gramosMerma=gramos_merma,
            mililitrosMerma=mililitros_merma,
            piezasMerma=piezas_merma,
            produccionTotal=produccion_total,
            idReceta=id_receta,
            idGalleta=id_galleta
        )
        return self.add(produccion)
    
    def get_producciones(self):
        return self.get_all(Produccion)

class UserService(BaseService):
    def __init__(self, db_session):
        super().__init__(db_session)
    
    def get_user(self, id_user):
        return self.get(User, id_user)
    
    def get_all_users(self):
        return self.db_session.query(User).join(Rol).filter(
            Rol.nombreRol.in_(['Administrador', 'Produccion', 'Ventas'])
        ).order_by(User.idUser.desc()).all()
    
    def get_roles(self):
        return self.db_session.query(Rol).filter(
            Rol.nombreRol.in_(['Administrador', 'Produccion', 'Ventas'])
        ).all()