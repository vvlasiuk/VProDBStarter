from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from core.db.db_utils import build_uri

def test_connection(cfg):
    try:
        engine = create_engine(build_uri(cfg), future=True)
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except OperationalError:
        return False