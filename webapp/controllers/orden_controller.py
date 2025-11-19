from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from webapp.models.orden_model import crear_orden, listar_ordenes, obtener_orden, listar_productos, eliminar_orden
from webapp.models.factura_model import obtener_factura_por_orden
import json
import uuid

bp = Blueprint("orden", __name__, url_prefix="/ordenes")

@bp.route("/", methods=["GET"])
def listar_ordenes_view():
    if "user" not in session:
        return redirect(url_for("login.login"))
    ordenes = listar_ordenes()
    # Anotar si existe factura para cada orden (para mostrar estado en la lista)
    annotated = []
    for o in ordenes:
        factura = obtener_factura_por_orden(o['id'])
        o_copy = dict(o)
        o_copy['factura'] = factura
        annotated.append(o_copy)
    return render_template("ordenes.html", ordenes=annotated, productos=None)


@bp.route('/ver/<int:orden_id>', methods=['GET'])
def ver_orden(orden_id):
    """Muestra el detalle de una orden y acciones (generar factura / ver factura)."""
    if "user" not in session:
        return redirect(url_for("login.login"))
    orden = obtener_orden(orden_id)
    if not orden:
        return "Orden no encontrada", 404
    factura = obtener_factura_por_orden(orden_id)
    return render_template('orden_detalle.html', orden=orden, factura=factura)


@bp.route('/eliminar/<int:orden_id>', methods=['POST'])
def eliminar_orden_view(orden_id):
    if "user" not in session:
        return redirect(url_for("login.login"))
    # eliminar orden y datos relacionados
    eliminar_orden(orden_id)
    return redirect(url_for('orden.listar_ordenes_view'))

@bp.route("/nuevo", methods=["GET","POST"])
def nueva_orden():
    if "user" not in session:
        return redirect(url_for("login.login"))
    if request.method == "POST":
        cliente = request.form.get("cliente")
        direccion = request.form.get("direccion")
        telefono = request.form.get("telefono")
        comuna = request.form.get("comuna")
        region = request.form.get("region")

        # Construir lista de productos desde campos qty_<id>
        productos_db = listar_productos()
        productos = []
        total = 0.0
        for p in productos_db:
            pid = p['id']
            qty_field = f"qty_{pid}"
            qty_raw = request.form.get(qty_field)
            try:
                qty = int(qty_raw) if qty_raw else 0
            except Exception:
                qty = 0
            if qty > 0:
                nombre = p.get('nombre')
                precio = float(p.get('precio', 0))
                subtotal = round(precio * qty, 2)
                productos.append({
                    'id': pid,
                    'nombre': nombre,
                    'cantidad': qty,
                    'precio': precio,
                    'subtotal': subtotal
                })
                total += subtotal

        numero_orden = str(uuid.uuid4())[:8]
        crear_orden(numero_orden, cliente, direccion, telefono, comuna, region, productos, total)
        return redirect(url_for("orden.listar_ordenes_view"))

    # GET: mostrar formulario con productos disponibles
    productos = listar_productos()
    # También mostrar las órdenes existentes debajo del formulario (anotadas con factura)
    ordenes_raw = listar_ordenes()
    annotated = []
    for o in ordenes_raw:
        factura = obtener_factura_por_orden(o['id'])
        o_copy = dict(o)
        o_copy['factura'] = factura
        annotated.append(o_copy)
    return render_template("ordenes.html", ordenes=annotated, productos=productos)

# REST API ejemplo
@bp.route("/api/ordenes", methods=["GET"])
def api_listar_ordenes():
    ordenes = listar_ordenes()
    return jsonify(ordenes)
