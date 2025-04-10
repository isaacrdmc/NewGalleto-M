from flask_login import current_user
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
# from .models import Galleta, Insumo, Produccion, Receta,Horneado, SolicitudHorneado, db, TransaccionCompra, DetalleCompraInsumo, Notificacion, Merma
from .models import Galleta, Insumo, Produccion, Receta,Horneado, SolicitudHorneado, db, Notificacion
from modules.admin.models import Proveedores as Proveedor
from modules.shared.models import Rol as Role, User
from modules.shared.models import User as Usuario
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy import func, and_, desc
from sqlalchemy.orm import joinedload

# En services.py, al inicio del archivo
UNIDADES_COMPATIBLES = {
    'Gr': ['Gr', 'Kg'],       # Gramos puede comprarse en gramos o kilogramos
    'mL': ['mL', 'L'],        # Mililitros puede comprarse en ml o litros
    'Pz': ['Pz', 'Dz']        # Piezas puede comprarse en piezas o docenas
}

FACTORES_CONVERSION = {
    ('Kg', 'Gr'): 1000,      # 1 Kg = 1000 Gr
    ('L', 'mL'): 1000,       # 1 L = 1000 mL
    ('Dz', 'Pz'): 12         # 1 Dz = 12 Pz
}
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
        return self.get(Proveedor, id_proveedor)

    def get_all_proveedores(self):
        return self.get_all(Proveedor)

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
    
    def get_horneados_filtrados(self, fecha_inicio=None, fecha_fin=None, id_receta=None, id_usuario=None):
        """
        Obtiene horneados con filtros opcionales de fecha, receta y usuario
        """
        try:
            query = self.db_session.query(Horneado).order_by(Horneado.fecha_horneado.desc())
            
            if fecha_inicio:
                query = query.filter(Horneado.fecha_horneado >= fecha_inicio)
            
            if fecha_fin:
                fecha_fin_completa = datetime.strptime(fecha_fin, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(Horneado.fecha_horneado < fecha_fin_completa)
            
            if id_receta:
                query = query.filter(Horneado.id_receta == id_receta)
                
            if id_usuario:
                query = query.filter(Horneado.id_usuario == id_usuario)
            
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
        return self.db_session.query(User).join(Role).filter(
            Role.nombreRol.in_(['Administrador', 'Produccion', 'Ventas'])
        ).order_by(User.idUser.desc()).all()
    
    def get_roles(self):
        return self.db_session.query(Role).filter(
            Role.nombreRol.in_(['Administrador', 'Produccion', 'Ventas'])
        ).all()
        
############################
# Añadir al final de services.py

class SolicitudHorneadoService:
    def __init__(self, db_session):
        self.db_session = db_session
    
    def crear_solicitud(self, id_receta, cantidad_lotes, id_usuario):
        try:
            print(f"Creando solicitud - Receta: {id_receta}, Lotes: {cantidad_lotes}, Usuario: {id_usuario}")  # Debug
            
            # 1. Ejecutar el procedimiento almacenado
            self.db_session.execute(
                text("CALL sp_SolicitarHorneado(:id_receta, :cantidad, :usuario, @resultado)"),
                {
                    'id_receta': id_receta,
                    'cantidad': cantidad_lotes,
                    'usuario': id_usuario
                }
            )
            
            # 2. Obtener el mensaje de resultado
            resultado = self.db_session.execute(text("SELECT @resultado")).scalar()
            print(f"Resultado del SP: {resultado}")  # Debug
            
            # 3. Si fue exitoso, obtener los datos de la solicitud creada
            if resultado.startswith('Solicitud #'):
                id_solicitud = int(resultado.split('#')[1].split()[0])
                print(f"Solicitud creada con ID: {id_solicitud}")  # Debug
                
                solicitud = self.db_session.query(SolicitudHorneado).get(id_solicitud)
                self.db_session.refresh(solicitud)  # Asegurar que tenemos los últimos datos
                
                print(f"Solicitud encontrada en DB: {solicitud is not None}")  # Debug
                if solicitud:
                    print(f"Detalles solicitud - ID: {solicitud.id}, Estado: {solicitud.estado}")  # Debug
                
                if resultado.startswith('Solicitud #'):
                    id_solicitud = int(resultado.split('#')[1].split()[0])
                    
                    # Forzar commit y refrescar
                    self.db_session.commit()
                    solicitud = self.db_session.query(SolicitudHorneado)\
                        .options(joinedload(SolicitudHorneado.receta))\
                        .get(id_solicitud)
                    
                    # Debug: verificar datos exactos
                    print(f"Datos completos solicitud: {solicitud.__dict__}")
                    
                    return {
                        'success': True,
                        'message': resultado,
                        'data': {
                            'id': id_solicitud,
                            'receta': solicitud.receta.nombre,
                            'cantidad_lotes': solicitud.cantidad_lotes,
                            'estado': solicitud.estado,
                            'id_solicitante': solicitud.id_solicitante  # Verificar este valor
                        }
                    }
                
                return {
                    'success': True,
                    'message': resultado,
                    'data': {
                        'id': id_solicitud,
                        'receta': solicitud.receta.nombre if solicitud else 'N/A',
                        'cantidad_lotes': solicitud.cantidad_lotes if solicitud else 0,
                        'estado': solicitud.estado if solicitud else 'N/A'
                    }
                }
            else:
                return {
                    'success': False,
                    'message': resultado,
                    'data': {
                        'requiere_aprobacion': False,
                        'insumos_faltantes': resultado.replace('Error: Insuficientes insumos - ', '')
                    }
                }
                
        except SQLAlchemyError as e:
            self.db_session.rollback()
            error_msg = f"Error al crear solicitud: {str(e)}"
            print(error_msg)  # Debug
            
            return {
                'success': False,
                'message': error_msg,
                'data': {
                    'requiere_aprobacion': False,
                    'error_tecnico': True
                }
                
            }
            
    
    def aprobar_solicitud(self, id_solicitud, id_aprobador):
        """Aprueba una solicitud de horneado"""
        try:
            solicitud = self.db_session.query(SolicitudHorneado).get(id_solicitud)
            
            if not solicitud:
                return {'success': False, 'message': 'Solicitud no encontrada'}
                
            if solicitud.estado != 'Pendiente':
                return {'success': False, 'message': 'La solicitud no está pendiente de aprobación'}
            
            # Verificar nuevamente los insumos (por si cambiaron desde la solicitud)
            insumos_faltantes = self.verificar_insumos(solicitud.id_receta, solicitud.cantidad_lotes)
            
            if insumos_faltantes:
                return {
                    'success': False,
                    'message': 'Ya no hay suficientes insumos para completar la solicitud',
                    'insumos_faltantes': insumos_faltantes
                }
            
            solicitud.estado = 'Aprobada'
            solicitud.id_aprobador = id_aprobador
            solicitud.fecha_aprobacion = datetime.now()
            
            self.db_session.commit()
            
            # Crear notificación para el solicitante
            notificacion = Notificacion(
                tipo_notificacion='Solicitud Produccion',
                mensaje=f'Tu solicitud de horneado para {solicitud.cantidad_lotes} lotes de {solicitud.receta.nombre} ha sido aprobada',
                fecha_creacion=datetime.now(),
                estatus='Nueva',
                id_usuario=solicitud.id_solicitante
            )
            
            self.db_session.add(notificacion)
            self.db_session.commit()
            
            return {'success': True, 'solicitud': solicitud.to_dict()}
            
        except SQLAlchemyError as e:
            self.db_session.rollback()
            print(f"Error al aprobar solicitud: {e}")
            return {'success': False, 'message': 'Error al aprobar la solicitud'}
    
    def rechazar_solicitud(self, id_solicitud, id_aprobador, motivo):
        """Rechaza una solicitud de horneado"""
        try:
            solicitud = self.db_session.query(SolicitudHorneado).get(id_solicitud)
            
            if not solicitud:
                return {'success': False, 'message': 'Solicitud no encontrada'}
                
            if solicitud.estado != 'Pendiente':
                return {'success': False, 'message': 'La solicitud no está pendiente de aprobación'}
            
            solicitud.estado = 'Rechazada'
            solicitud.id_aprobador = id_aprobador
            solicitud.motivo_rechazo = motivo
            solicitud.fecha_aprobacion = datetime.now()
            
            self.db_session.commit()
            
            # Crear notificación para el solicitante
            notificacion = Notificacion(
                tipo_notificacion='Solicitud Produccion',
                mensaje=f'Tu solicitud de horneado para {solicitud.cantidad_lotes} lotes de {solicitud.receta.nombre} ha sido rechazada. Motivo: {motivo}',
                fecha_creacion=datetime.now(),
                estatus='Nueva',
                id_usuario=solicitud.id_solicitante
            )
            
            self.db_session.add(notificacion)
            self.db_session.commit()
            
            return {'success': True, 'solicitud': solicitud.to_dict()}
            
        except SQLAlchemyError as e:
            self.db_session.rollback()
            print(f"Error al rechazar solicitud: {e}")
            return {'success': False, 'message': 'Error al rechazar la solicitud'}
    
    def completar_solicitud(self, id_solicitud, datos_horneado):
        """Completa una solicitud aprobada registrando el horneado a través del procedimiento almacenado"""
        try:
            solicitud = self.db_session.query(SolicitudHorneado).get(id_solicitud)
            
            if not solicitud:
                return {'success': False, 'message': 'Solicitud no encontrada'}
                
            if solicitud.estado != 'Aprobada':
                return {'success': False, 'message': 'La solicitud no está aprobada'}
            
            # Usamos el nuevo servicio de horneado con el stored procedure
            horneado_service = HorneadoService(self.db_session)
            cantidad_producida = solicitud.cantidad_lotes * solicitud.receta.cantGalletasProduction
            
            resultado = horneado_service.registrar_horneado(
                datos_horneado['temperatura'],
                datos_horneado['tiempo'],
                cantidad_producida,
                datos_horneado['observaciones'],
                solicitud.id_receta,
                current_user.idUser
            )
            
            if not resultado:
                return {'success': False, 'message': 'Error al registrar el horneado'}
            
            # Obtener el ID del horneado recién creado
            horneado = self.db_session.query(Horneado)\
                .filter_by(id_receta=solicitud.id_receta)\
                .order_by(Horneado.fecha_horneado.desc())\
                .first()
            
            # Actualizar la solicitud
            solicitud.estado = 'Completada'
            solicitud.id_horneado = horneado.id
            solicitud.fecha_completado = datetime.now()
            
            # Notificar al solicitante
            notificacion = Notificacion(
                tipo_notificacion='Solicitud Produccion',
                mensaje=f'Tu solicitud de horneado para {solicitud.cantidad_lotes} lotes de {solicitud.receta.nombre} ha sido completada',
                fecha_creacion=datetime.now(),
                estatus='Nueva',
                id_usuario=solicitud.id_solicitante
            )
            
            self.db_session.add(notificacion)
            self.db_session.commit()
            
            return {'success': True, 'solicitud': solicitud.to_dict()}
            
        except SQLAlchemyError as e:
            self.db_session.rollback()
            print(f"Error al completar solicitud: {e}")
            return {'success': False, 'message': 'Error al completar la solicitud'}
        
    def get_solicitudes_pendientes(self):
        """Obtiene todas las solicitudes pendientes de aprobación"""
        try:
            return self.db_session.query(SolicitudHorneado)\
                .filter(SolicitudHorneado.estado == 'Pendiente')\
                .order_by(SolicitudHorneado.fecha_solicitud.asc())\
                .all()
        except SQLAlchemyError as e:
            print(f"Error al obtener solicitudes pendientes: {e}")
            return []
    
    def get_solicitudes_usuario(self, id_usuario):
        """Obtiene las solicitudes de un usuario específico"""
        try:
            # Forzar una nueva sesión para evitar problemas de caché
            db.session.expire_all()
            
            # Consulta con join explícito para evitar problemas de carga
            solicitudes = db.session.query(SolicitudHorneado)\
                .options(joinedload(SolicitudHorneado.receta))\
                .filter(SolicitudHorneado.id_solicitante == id_usuario)\
                .order_by(SolicitudHorneado.fecha_solicitud.desc())\
                .all()
            
            # Debug avanzado - ver consulta SQL generada
            from sqlalchemy.dialects import postgresql
            stmt = db.session.query(SolicitudHorneado)\
                .filter(SolicitudHorneado.id_solicitante == id_usuario)\
                .statement
            print("SQL EJECUTADO:", stmt.compile(dialect=postgresql.dialect()))
            
            return solicitudes
        except SQLAlchemyError as e:
            print(f"Error al obtener solicitudes de usuario: {e}")
            return []
    
    def get_solicitud(self, id_solicitud):
        """Obtiene una solicitud por su ID"""
        try:
            return self.db_session.query(SolicitudHorneado).get(id_solicitud)
        except SQLAlchemyError as e:
            print(f"Error al obtener solicitud: {e}")
            return None
    def obtener_solicitudes_para_completar(self, id_usuario):
        """Obtiene las solicitudes aprobadas pendientes de completar por un usuario"""
        try:
            return self.db_session.query(SolicitudHorneado)\
                .filter(
                    and_(
                        SolicitudHorneado.estado == 'Aprobada',
                        SolicitudHorneado.id_solicitante == id_usuario
                    )
                )\
                .order_by(SolicitudHorneado.fecha_aprobacion.asc())\
                .all()
        except SQLAlchemyError as e:
            print(f"Error al obtener solicitudes para completar: {e}")
            return []
    def verificar_insumos(self, id_receta, cantidad_lotes):
        """Verifica si hay suficientes insumos para la receta y cantidad de lotes especificados"""
        try:
            # Obtener los ingredientes necesarios para la receta
            ingredientes = self.db_session.execute(
                text("""
                    SELECT i.idInsumo, i.nombre, ir.cantidad, i.unidadInsumo, i.cantidadDisponible
                    FROM ingredientesReceta ir
                    JOIN insumos i ON ir.idInsumo = i.idInsumo
                    WHERE ir.idReceta = :id_receta
                """),
                {'id_receta': id_receta}
            ).fetchall()

            insumos_faltantes = []
            
            for ingrediente in ingredientes:
                id_insumo, nombre, cantidad_necesaria, unidad, cantidad_disponible = ingrediente
                cantidad_total_necesaria = cantidad_necesaria * cantidad_lotes
                
                if cantidad_disponible < cantidad_total_necesaria:
                    insumos_faltantes.append({
                        'nombre': nombre,
                        'necesario': cantidad_total_necesaria,
                        'disponible': cantidad_disponible,
                        'unidad': unidad
                    })
            
            return insumos_faltantes if insumos_faltantes else None
            
        except SQLAlchemyError as e:
            print(f"Error al verificar insumos: {e}")
            return None