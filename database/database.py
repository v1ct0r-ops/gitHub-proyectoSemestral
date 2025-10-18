import sqlite3
import os
from datetime import datetime


#Es mi ruta a la base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), 'proyecto.db')

def conectar():
    """"Conecta a la base de datos SQLite"""
    try:
        conexion = sqlite3.connect(DB_PATH)
        return conexion
    except Exception as e:
        print(f"Error al conectar a la base de datos {e}")
        return None
    

def crear_tablas():
    """Crea las tablas necesarias en la base de datos si no existen"""
    conexion = conectar()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ordenes_compra (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_orden TEXT UNIQUE NOT NULL,
                cliente TEXT NOT NULL,
                direccion TEXT NOT NULL,
                telefono TEXT NOT NULL,
                comuna TEXT NOT NULL,
                region TEXT NOT NULL,
                productos TEXT NOT NULL,
                precios REAL NOT NULL,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conexion.commit()
        conexion.close()

def cerrar_conexion(conexion):
    """Cierra la conexión a la base de datos"""
    if conexion:
        conexion.close()
        print("Conexión cerrada")
        

def inicializar_base_de_datos():
    """Inicializa la base de datos y crea un usuario admin por defecto"""
    crear_tablas()
    
    # Crear usuario admin por defecto
    conexion = conectar()
    if conexion:
        try:
            cursor = conexion.cursor()
            
            # Verificar si ya existe el usuario admin
            cursor.execute("SELECT * FROM usuarios WHERE username = ?", ('admin',))
            if not cursor.fetchone():
                # Crear usuario admin (contraseña: admin123)
                import hashlib
                password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
                cursor.execute(
                    "INSERT INTO usuarios (username, password_hash) VALUES (?, ?)",
                    ('admin', password_hash)
                )
                conexion.commit()
                print("Usuario admin creado: admin/admin123")
                
        except Exception as e:
            print(f"Error al inicializar BD: {e}")
        finally:
            conexion.close()
    
    print("Base de datos inicializada")

# Código de prueba
if __name__ == "__main__":
    print("Inicializando base de datos...")
    inicializar_base_de_datos()
    print("¡Base de datos lista!")