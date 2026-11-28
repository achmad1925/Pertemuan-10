import os
import logging
from flask import Flask
from app.config import Config
from app.models.product_model import db, Product
from app.models.category_product_models import Category, ProductItem
from app.routes.product_routes import product_bp
from app.routes.product_db_routes import product_db_bp
from app.routes.advanced_routes import advanced_bp
from app.routes.mongo_log_routes import mongo_bp
from app.routes.validation_routes import val_bp # [BARU Pertemuan 10]
from app.routes.v1.user_routes import user_bp_v1 # [BARU Pertemuan 10]
from app.utils.error_handlers import register_error_handlers # [BARU Pertemuan 10]

def configure_logging():
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler("logs/app_error.log", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

def create_app():
    configure_logging()
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    # Registrasi seluruh Blueprint (Pertemuan 4, 6, 7, 9, dan 10)
    app.register_blueprint(product_bp)
    app.register_blueprint(product_db_bp)
    app.register_blueprint(advanced_bp)
    app.register_blueprint(mongo_bp)
    app.register_blueprint(val_bp)
    app.register_blueprint(user_bp_v1)
    # Aktifkan Global Error Handlers (400, 404, 405, 500) secara terpusat
    register_error_handlers(app)
    with app.app_context():
        db.create_all()
    return app