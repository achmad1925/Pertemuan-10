from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.schemas.user_schema import UserRegisterSchema, UserUpdateSchema
from app.repositories.user_repo import user_repo

val_bp = Blueprint('validation_demo', __name__, url_prefix='/api/v1/auth-val')
register_schema = UserRegisterSchema()
update_schema = UserUpdateSchema()

    
@val_bp.route('/register', methods=['POST'])
def register_with_validation():
    # 1. Validasi Header Content-Type & sintaksis JSON secara aman
    if not request.is_json:
        return jsonify({
            "status": "fail",
            "message": "Header Content-Type wajib application/json"
        }), 400

    raw_payload = request.get_json(silent=True)

    if raw_payload is None:
        return jsonify({
            "status": "fail",
            "message": "Sintaksis JSON pada request body rusak atau kosong"
        }), 400

    # 2. Validasi Skema Deklaratif menggunakan Marshmallow
    try:
        validated_data = register_schema.load(raw_payload)
    except ValidationError as err:
        return jsonify({
            "status": "fail",
            "message": "Validasi data input gagal",
            "errors": err.messages
        }), 422

    # 3. Cek duplikasi akun
    if user_repo.find_by_username(validated_data["username"]):
        return jsonify({
            "status": "fail",
            "message": "Registrasi gagal",
            "errors": {"username": ["Username sudah terdaftar"]}
        }), 409

    if user_repo.find_by_email(validated_data["email"]):
        return jsonify({
            "status": "fail",
            "message": "Registrasi gagal",
            "errors": {"email": ["Email sudah terdaftar"]}
        }), 409

    # 4. Simpan user (password hanya disimpan sebagai hash)
    new_user = user_repo.create(**validated_data)

    # Serialisasi kembali menggunakan dump() agar field load_only (password) otomatis tersembunyi
    safe_response_data = register_schema.dump(validated_data)
    safe_response_data["id"] = new_user["id"]

    return jsonify({
        "status": "success",
        "message": "Registrasi berhasil disimpan",
        "data": safe_response_data
    }), 201


@val_bp.route('/register/<int:user_id>', methods=['PUT'])
def update_registered_user(user_id):
    # 1. Cek keberadaan user terlebih dahulu
    existing_user = user_repo.find_by_id(user_id)
    if existing_user is None:
        return jsonify({
            "status": "fail",
            "message": f"User dengan id {user_id} tidak ditemukan"
        }), 404

    # 2. Validasi Header Content-Type & sintaksis JSON secara aman
    if not request.is_json:
        return jsonify({
            "status": "fail",
            "message": "Header Content-Type wajib application/json"
        }), 400

    raw_payload = request.get_json(silent=True)

    if raw_payload is None:
        return jsonify({
            "status": "fail",
            "message": "Sintaksis JSON pada request body rusak atau kosong"
        }), 400

    if not isinstance(raw_payload, dict) or not raw_payload:
        return jsonify({
            "status": "fail",
            "message": "Validasi data input gagal",
            "errors": {"payload": ["Minimal satu field harus dikirim untuk proses update"]}
        }), 422

    # 3. Validasi Skema Parsial menggunakan Marshmallow
    try:
        validated_data = update_schema.load(raw_payload)
    except ValidationError as err:
        return jsonify({
            "status": "fail",
            "message": "Validasi data input gagal",
            "errors": err.messages
        }), 422

    if not validated_data:
        return jsonify({
            "status": "fail",
            "message": "Validasi data input gagal",
            "errors": {"payload": ["Minimal satu field valid harus dikirim untuk proses update"]}
        }), 422

    # 4. Cek duplikasi akun (kecuali milik user itu sendiri)
    if "username" in validated_data:
        duplicated = user_repo.find_by_username_except(validated_data["username"], user_id)
        if duplicated:
            return jsonify({
                "status": "fail",
                "message": "Update gagal",
                "errors": {"username": ["Username sudah terdaftar"]}
            }), 409

    if "email" in validated_data:
        duplicated = user_repo.find_by_email_except(validated_data["email"], user_id)
        if duplicated:
            return jsonify({
                "status": "fail",
                "message": "Update gagal",
                "errors": {"email": ["Email sudah terdaftar"]}
            }), 409

    # 5. Simpan perubahan (password hanya disimpan sebagai hash)
    updated_user = user_repo.update(user_id, validated_data)

    safe_response_data = update_schema.dump(validated_data)
    safe_response_data["id"] = updated_user["id"]
    safe_response_data["username"] = updated_user["username"]
    safe_response_data["email"] = updated_user["email"]

    return jsonify({
        "status": "success",
        "message": "Data user berhasil diperbarui",
        "data": safe_response_data
    }), 200


@val_bp.route('/register/<int:user_id>', methods=['DELETE'])
def delete_registered_user(user_id):
    deleted_user = user_repo.delete(user_id)

    if deleted_user is None:
        return jsonify({
            "status": "fail",
            "message": f"User dengan id {user_id} tidak ditemukan"
        }), 404

    return jsonify({
        "status": "success",
        "message": "User berhasil dihapus",
        "data": deleted_user
    }), 200


@val_bp.route('/trigger-500-demo', methods=['GET'])
def trigger_server_error_demo():
    # Endpoint simulasi bug internal untuk menguji Global Error Handler 500 & Error Logging
    hasil = 100 / 0

    return jsonify({"hasil": hasil}), 200
