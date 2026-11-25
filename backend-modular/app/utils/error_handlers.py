import logging
from flask import jsonify, request
from werkzeug.exceptions import HTTPException

logger = logging.getLogger("backend_error_logger")


def register_error_handlers(app):

    @app.errorhandler(400)
    def bad_request_handler(error):
        return jsonify({
            "status": "fail",
            "code": 400,
            "message": getattr(
                error,
                "description",
                "Permintaan tidak valid atau format JSON rusak"
            )
        }), 400

    @app.errorhandler(404)
    def not_found_handler(error):
        return jsonify({
            "status": "error",
            "code": 404,
            "message": f"Endpoint URI '{request.path}' tidak ditemukan pada server"
        }), 404

    @app.errorhandler(405)
    def method_not_allowed_handler(error):
        return jsonify({
            "status": "error",
            "code": 405,
            "message": f"Metode HTTP '{request.method}' tidak diizinkan untuk endpoint '{request.path}'"
        }), 405

    @app.errorhandler(Exception)
    def unhandled_exception_handler(error):
        # Jika error adalah HTTPException lain (misal 401/403), pertahankan kode statusnya
        if isinstance(error, HTTPException):
            return jsonify({
                "status": "error",
                "code": error.code,
                "message": error.description
            }), error.code

        # Catat stack trace lengkap secara internal untuk keperluan debugging developer
        logger.exception(
            f"Unhandled Server Error pada {request.method} {request.path}: {str(error)}"
        )

        # Kembalikan pesan aman tanpa membocorkan detail internal kepada klien
        return jsonify({
            "status": "error",
            "code": 500,
            "message": "Terjadi kesalahan internal pada server. Silakan hubungi administrator."
        }), 500
