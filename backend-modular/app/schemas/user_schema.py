from marshmallow import Schema, fields, validate, validates, ValidationError, EXCLUDE

RESERVED_USERNAMES = {"admin", "root", "superuser", "system"}

USERNAME_VALIDATORS = [
    validate.Length(
        min=4,
        max=30,
        error="Username harus antara 4 hingga 30 karakter."
    ),
    validate.Regexp(
        r'^[a-zA-Z0-9_]+$',
        error="Username hanya boleh berisi huruf, angka, dan underscore."
    )
]

PASSWORD_VALIDATOR = validate.Length(
    min=8,
    error="Password minimal harus 8 karakter."
)

AGE_VALIDATOR = validate.Range(
    min=17,
    max=100,
    error="Usia harus berada di rentang 17 hingga 100 tahun."
)

ROLE_VALIDATOR = validate.OneOf(
    ["user", "admin"],
    error="Role hanya diperbolehkan 'user' atau 'admin'."
)


class UserRegisterSchema(Schema):
    class Meta:
        # Mengabaikan field asing yang tidak didefinisikan dalam skema (mencegah Mass Assignment)
        unknown = EXCLUDE

    username = fields.Str(
        required=True,
        validate=USERNAME_VALIDATORS,
        error_messages={"required": "Field username wajib diisi."}
    )

    email = fields.Email(
        required=True,
        error_messages={
            "required": "Field email wajib diisi.",
            "invalid": "Format alamat email tidak valid."
        }
    )

    password = fields.Str(
        required=True,
        load_only=True,  # Tidak pernah dikembalikan saat proses serialisasi (dump)
        validate=PASSWORD_VALIDATOR
    )

    age = fields.Int(
        required=False,
        validate=AGE_VALIDATOR
    )

    role = fields.Str(
        load_default="user",
        validate=ROLE_VALIDATOR
    )

    @validates("username")
    def validate_reserved_username(self, value, **kwargs):
        # Contoh Custom Validator untuk aturan bisnis spesifik
        if value.lower() in RESERVED_USERNAMES:
            raise ValidationError(
                f"Username '{value}' dilindungi sistem dan tidak dapat digunakan."
            )


class UserUpdateSchema(Schema):
    # Skema parsial untuk PUT: seluruh field opsional, minimal satu wajib diisi
    class Meta:
        unknown = EXCLUDE

    username = fields.Str(required=False, validate=USERNAME_VALIDATORS)

    email = fields.Email(
        required=False,
        error_messages={"invalid": "Format alamat email tidak valid."}
    )

    password = fields.Str(
        required=False,
        load_only=True,
        validate=PASSWORD_VALIDATOR
    )

    age = fields.Int(required=False, validate=AGE_VALIDATOR)

    role = fields.Str(required=False, validate=ROLE_VALIDATOR)

    @validates("username")
    def validate_reserved_username(self, value, **kwargs):
        if value.lower() in RESERVED_USERNAMES:
            raise ValidationError(
                f"Username '{value}' dilindungi sistem dan tidak dapat digunakan."
            )
