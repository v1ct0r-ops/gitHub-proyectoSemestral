import json
import time
import sqlite3
from datetime import datetime
from webapp.models.database import get_connection
import re


def crear_orden(numero_orden, cliente, direccion, telefono, comuna, region, productos, total):
    conn = get_connection()
    cur = conn.cursor()
    fecha = datetime.utcnow().isoformat()

    # Inspeccionar columnas reales para construir INSERT compatible
    cur.execute("PRAGMA table_info(ordenes_compra)")
    cols = [r[1] for r in cur.fetchall()]

    insert_cols = ['numero_orden', 'cliente', 'direccion', 'telefono', 'comuna', 'region', 'productos']
    values = [numero_orden, cliente, direccion, telefono, comuna, region, json.dumps(productos)]

    # Compatibilidad legacy: si existe 'precios' (NOT NULL en algunas DBs), rellenarlo
    if 'precios' in cols:
        insert_cols.append('precios')
        values.append(total)

    # Columna 'total' (nueva schema)
    if 'total' in cols:
        insert_cols.append('total')
        values.append(total)

    # Fecha creación si existe
    if 'fecha_creacion' in cols:
        insert_cols.append('fecha_creacion')
        values.append(fecha)

    placeholders = ','.join(['?'] * len(insert_cols))
    sql = f"INSERT INTO ordenes_compra ({','.join(insert_cols)}) VALUES ({placeholders})"

    # Reintentos en caso de 'database is locked'
    attempts = 6
    for attempt in range(attempts):
        try:
            cur.execute(sql, tuple(values))
            conn.commit()
            orden_id = cur.lastrowid
            conn.close()
            return orden_id
        except sqlite3.OperationalError as e:
            msg = str(e).lower()
            if 'locked' in msg and attempt < attempts - 1:
                time.sleep(0.5 + attempt * 0.2)
                continue
            conn.close()
            raise
        except sqlite3.IntegrityError:
            # No reintentar sobre errores de integridad; propagar para debugging
            conn.close()
            raise


def listar_ordenes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM ordenes_compra ORDER BY fecha_creacion DESC")
    rows = cur.fetchall()
    conn.close()
    result = []
    for r in rows:
        item = dict(r)
        # Normalize productos field: support JSON (new) and legacy human-readable string
        productos_field = item.get('productos')
        parsed = []
        if productos_field:
            try:
                parsed = json.loads(productos_field)
            except Exception:
                # legacy format example: "Galón 5kg: 10 unidades | Galón 11kg: 2 unidades"
                parts = [p.strip() for p in productos_field.split('|') if p.strip()]
                conn2 = get_connection()
                cur2 = conn2.cursor()
                for p in parts:
                    m = re.match(r"^(.+?):\s*([0-9]+)", p)
                    if m:
                        nombre = m.group(1).strip()
                        cantidad = int(m.group(2))
                        # try to get price from productos table
                        cur2.execute("SELECT id, nombre, precio FROM productos WHERE nombre LIKE ?", (nombre + '%',))
                        prod = cur2.fetchone()
                        precio = float(prod['precio']) if prod else 0.0
                        pid = prod['id'] if prod else None
                        subtotal = round(precio * cantidad, 2)
                        parsed.append({'id': pid, 'nombre': nombre, 'cantidad': cantidad, 'precio': precio, 'subtotal': subtotal})
                conn2.close()
        item['productos'] = parsed
        # normalize total: older DB may use column 'precios'
        if 'total' not in item or item.get('total') is None:
            if 'precios' in item:
                item['total'] = item.get('precios')
        result.append(item)
    return result


def obtener_orden(orden_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM ordenes_compra WHERE id=?", (orden_id,))
    r = cur.fetchone()
    conn.close()
    if not r:
        return None
    item = dict(r)
    # normalize productos as above
    productos_field = item.get('productos')
    parsed = []
    if productos_field:
        try:
            parsed = json.loads(productos_field)
        except Exception:
            parts = [p.strip() for p in productos_field.split('|') if p.strip()]
            conn2 = get_connection()
            cur2 = conn2.cursor()
            for p in parts:
                m = re.match(r"^(.+?):\s*([0-9]+)", p)
                if m:
                    nombre = m.group(1).strip()
                    cantidad = int(m.group(2))
                    cur2.execute("SELECT id, nombre, precio FROM productos WHERE nombre LIKE ?", (nombre + '%',))
                    prod = cur2.fetchone()
                    precio = float(prod['precio']) if prod else 0.0
                    pid = prod['id'] if prod else None
                    subtotal = round(precio * cantidad, 2)
                    parsed.append({'id': pid, 'nombre': nombre, 'cantidad': cantidad, 'precio': precio, 'subtotal': subtotal})
            conn2.close()
    item['productos'] = parsed
    if 'total' not in item or item.get('total') is None:
        if 'precios' in item:
            item['total'] = item.get('precios')
    return item


def listar_productos():
    """Devuelve lista de productos (id, nombre, precio)"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, precio FROM productos ORDER BY nombre")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def eliminar_orden(orden_id):
    """Elimina una orden y datos relacionados (factura, detalle_facturas, envios) si existen."""
    conn = get_connection()
    cur = conn.cursor()
    # eliminar envios relacionados a facturas asociadas
    cur.execute("SELECT id FROM facturas WHERE orden_id=?", (orden_id,))
    filas = cur.fetchall()
    factura_ids = [f['id'] for f in filas]
    for fid in factura_ids:
        cur.execute("DELETE FROM envios WHERE factura_id=?", (fid,))
        cur.execute("DELETE FROM detalle_facturas WHERE factura_id=?", (fid,))
        cur.execute("DELETE FROM facturas WHERE id=?", (fid,))
    # eliminar la orden
    cur.execute("DELETE FROM ordenes_compra WHERE id=?", (orden_id,))
    conn.commit()
    conn.close()
