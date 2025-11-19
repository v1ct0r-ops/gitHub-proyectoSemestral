from webapp.app import create_app

# WSGI entrypoint for gunicorn
app = create_app()
