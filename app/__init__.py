from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)

    # Importar los modelos
    from .models import Registro, PrecioColor

    # Registrar blueprints
    from .routes import main
    from .felpa_routes import felpa_routes
    from .graficos_routes import graficos_routes

    app.register_blueprint(main)
    app.register_blueprint(felpa_routes)
    app.register_blueprint(graficos_routes, url_prefix='/graficos')

    # Registrar filtro personalizado number_format
    @app.template_filter('number_format')
    def number_format(value, decimals=0):
        try:
            return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except (ValueError, TypeError):
            return value

    return app
