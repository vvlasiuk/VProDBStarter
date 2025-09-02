#import sys
#import pyodbc
from sqlalchemy import create_engine, text
from sqlalchemy_utils import database_exists, create_database
from core.db.models import metadata
from config.schema_version import ensure_schema_version
from urllib.parse import quote_plus
from core.db.db_utils import check_sql_database_exists, build_uri, check_odbc_driver
from core.secure_config import save_encrypted_value
import secrets
import string

def initialize_database(cfg):
    check_odbc_driver()  # Додаємо перевірку драйвера
    ensure_database_exists(cfg)
    uri_target = build_uri(cfg)
    engine = create_engine(uri_target, future=True)
    metadata.create_all(engine)
    ensure_schema_version(engine)
    return engine

def generate_password(length=16):
    alphabet = string.ascii_letters + string.digits  # Тільки латиниця та цифри
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def ensure_database_exists(cfg):
    uri_master = build_uri(cfg, use_master=True)
    engine = create_engine(uri_master, future=True)
    db_name = cfg['database']

    exists = check_sql_database_exists(cfg)
    if not exists:
        # Відкриваємо окреме з'єднання з AUTOCOMMIT для CREATE DATABASE
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            conn.execute(text(f"CREATE DATABASE [{db_name}]"))
            # --- Створення користувача після створення бази ---
            user_name = f"sa_{db_name}"
            user_password = generate_password(16)
            # Створюємо логін на сервері
            conn.execute(text(f"CREATE LOGIN [{user_name}] WITH PASSWORD = '{user_password}', CHECK_POLICY = OFF;"))
        # Тепер підключаємося до нової бази для створення користувача та призначення ролей
        uri_newdb = build_uri(cfg)
        engine_newdb = create_engine(uri_newdb, future=True)
        with engine_newdb.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            # Створюємо користувача у базі
            conn.execute(text(f"CREATE USER [{user_name}] FOR LOGIN [{user_name}];"))
            # Додаємо до ролі db_owner
            conn.execute(text(f"ALTER ROLE db_owner ADD MEMBER [{user_name}];"))

        save_encrypted_value(db_name, user_name, user_password)
