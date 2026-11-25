from flask import Blueprint, jsonify, request
from app.models.product_model import Product, db


product_db_bp = Blueprint(
    "product_db",
    __name__,
    url_prefix="/api/v1/db/products"
)


# 1. READ: Ambil Semua Produk
@product_db_bp.route("", methods=["GET"])
def get_all_products():
    items = Product.query.all()

    return jsonify({
        "status": "success",
        "data": [item.to_dict() for item in items]
    }), 200


# 2. READ BY ID: Ambil Detail Produk
@product_db_bp.route("/<int:product_id>", methods=["GET"])
def get_product_by_id(product_id):
    item = db.session.get(Product, product_id)

    if item is None:
        return jsonify({
            "status": "fail",
            "message": "Produk tidak ditemukan"
        }), 404

    return jsonify({
        "status": "success",
        "data": item.to_dict()
    }), 200


# 3. CREATE: Tambah Produk
@product_db_bp.route("", methods=["POST"])
def create_product():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "status": "fail",
            "message": "Request harus berisi JSON yang valid"
        }), 400

    name = data.get("name")
    price = data.get("price")
    stock = data.get("stock", 0)

    if not isinstance(name, str) or not name.strip():
        return jsonify({
            "status": "fail",
            "message": "Nama produk wajib diisi"
        }), 400

    if price is None or isinstance(price, bool):
        return jsonify({
            "status": "fail",
            "message": "Harga wajib diisi"
        }), 400

    try:
        price = float(price)
        stock = int(stock)

        if price <= 0 or stock < 0:
            raise ValueError
    except (ValueError, TypeError, OverflowError):
        return jsonify({
            "status": "fail",
            "message": "Harga harus lebih dari 0 dan stok tidak boleh negatif"
        }), 400

    new_item = Product(
        name=name.strip(),
        price=price,
        stock=stock
    )

    db.session.add(new_item)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Produk berhasil disimpan ke database",
        "data": new_item.to_dict()
    }), 201


# 4. UPDATE: Perbarui Produk
@product_db_bp.route("/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    item = db.session.get(Product, product_id)

    if item is None:
        return jsonify({
            "status": "fail",
            "message": "Produk tidak ditemukan"
        }), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "status": "fail",
            "message": "Request harus berisi JSON yang valid"
        }), 400

    if "name" in data:
        if not isinstance(data["name"], str) or not data["name"].strip():
            return jsonify({
                "status": "fail",
                "message": "Nama produk tidak boleh kosong"
            }), 400

        item.name = data["name"].strip()

    if "price" in data:
        try:
            if isinstance(data["price"], bool):
                raise ValueError

            price = float(data["price"])

            if price <= 0:
                raise ValueError

            item.price = price
        except (ValueError, TypeError, OverflowError):
            return jsonify({
                "status": "fail",
                "message": "Harga harus berupa angka lebih dari 0"
            }), 400

    if "stock" in data:
        try:
            if isinstance(data["stock"], bool):
                raise ValueError

            stock = int(data["stock"])

            if stock < 0 or float(data["stock"]) != stock:
                raise ValueError

            item.stock = stock
        except (ValueError, TypeError, OverflowError):
            return jsonify({
                "status": "fail",
                "message": "Stok harus berupa bilangan bulat nonnegatif"
            }), 400

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Produk berhasil diperbarui",
        "data": item.to_dict()
    }), 200


# 5. DELETE: Hapus Produk
@product_db_bp.route("/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    item = db.session.get(Product, product_id)

    if item is None:
        return jsonify({
            "status": "fail",
            "message": "Produk tidak ditemukan"
        }), 404

    db.session.delete(item)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Produk berhasil dihapus dari database"
    }), 200