# Sistema de Gestión de Órdenes de Compra (Web)

Descripción
-----------
Proyecto Flask para gestionar órdenes de compra y facturación para una pequeña distribuidora de gas licuado. Incluye:

- Autenticación de usuarios.
- Gestión de catálogo de productos.
- Creación y listado de órdenes de compra.
- Generación de facturas y registro de envíos.
- Compatibilidad con una base de datos SQLite legacy (migraciones ligeras incluidas).

Este README cubre instalación local, ejecución, despliegue en Render, y notas de compatibilidad con bases legacy.

Estructura principal
-------------------
Directorio relevante del proyecto:

```
gitHub-proyectoSemestral/
├── webapp/                     # Código principal de la aplicación (Flask)
│   ├── app.py                  # Factory de Flask
│   ├── wsgi.py                 # Entrypoint WSGI (gunicorn)
│   ├── models/                 # Lógica de acceso a datos y migraciones ligeras
│   ├── controllers/            # Rutas / controllers
│   └── templates/              # Plantillas Jinja2
├── database/                   # (opcional) base legacy `proyecto.db`
├── requirements.txt            # archivo root que referencia webapp/requirements.txt
├── webapp/requirements.txt     # dependencias del proyecto
├── Procfile                    # comando de arranque para PaaS (gunicorn)
└── README.md
```

Requisitos
----------
- Python 3.11+ (recomendado)
- pip
- Git

Instalación y ejecución local
-----------------------------
1. Clonar el repositorio:

```bash
git clone https://github.com/v1ct0r-ops/gitHub-proyectoSemestral.git
cd gitHub-proyectoSemestral
```

2. Crear y activar un entorno virtual (opcional pero recomendado):

Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Ejecutar la aplicación en modo desarrollo:

```bash
# Opción 1 — modo Flask builtin (útil para debugging)
python -m webapp.app

# Opción 2 — servidor WSGI (equivalente al despliegue)
gunicorn webapp.wsgi:app --bind 0.0.0.0:8000
```

5. Abrir en el navegador: http://127.0.0.1:5000 (si usas `python -m webapp.app`) o el puerto configurado para gunicorn.

Credenciales por defecto
-----------------------
- Usuario: `admin`
- Contraseña: `admin123`

Notas sobre la base de datos
---------------------------
- La aplicación usa SQLite por defecto. El módulo `webapp/models/database.py` selecciona el archivo de DB así:
	- Si existe `database/proyecto.db` (legacy), se usa esa ruta.
	- En caso contrario usa `webapp/database.db` (DB local para la webapp).
- El código incluye migraciones ligeras que:
	- Añaden columnas faltantes (por ejemplo `total`, `fecha_creacion`, columnas en `facturas`).
	- Crean tablas faltantes (`detalle_facturas`, `envios`).
- Compatibilidad legacy:
	- El modelo `orden_model` normaliza el campo `productos` (JSON o formato legacy de texto) y soporta la columna legacy `precios` rellenándola si es requerida por el esquema antiguo.

Limitaciones de SQLite en producción
-----------------------------------
- SQLite no es ideal en PaaS (instancias pueden ser efímeras y la concurrencia es limitada). En particular puedes encontrar:
	- `sqlite3.OperationalError: database is locked` cuando hay concurrencia.
	- Pérdida de datos si la instancia se reinicia y solo se usa el archivo local.

Recomendación: para producción usar Postgres gestionado. Ver "Migración a Postgres" abajo.

Despliegue en Render (Guía rápida)
---------------------------------
- Root Directory: `.` (raíz del repo). Si prefieres mover `Procfile` y `requirements.txt` dentro de `webapp/`, cambia Root a `webapp`.
- Build Command:
	```bash
	pip install -r requirements.txt
	```
- Start Command:
	```bash
	gunicorn webapp.wsgi:app --bind 0.0.0.0:$PORT
	```
