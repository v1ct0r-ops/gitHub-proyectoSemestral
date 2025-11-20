from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
import hashlib
from webapp.models.database import get_connection

bp = Blueprint("login", __name__, url_prefix="/login")

@bp.route("/", methods=["GET"])
def login():
    return render_template("login.html")

@bp.route("/", methods=["POST"])
def do_login():
    username = request.form.get("username")
    password = request.form.get("password")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios WHERE username=?", (username,))
    user = cur.fetchone()
    conn.close()
    if user:
        stored = user["password_hash"]
        # Prefer werkzeug check (salted pbkdf2/argon2). If stored hash looks like a raw sha256 hex, fallback to sha256 comparison.
        ok = False
        try:
            ok = check_password_hash(stored, password)
        except Exception:
            ok = False
        if not ok:
            # fallback: check raw SHA-256 hex (legacy)
            try:
                h = hashlib.sha256(password.encode('utf-8')).hexdigest()
                if h == stored:
                    ok = True
            except Exception:
                ok = False

        if ok:
            session["user"] = username
            return redirect(url_for("orden.listar_ordenes_view"))
    flash("Usuario o contraseña incorrectos")
    return redirect(url_for("login.login"))

@bp.route("/logout")
def logout():
    session.pop("user", None)
    flash("Sesión cerrada correctamente")
    return redirect(url_for("login.login"))
