from flask import Blueprint, render_template, request, redirect, url_for, session
from utils.iva import calcular_iva
from models.factura_model import crear_factura, agregar_detalle_factura, obtener_factura, obtener_detalles, obtener_factura_por_orden
from models.orden_model import obtener_orden
import uuid

from models.envio_model import listar_envios_por_factura

bp = Blueprint("factura", __name__, url_prefix="/factura")

@bp.route("/crear/<int:orden_id>", methods=["GET"])
def crear_factura_view(orden_id):
    """Crea la factura a partir de una orden y redirige al detalle de la factura."""
    if "user" not in session:
        return redirect(url_for("login.login"))
    orden = obtener_orden(orden_id)
    if not orden:
        return "Orden no encontrada", 404
    total = orden.get("total") or 0
    iva, total_con_iva = calcular_iva(total)
    # Si ya existe una factura para esta orden, redirigir al detalle existente
    existente = obtener_factura_por_orden(orden_id)
    if existente:
        return redirect(url_for('factura.detalle_factura', factura_id=existente['id']))

    numero_factura = str(uuid.uuid4())[:10]
    fid = crear_factura(numero_factura, orden_id, orden["cliente"], total, iva, total_con_iva)
    for p in orden["productos"]:
        agregar_detalle_factura(fid, p.get("id"), p.get("nombre"), int(p.get("cantidad",1)), float(p.get("precio",0)))
    # redirigir a la vista detalle de factura
    return redirect(url_for('factura.detalle_factura', factura_id=fid))


@bp.route('/detalle/<int:factura_id>', methods=['GET'])
def detalle_factura(factura_id):
    if "user" not in session:
        return redirect(url_for("login.login"))
    factura = obtener_factura(factura_id)
    if not factura:
        return "Factura no encontrada", 404
    detalles = obtener_detalles(factura_id)
    historial = listar_envios_por_factura(factura_id)
    return render_template('factura.html', factura=factura, detalles=detalles, historial=historial)
