from datetime import datetime
from models.database import get_connection


def crear_factura(numero_factura, orden_id, cliente, total, iva, total_con_iva, estado_despacho="pendiente", notas_despacho=None):
    conn = get_connection()
    cur = conn.cursor()
    fecha = datetime.utcnow().isoformat()
    cur.execute("""
        INSERT INTO facturas (numero_factura, orden_id, cliente, total, iva, total_con_iva, fecha, estado_despacho, notas_despacho)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (numero_factura, orden_id, cliente, total, iva, total_con_iva, fecha, estado_despacho, notas_despacho))
    conn.commit()
    fid = cur.lastrowid
    conn.close()
    return fid


def agregar_detalle_factura(factura_id, producto_id, producto_nombre, cantidad, precio_unitario):
    subtotal = cantidad * precio_unitario
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO detalle_facturas (factura_id, producto_id, producto_nombre, cantidad, precio_unitario, subtotal)
        VALUES (?,?,?,?,?,?)
    """, (factura_id, producto_id, producto_nombre, cantidad, precio_unitario, subtotal))
    conn.commit()
    conn.close()


def listar_facturas():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM facturas ORDER BY fecha DESC")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def obtener_detalles(factura_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM detalle_facturas WHERE factura_id=?", (factura_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def obtener_factura(factura_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM facturas WHERE id=?", (factura_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def obtener_factura_por_orden(orden_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM facturas WHERE orden_id=?", (orden_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None
