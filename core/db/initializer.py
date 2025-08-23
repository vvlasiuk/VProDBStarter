import sys
import pyodbc
from sqlalchemy import create_engine, text
from sqlalchemy_utils import database_exists, create_database
from core.db.models import metadata
from config.schema_version import ensure_schema_version
from urllib.parse import quote_plus
from core.db.db_utils import check_sql_database_exists, build_uri

def check_odbc_driver():
    """Перевіряє, чи встановлений ODBC Driver 17 for SQL Server."""
    drivers = [d for d in pyodbc.drivers()]
    if "ODBC Driver 17 for SQL Server" not in drivers:
        raise RuntimeError(
            "ODBC Driver 17 for SQL Server не встановлений!\n"
            "Завантажте та встановіть драйвер з:\n"
            "https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server"
        )

#def build_uri(cfg, use_master=False):
#    user = quote_plus(cfg['user'])
#    password = quote_plus(cfg['password'])
#    # Сервер з інстансом кодуємо повністю!
#    server = cfg['server']
#    database = cfg['database'] if not use_master else 'master'
#    return (
#        f"mssql+pyodbc://{user}:{password}@{server}/{database}"
#        "?driver=ODBC+Driver+17+for+SQL+Server"
#    )

def initialize_database(cfg):
    check_odbc_driver()  # Додаємо перевірку драйвера
    ensure_database_exists(cfg)
    uri_target = build_uri(cfg)
    engine = create_engine(uri_target, future=True)
    metadata.create_all(engine)
    ensure_schema_version(engine)
    return engine

def ensure_database_exists(cfg):
    uri_master = build_uri(cfg, use_master=True)
    engine = create_engine(uri_master, future=True)
    db_name = cfg['database']

#    with engine.connect() as conn: і
#        result = conn.execute(
#            text("SELECT db_id(:db_name)"), {"db_name": db_name}
#        )
#        exists = result.scalar() is not None

    exists = check_sql_database_exists(cfg)
    if not exists:
        # Відкриваємо окреме з'єднання з AUTOCOMMIT для CREATE DATABASE
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            conn.execute(text(f"CREATE DATABASE [{db_name}]"))