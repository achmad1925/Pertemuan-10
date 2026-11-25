from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from app.models.category_product_models import db, Category, ProductItem

advanced_bp = Blueprint('advanced_api', __name__, url_prefix='/api/v1/advanced/products')

# 1. READ: Paginasi dan Pencarian Dinamis (Filtering)
@advanced_bp.route('', methods=['GET'])
def get_paginated_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    search = request.args.get('search', '', type=str)
        
    query = ProductItem.query
    if search:
        query = query.filter(ProductItem.name.ilike(f"%{search}%"))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "status": "success",
        "data": [item.to_dict() for item in pagination.items],
        "pagination": {
            "current_page": pagination.page,
            "per_page": pagination.per_page,
            "total_pages": pagination.pages,
            "total_items": pagination.total
        }
    }), 200
    
# 2. UPDATE: Perbarui Produk (Nama, Harga, Kategori)
@advanced_bp.route('/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    item = db.session.get(ProductItem, product_id)
    if item is None:
        return jsonify({"status": "fail", "message": "Produk tidak ditemukan"}), 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"status": "fail", "message": "Request harus berisi JSON yang valid"}), 400

    if "product_name" in data:
        if not isinstance(data["product_name"], str) or not data["product_name"].strip():
            return jsonify({"status": "fail", "message": "Nama produk tidak boleh kosong"}), 400
        item.name = data["product_name"].strip()

    if "price" in data:
        try:
            if isinstance(data["price"], bool):
                raise ValueError
            price = float(data["price"])
            if price <= 0:
                raise ValueError
            item.price = price
        except (ValueError, TypeError, OverflowError):
            return jsonify({"status": "fail", "message": "Harga harus berupa angka lebih dari 0"}), 400

    if "category_name" in data:
        if not isinstance(data["category_name"], str) or not data["category_name"].strip():
            return jsonify({"status": "fail", "message": "Nama kategori tidak boleh kosong"}), 400
        cat = Category.query.filter_by(name=data["category_name"].strip()).first()
        if not cat:
            cat = Category(name=data["category_name"].strip())
            db.session.add(cat)
            db.session.flush()
        item.category_id = cat.id

    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Gagal memperbarui: {str(e)}"}), 500

    return jsonify({
        "status": "success",
        "message": "Produk berhasil diperbarui",
        "data": item.to_dict()
    }), 200

# 3. DELETE: Hapus Produk Berdasarkan ID
@advanced_bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    item = db.session.get(ProductItem, product_id)
    if item is None:
        return jsonify({"status": "fail", "message": "Produk tidak ditemukan"}), 404

    try:
        db.session.delete(item)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Gagal menghapus: {str(e)}"}), 500

    return jsonify({
        "status": "success",
        "message": "Produk berhasil dihapus"
    }), 200

# 4. CREATE: Transaksi Atomik Multi-Tabel (Kategori + Produk)
@advanced_bp.route('/transaction-demo', methods=['POST'])
def create_product_with_category_transaction():
    data = request.get_json() if request.is_json else None
    if not data or not data.get("category_name") or not data.get("product_name") or data.get("price") is None:
        return jsonify({"status": "fail", "message": "category_name, product_name, dan price wajib diisi"}), 400
    
    try:
        cat = Category.query.filter_by(name=data["category_name"]).first()
        if not cat:
            cat = Category(name=data["category_name"])
            db.session.add(cat)
            db.session.flush() # Memperoleh cat.id sebelum commit akhir
        prod = ProductItem(
            name=data["product_name"],
            price=float(data["price"]),
            category_id=cat.id
            )
        db.session.add(prod)
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "Transaksi berhasil disimpan",
            "data": prod.to_dict()
            }), 201
    except (SQLAlchemyError, ValueError, TypeError) as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Transaksi dibatalkan: {str(e)}"}), 500