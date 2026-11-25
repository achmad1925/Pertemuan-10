from flask import Blueprint, jsonify, request
from app.repositories.product_repo import ProductRepository
from app.services.product_service import ProductService


product_bp = Blueprint('products', __name__, url_prefix='/api/v1/products')
repo = ProductRepository()
service = ProductService(repo)

@product_bp.route('', methods=['GET'])
def list_products():
    return jsonify({"status": "succes", "data": service.fetch_products()}), 200

@product_bp.route('/<int:product_id>', methods=['GET'])
def find_product(product_id):
    resp, code = service.fetch_product_details(product_id)
    return jsonify(resp), code

@product_bp.route('', methods=['POST'])
def create_product():
    data = request.get_json(silent=True)
    respone, status_code = service.add_new_product(data)
    return jsonify(respone), (status_code)