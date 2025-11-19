from datetime import datetime
from models.database import get_connection


def registrar_envio(factura_id, estado, notas=None):
    conn = get_connection()
    cur = conn.cursor()
    fecha = datetime.utcnow().isoformat()
    cur.execute("INSERT INTO envios (factura_id, estado, notas, fecha) VALUES (?,?,?,?)", (factura_id, estado, notas, fecha))
    cur.execute("UPDATE facturas SET estado_despacho=?, notas_despacho=? WHERE id=?", (estado, notas, factura_id))
    conn.commit()
    conn.close()


def listar_envios_por_factura(factura_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM envios WHERE factura_id=? ORDER BY fecha DESC", (factura_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]