- Procfile (ya incluido):
	```text
	web: gunicorn webapp.wsgi:app --bind 0.0.0.0:$PORT -w 1
	```
	Nota: el repo incluye una variante que fuerza un worker (`-w 1`) para mitigar locks en SQLite. Para producción con Postgres puedes usar más workers.
- Variables de entorno recomendadas en Render:
	- `FLASK_SECRET` (cadena larga para seguridad)
	- `DATABASE_URL` (si vas a usar Postgres)

Migración a Postgres (opcional, recomendado)
-----------------------------------------
Pasos básicos:

1. Crear un servicio Postgres en Render (o en otro proveedor) y obtener la URL `DATABASE_URL`.
2. Añadir `psycopg2-binary` a `webapp/requirements.txt` y a tu `requirements.txt` raíz si aplica.
3. Actualizar `webapp/models/database.py` para detectar `DATABASE_URL` y usar `psycopg2` en vez de sqlite3 (o usar SQLAlchemy para mayor flexibilidad).
4. Exportar/convertir datos desde SQLite a Postgres si necesitas conservar los datos existentes (puedo ayudarte con un script de export / import).

Pruebas y CI
------------
- Se incluyen tests básicos en `webapp/tests/` ejecutables con `pytest`.
- En CI (GitHub Actions) la implementación exporta el repo al `PYTHONPATH` o ejecuta `pip install -r webapp/requirements.txt` para que las pruebas importen el paquete `webapp` correctamente.

Resolución de errores comunes
-----------------------------
- `ModuleNotFoundError: No module named 'webapp'`:
	- En Render asegúrate de que `Root Directory` esté en la carpeta correcta (`.` si el paquete `webapp/` queda en la raíz).
	- Alternativa: en el Start Command, ejecuta `PYTHONPATH=/opt/render/project/src:$PYTHONPATH gunicorn webapp.wsgi:app ...` (no recomendado si puedes ajustar root).
- `sqlite3.OperationalError: table ordenes_compra has no column named total`:
	- Solución: el módulo `database.py` incluye migraciones ligeras; redeploy para que apliquen. Si la DB es legacy quizá necesites ejecutar `inicializar_base_de_datos()` una vez.
- `NOT NULL constraint failed: ordenes_compra.precios`:
	- Causado por esquemas legacy que tienen la columna `precios` NOT NULL. El código ahora detecta y rellena `precios` con el `total` al insertar.
- `database is locked`:
	- Mitigaciones incluidas: activación de WAL y incremento de timeout en SQLite; además el Procfile por defecto usa `-w 1` para gunicorn.
	- Solución definitiva: migrar a Postgres.

Desarrollo y flujo de trabajo
----------------------------
- Ramas principales: `main` (producción), `dev` (integración), `feature/*` (funcionalidades).
- Comandos útiles:
	- Ejecutar tests: `pytest -q webapp/tests`
	- Formatear/lintear: usar `black` / `flake8` si lo deseas.
	- Crear commit y push:
		```bash
		git add .
		git commit -m "Descripción del cambio"
		git push origin dev
		```

Archivos clave
-------------
- `webapp/app.py`: factory de Flask y registro de blueprints.
- `webapp/wsgi.py`: entrypoint WSGI (usado por gunicorn).
- `webapp/models/database.py`: conexión a DB y migraciones ligeras.
- `webapp/models/orden_model.py`: lógica de órdenes y compatibilidad legacy.
- `webapp/controllers/*`: controladores/blueprints para rutas.

Contribuciones
--------------
Si quieres contribuir:

1. Crea una rama `feature/descripcion`
2. Realiza cambios y pruebas locales
3. Abre un pull request contra `dev`

Contacto
-------
Para dudas o para que te ayude a migrar a Postgres, envíame los logs o permisos de despliegue y lo hacemos juntos.

Licencia
-------
Este repositorio no incluye una licencia explícita. Si necesitas una, puedo añadir una (MIT/Apache2/GPL).
