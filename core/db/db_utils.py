import pyodbc
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
import socket

def check_odbc_driver():
    """Перевіряє, чи встановлений ODBC Driver 17 for SQL Server."""
    drivers = [d for d in pyodbc.drivers()]
    if "ODBC Driver 17 for SQL Server" not in drivers:
        raise RuntimeError(
            "ODBC Driver 17 for SQL Server не встановлений!\n"
            "Завантажте та встановіть драйвер з:\n"
            "https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server"
        )
    
def is_sql_server_alive(cfg):
    try:
        with socket.create_connection((cfg['server'], cfg['port']), timeout=0.1):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

def build_uri(cfg, use_master=False):
    user     = quote_plus(cfg['user'])
    password = quote_plus(cfg['password'])
    server   = cfg['server']
    database = cfg['database'] if not use_master else 'master'
    port     = cfg['port']

    return (
        f"mssql+pyodbc://{user}:{password}@{server},{port}/{database}"
        "?driver=ODBC+Driver+17+for+SQL+Server"
    )

def check_sql_database_exists(cfg):
    """
    Перевіряє, чи існує база даних у MSSQL.
    Повертає True, якщо існує, інакше False (або якщо сталася помилка підключення).
    """
    if not is_sql_server_alive(cfg):
        return False

    uri_master = build_uri(cfg, use_master=True) 
    engine = create_engine(uri_master, future=True)
    db_name = cfg['database']

    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT db_id(:db_name)"), {"db_name": db_name}
            )
            exists = result.scalar() is not None
        return exists
    except:
        return False