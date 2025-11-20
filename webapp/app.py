import os
from flask import Flask, redirect, url_for

# Crear la aplicación Flask con estructura de blueprints

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.secret_key = os.environ.get("FLASK_SECRET", "cambia_esto_en_produccion")

    # Inicializar base de datos (si no existe)
    from webapp.models.database import inicializar_base_de_datos
    inicializar_base_de_datos()

    # Registrar blueprints
    from webapp.controllers.login_controller import bp as login_bp
    from webapp.controllers.orden_controller import bp as orden_bp
    from webapp.controllers.factura_controller import bp as factura_bp
    from webapp.controllers.envio_controller import bp as envio_bp

    app.register_blueprint(login_bp)
    app.register_blueprint(orden_bp)
    app.register_blueprint(factura_bp)
    app.register_blueprint(envio_bp)

    @app.route("/")
    def index():
        return redirect(url_for("login.login"))

    # Filtro Jinja para formatear montos en CLP (sin decimales, separador de miles con punto)
    def format_clp(value):
        try:
            n = int(round(float(value)))
        except Exception:
            n = 0
        s = f"{n:,}"  # 1,234,567
        s = s.replace(",", ".")
        return f"${s} "

    app.jinja_env.filters['clp'] = format_clp

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
