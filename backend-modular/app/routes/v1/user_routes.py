from flask import Blueprint, request
from app.repositories.user_repo import user_repo
from app.utils.response_helper import succes_response, fail_response


user_bp_v1 = Blueprint('user_v1', __name__, url_prefix='/api/v1/users')


@user_bp_v1.route('', methods=['GET'])
def get_users():
    users = user_repo.get_all()
    return succes_response(data={"users": users, "total": len(users)})


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
    elif user_repo.find_by_username(username):
        errors["username"] = "Username sudah terdaftar"

    if not isinstance(email, str) or "@" not in email:
        errors["email"] = "Email tidak valid"
    elif user_repo.find_by_email(email):
        errors["email"] = "Email sudah terdaftar"

    password = body.get("password")
    if not isinstance(password, str) or len(password) < 8:
        errors["password"] = "Password minimal 8 karakter"

    if errors:
        return fail_response(errors, 400)

    new_user = user_repo.create(
        username=username.strip(),
        email=email.strip(),
        password=password
    )
    return succes_response(data=new_user, message="User berhasil didaftarkan", code=201)
