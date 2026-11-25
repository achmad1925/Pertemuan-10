from flask import Blueprint, request
from app.utils.response_helper import succes_response, fail_response


user_bp_v1 = Blueprint('user_v1', __name__, url_prefix='/api/v1/users')

mock_users = [
    {"id": 1, "username": "admin_bwi", "email": "admin@stikom.ac.id", "role": "admin"}
]

@user_bp_v1.route('', methods=['GET'])
def get_users():
    return succes_response(data={"users": mock_users, "total": len(mock_users)})

@user_bp_v1.route('', methods=['POST'])
def register_user():
    if not request.is_json:
        return fail_response({"content-type": "Header harus application/json"}, 400)

    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return fail_response({"body": "Harus berupa objek JSON yang valid"})
    errors = {}
    username, email = body.get("username"), body.get("email")
    if not isinstance(username, str) or not username.strip():
        errors["username"] = "Username wajib diisi"
    if not isinstance(email, str) or "@" not in email:
        errors["email"] = "Email tidak valid"
    if errors:
        return fail_response(errors, 400)

    new_u = {"id": len(mock_users) + 1, "username": body["username"], "email": body["email"], "role": "user"}
    mock_users.append(new_u)
    return succes_response(data=new_u, message="User berhasil didaftarkan", code=201)