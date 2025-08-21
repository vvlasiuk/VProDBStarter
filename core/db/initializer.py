from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from core.db.models import metadata
from config.schema_version import ensure_schema_version
from urllib.parse import quote_plus

def build_uri(cfg, use_master=False):
    user = quote_plus(cfg['user'])
    password = quote_plus(cfg['password'])
    server = cfg['server']
    database = cfg['database'] if not use_master else 'master'
    return f"mssql+pyodbc://{user}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"

def initialize_database(cfg):
    # Для перевірки існування бази та створення — URI до master
    uri_master = build_uri(cfg, use_master=True)
    uri_target = build_uri(cfg)
    if not database_exists(uri_target):
        create_database(uri_target)
    engine = create_engine(uri_target, future=True)
    metadata.create_all(engine)
    ensure_schema_version(engine)
    return engine