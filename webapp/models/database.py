import sqlite3
import os
from werkzeug.security import generate_password_hash

# Prefer the central project database if present (keeps data from legacy/desktop app)
legacy_db = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'database', 'proyecto.db'))
local_db = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database.db'))

if os.path.exists(legacy_db):
    DB_PATH = legacy_db
else:
    DB_PATH = local_db


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_base_de_datos():
    # Create DB if missing, otherwise run lightweight migrations to ensure expected columns/tables
    need_create = not os.path.exists(DB_PATH)
    conn = get_connection()
    cur = conn.cursor()

    def table_exists(name):
        cur.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name=?""", (name,))
        return cur.fetchone() is not None

    def column_exists(table, column):
        cur.execute(f"PRAGMA table_info({table})")
        cols = [r[1] for r in cur.fetchall()]
        return column in cols

    if need_create:
        # usuarios
        cur.execute("""
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )""")
        # productos
        cur.execute("""
        CREATE TABLE productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL
        )""")
        # ordenes_compra
        cur.execute("""
        CREATE TABLE ordenes_compra (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_orden TEXT UNIQUE NOT NULL,
            cliente TEXT NOT NULL,
            direccion TEXT,
            telefono TEXT,
            comuna TEXT,
            region TEXT,
            productos TEXT,
            total REAL,
            fecha_creacion TEXT
        )""")
        # facturas
        cur.execute("""
        CREATE TABLE facturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_factura TEXT UNIQUE NOT NULL,
            orden_id INTEGER,
            cliente TEXT,
            total REAL,
            iva REAL,
            total_con_iva REAL,
            fecha TEXT,
            estado_despacho TEXT DEFAULT 'pendiente',
            notas_despacho TEXT,
            FOREIGN KEY(orden_id) REFERENCES ordenes_compra(id)
        )""")
        # detalle_facturas
        cur.execute("""
        CREATE TABLE detalle_facturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            factura_id INTEGER,
            producto_id INTEGER,
            producto_nombre TEXT,
            cantidad INTEGER,
            precio_unitario REAL,
            subtotal REAL,
            FOREIGN KEY(factura_id) REFERENCES facturas(id)
        )""")
        # envios
        cur.execute("""
        CREATE TABLE envios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            factura_id INTEGER,
            estado TEXT,
            notas TEXT,
            fecha TEXT,
            FOREIGN KEY(factura_id) REFERENCES facturas(id)
        )""")

        # usuario admin por defecto
        admin_pw = generate_password_hash("admin123")
        cur.execute("INSERT INTO usuarios (username, password_hash) VALUES (?,?)", ("admin", admin_pw))

        # productos de ejemplo
        productos = [
            ("Galón 5kg", 8500),
            ("Galón 11kg", 15000),
            ("Galón 15kg", 22000),
            ("Galón 30kg", 35000),
            ("Galón 45kg", 48000)
        ]
        cur.executemany("INSERT INTO productos (nombre, precio) VALUES (?,?)", productos)
        conn.commit()
    else:
        # Run lightweight migrations for existing DBs (add missing columns/tables)
        # Ensure facturas has iva and total_con_iva, estado_despacho, notas_despacho
        if table_exists('facturas'):
            if not column_exists('facturas', 'iva'):
                cur.execute("ALTER TABLE facturas ADD COLUMN iva REAL DEFAULT 0")
            if not column_exists('facturas', 'total_con_iva'):
                cur.execute("ALTER TABLE facturas ADD COLUMN total_con_iva REAL DEFAULT 0")
            if not column_exists('facturas', 'estado_despacho'):
                cur.execute("ALTER TABLE facturas ADD COLUMN estado_despacho TEXT DEFAULT 'pendiente'")
            if not column_exists('facturas', 'notas_despacho'):
                cur.execute("ALTER TABLE facturas ADD COLUMN notas_despacho TEXT")
            if not column_exists('facturas', 'fecha'):
                cur.execute("ALTER TABLE facturas ADD COLUMN fecha TEXT")
        else:
            # create table if somehow missing
            cur.execute("""
            CREATE TABLE facturas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_factura TEXT UNIQUE NOT NULL,
                orden_id INTEGER,
                cliente TEXT,
                total REAL,
                iva REAL,
                total_con_iva REAL,
                fecha TEXT,
                estado_despacho TEXT DEFAULT 'pendiente',
                notas_despacho TEXT,
                FOREIGN KEY(orden_id) REFERENCES ordenes_compra(id)
            )""")

        # detalle_facturas
        if not table_exists('detalle_facturas'):
            cur.execute("""
            CREATE TABLE detalle_facturas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                factura_id INTEGER,
                producto_id INTEGER,
                producto_nombre TEXT,
                cantidad INTEGER,
                precio_unitario REAL,
                subtotal REAL,
                FOREIGN KEY(factura_id) REFERENCES facturas(id)
            )""")

        # envios
        if not table_exists('envios'):
            cur.execute("""
            CREATE TABLE envios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                factura_id INTEGER,
                estado TEXT,
                notas TEXT,
                fecha TEXT,
                FOREIGN KEY(factura_id) REFERENCES facturas(id)
            )""")

        conn.commit()

    conn.close()
