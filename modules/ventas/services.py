from datetime import datetime
from flask_login import current_user
from sqlalchemy import text
from modules.admin.models import Notificacion
from modules.client.models import Pedido
from modules.production.models import Horneado, Receta, SolicitudHorneado
from modules.production.services import BaseService, HorneadoService
from modules.ventas.models import Venta
from database.conexion import db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

def obtener_historial_ventas():
    ventas = Venta.query.join(Venta.usuario).all()

    resultado = []
    for venta in ventas:
        cantidad = sum(det.cantGalletasVendidas for det in venta.detalles) if venta.detalles else 0

        resultado.append({
            "id": venta.idVenta,
            "responsable": venta.usuario.username,
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
            "cliente": pedido.cliente.username,
            "fecha_pedido": pedido.fechaPedido.strftime('%d/%m/%y'),
            "estado": pedido.estadoPedido,
            "total": float(pedido.costoPedido)
        })

    return resultado


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
    
    # Calcular el costo de la galleta:
    def calcular_costo_galleta(self, id_receta):
        """Calcula el costo de producción por galleta y por lote"""
        try:
            # Llamar al procedimiento almacenado
            self.db_session.execute(
                text("CALL sp_CalcularCostoGalleta(:id_receta, @costo_unitario, @costo_lote)"),
                {'id_receta': id_receta}
            )
            
            # Obtener los resultados
            result = self.db_session.execute(
                text("SELECT @costo_unitario, @costo_lote")
            ).fetchone()
            
            return {
                'costo_unitario': float(result[0]) if result[0] else 0,
                'costo_lote': float(result[1]) if result[1] else 0
            }
        except SQLAlchemyError as e:
            print(f"Error al calcular costo: {e}")
            return None
        

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
                tipo='Solicitud Produccion',
                mensaje=f'Tu solicitud de horneado para {solicitud.cantidad_lotes} lotes de {solicitud.receta.nombre} ha sido aprobada',
                fecha_creacion=datetime.now(),
                estado='Nueva',
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
                tipo='Solicitud Produccion',
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
                tipo='Solicitud Produccion',
                mensaje=f'Tu solicitud de horneado para {solicitud.cantidad_lotes} lotes de {solicitud.receta.nombre} ha sido completada',
                fecha_creacion=datetime.now(),
                estado='Nueva',
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
        
    def obtener_solicitudes_para_completar(self, id_usuario=None):
        """Obtiene las solicitudes aprobadas pendientes de completar"""
        try:
            query = self.db_session.query(SolicitudHorneado)\
                .filter(SolicitudHorneado.estado == 'Aprobada')\
                .order_by(SolicitudHorneado.fecha_aprobacion.asc())
            
            if id_usuario:
                query = query.filter(SolicitudHorneado.id_solicitante == id_usuario)
            
            return query.all()
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