import json
from datetime import datetime
from models.database import get_connection
import re


def crear_orden(numero_orden, cliente, direccion, telefono, comuna, region, productos, total):
    conn = get_connection()
    cur = conn.cursor()
    fecha = datetime.utcnow().isoformat()
    cur.execute("""
        INSERT INTO ordenes_compra (numero_orden, cliente, direccion, telefono, comuna, region, productos, total, fecha_creacion)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (numero_orden, cliente, direccion, telefono, comuna, region, json.dumps(productos), total, fecha))
    conn.commit()
    orden_id = cur.lastrowid
    conn.close()
    return orden_id


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
