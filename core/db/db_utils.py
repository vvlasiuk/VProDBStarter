import pyodbc

def check_sql_database_exists(server: str, database: str, user: str, password: str) -> bool:
    """
    Перевіряє наявність підключення до SQL Server.
    Повертає True, якщо підключення вдалося, інакше False.
    """
    try:
        conn_str = (
            f"DRIVER={{SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={user};"
            f"PWD={password};"
            "Trust_Connection=no;"
        )
        with pyodbc.connect(conn_str, timeout=0.1):
            return True
    except Exception:
        return False