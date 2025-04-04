from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from .models import Galleta, Insumo, Receta, db
from modules.admin.models import Proveedores
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
