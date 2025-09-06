from sqlalchemy import create_engine, insert
from core.db.models import metadata, Users

def seed_users_table(engine):
    with engine.connect() as conn:
        result = conn.execute(Users.select())
        if result.first() is None:
            conn.execute(
                insert(Users),
                [
                    {"Username": "Адміністратор", "PasswordHash": "", "Email": "", "IsActive": True},
                    {"Username": "Тест", "PasswordHash": "", "Email": "", "IsActive": True}
                ]
            )
            conn.commit()

def initialize_database(uri):
    engine = create_engine(uri, future=True)
    metadata.create_all(engine)
    seed_users_table(engine)