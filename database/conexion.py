import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv      # ? Libreria para leer el contenido de las variables del archivo '.env'
import os

# * Cargamos las vairbles que estarna en el archiov '.env'
load_dotenv()

# ? Creamos la conexión con la BD
def conectar():
    try:
        conexion = mysql.connector.connect(
            # ? Obtenemos el valor de las variables del archivo '.env'
            host=os.getenv("MI_SERVIDOR"),
            user=os.getenv("USUARIO_MYSQL"),
            password=os.getenv("CONSTRASENA_MYSQL"),
            database=os.getenv("NOMBRE_BD")
        )
        
        if conexion.is_connected():
            print("La conexión con la base de datos ha sido exitosa")
            return conexion
    except Error as e:
        print(f"Error en la conección con MySQL: {e}")
        return None

if __name__ == "__main__":
    conexion = conectar()
    if conexion:
        conexion.close()
        print("🔌 Conexión cerrada")
