from werkzeug.security import generate_password_hash


class UserRepository:
    def __init__(self):
        self._users = [
            {
                "id": 1,
                "username": "admin_bwi",
                "email": "admin@stikom.ac.id",
                "password_hash": generate_password_hash("Admin123"),
                "age": None,
                "role": "admin"
            }
        ]

    def get_all(self):
        return [self._to_public(user) for user in self._users]

    def find_by_username(self, username):
        return next(
            (u for u in self._users if u["username"].lower() == username.lower()),
            None
        )

    def find_by_email(self, email):
        return next(
            (u for u in self._users if u["email"].lower() == email.lower()),
            None
        )

    def find_by_id(self, user_id):
        return next((u for u in self._users if u["id"] == user_id), None)

    def find_by_email_except(self, email, user_id):
        return next(
            (
                u for u in self._users
                if u["email"].lower() == email.lower() and u["id"] != user_id
            ),
            None
        )

    def find_by_username_except(self, username, user_id):
        return next(
            (
                u for u in self._users
                if u["username"].lower() == username.lower() and u["id"] != user_id
            ),
            None
        )

    def update(self, user_id, fields):
        user = self.find_by_id(user_id)
        if user is None:
            return None

        if fields.get("password"):
            user["password_hash"] = generate_password_hash(fields.pop("password"))

        user.update(fields)
        return self._to_public(user)

    def delete(self, user_id):
        user = self.find_by_id(user_id)
        if user is None:
            return None

        self._users.remove(user)
        return self._to_public(user)

    def create(self, username, email, password, age=None, role="user"):
        user = {
            "id": self._users[-1]["id"] + 1 if self._users else 1,
            "username": username,
            "email": email,
            "password_hash": generate_password_hash(password),
            "age": age,
            "role": role
        }
        self._users.append(user)
        return self._to_public(user)

    @staticmethod
    def _to_public(user):
        return {key: value for key, value in user.items() if key != "password_hash"}


user_repo = UserRepository()
