from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson import ObjectId
from bson.errors import InvalidId
from app.config import Config
import datetime

mongo_bp = Blueprint('mongo_logs', __name__, url_prefix='/api/v1/logs')
# Inisialisasi koneksi MongoDB dari konfigurasi terpusat
client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
db = client[Config.MONGO_DB_NAME]
log_collection = db['activity_logs']
# 1. READ ALL: Menampilkan maksimal 20 dokumen log terbaru
@mongo_bp.route('', methods=['GET'])
def get_all_logs():
    try:
        logs = list(log_collection.find().sort("timestamp", -1).limit(20))
        for log in logs:
            log['_id'] = str(log['_id']) # Serialisasi BSON ObjectId ke String
        return jsonify({
            "status": "success",
            "total": len(logs),
            "data": logs
            }), 200
    except PyMongoError as e:
        return jsonify({"status": "error", "message": f"Gagal mengakses MongoDB: {str(e)}"}), 500
# 2. READ ONE: Mengambil detail satu dokumen log berdasarkan ObjectId
@mongo_bp.route('/<string:log_id>', methods=['GET'])
def get_log_by_id(log_id):
    try:
        log = log_collection.find_one({"_id": ObjectId(log_id)})
        if not log:
            return jsonify({"status": "fail", "message": "Dokumen log tidak ditemukan"}), 404
        log['_id'] = str(log['_id'])
        return jsonify({"status": "success", "data": log}), 200
    except InvalidId:
        return jsonify({"status": "fail", "message": "Format ObjectId tidak valid (harus 24 karakter hex)"}), 400

# 3. CREATE: Menyimpan dokumen baru dengan struktur embedded metadata dinamis
@mongo_bp.route('', methods=['POST'])
def create_log():
    data = request.get_json() if request.is_json else None
    if not data or not data.get("action") or not data.get("user_id"):
        return jsonify({"status": "fail", "message": "Field 'action' dan 'user_id' wajib diisi"}), 400

    log_document = {
        "user_id": data["user_id"],
        "action": data["action"],
        "metadata": data.get("metadata", {}), # Embedded Document fleksibel
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
    try:
        result = log_collection.insert_one(log_document)
        log_document['_id'] = str(result.inserted_id)
        return jsonify({
            "status": "success",
            "message": "Log aktivitas tersimpan",
            "data": log_document
            }), 201
    except PyMongoError as e:
        return jsonify({"status": "error", "message": f"Gagal menyimpan dokumen: {str(e)}"}), 500

# 4. UPDATE: Memperbarui field tertentu pada dokumen menggunakan operator $set
@mongo_bp.route('/<string:log_id>', methods=['PUT'])
def update_log(log_id):
    data = request.get_json() if request.is_json else None
    if not data:
        return jsonify({"status": "fail", "message": "Request body JSON tidak boleh kosong"}), 400

    update_fields = {}
    if "action" in data:
        update_fields["action"] = data["action"]
    if "metadata" in data:
        update_fields["metadata"] = data["metadata"]
    if not update_fields:
        return jsonify({"status": "fail", "message": "Tidak ada field valid untuk diperbarui"}), 400

    update_fields["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    try:
        res = log_collection.update_one(
        {"_id": ObjectId(log_id)},
        {"$set": update_fields}
    )
        if res.matched_count == 0:
            return jsonify({"status": "fail", "message": "Dokumen log tidak ditemukan"}), 404
            return jsonify({"status": "success", "message": "Dokumen log berhasil diperbarui"}), 200
    except InvalidId:
        return jsonify({"status": "fail", "message": "Format ObjectId tidak valid"}), 400

# 5. DELETE: Menghapus dokumen berdasarkan ObjectId
@mongo_bp.route('/<string:log_id>', methods=['DELETE'])
def delete_log(log_id):
    try:
        res = log_collection.delete_one({"_id": ObjectId(log_id)})
        if res.deleted_count == 0:
            return jsonify({"status": "fail", "message": "Dokumen log tidak ditemukan"}), 404
        return jsonify({"status": "success", "message": "Dokumen log berhasil dihapus"}), 200
    except InvalidId:
        return jsonify({"status": "fail", "message": "Format ObjectId tidak valid"}), 400