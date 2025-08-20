from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from core.db.models import metadata
from config.schema_version import ensure_schema_version

def build_uri(cfg):
    return f"mssql+pyodbc://{cfg['user']}:{cfg['password']}@{cfg['server']}/{cfg['database']}?driver=ODBC Driver 17 for SQL Server"

def initialize_database(cfg):
    uri = build_uri(cfg)
    if not database_exists(uri):
        create_database(uri)
    engine = create_engine(uri, future=True)
    metadata.create_all(engine)
    ensure_schema_version(engine)
    return engine