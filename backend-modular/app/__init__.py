from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.models.product_model import db, Product
from app.models.category_product_models import Category, ProductItem
from app.routes.product_routes import product_bp
from app.routes.product_db_routes import product_db_bp
from app.routes.advanced_routes import advanced_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)  # Mengizinkan request HTTP lintas-port dari Frontend Live Server

    db.init_app(app)

    app.register_blueprint(product_bp)
    app.register_blueprint(product_db_bp)
    app.register_blueprint(advanced_bp)

    with app.app_context():
        db.create_all()

    return app
