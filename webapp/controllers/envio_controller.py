from flask import Blueprint, render_template, request, redirect, url_for, session
from models.envio_model import registrar_envio, listar_envios_por_factura

bp = Blueprint("envio", __name__, url_prefix="/envio")

@bp.route("/marcar/<int:factura_id>", methods=["GET","POST"])
def marcar_envio(factura_id):
    if "user" not in session:
        return redirect(url_for("login.login"))
    if request.method == "POST":
        estado = request.form.get("estado")
        notas = request.form.get("notas")
        registrar_envio(factura_id, estado, notas)
        # volver a la vista detalle de la factura
        return redirect(url_for("factura.detalle_factura", factura_id=factura_id))
    historial = listar_envios_por_factura(factura_id)
    return render_template("envio.html", factura_id=factura_id, historial=historial)
