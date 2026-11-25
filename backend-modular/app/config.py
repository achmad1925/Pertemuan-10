import os


class Config:
    # Konfigurasi RDBMS MySQL (Pertemuan 6 & 7)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://root:@localhost/db_backend_stikom'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Konfigurasi NoSQL MongoDB (Pertemuan 9)
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'db_backend_logs')