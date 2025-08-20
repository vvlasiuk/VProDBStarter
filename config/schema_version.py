from sqlalchemy import Table, Column, Integer, String, MetaData

def ensure_schema_version(engine):
    metadata = MetaData()
    schema_table = Table("DbSchemaVersion", metadata,
        Column("VersionID", Integer, primary_key=True),
        Column("VersionName", String(50))
    )
    metadata.create_all(engine)
    with engine.connect() as conn:
        result = conn.execute(schema_table.select())
        if not result.first():
            conn.execute(schema_table.insert().values(VersionID=1, VersionName="v1.0"))