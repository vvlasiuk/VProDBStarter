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
            "Connection Timeout=1;"
        )
        # Встановлюємо таймаут на рівні рядка підключення та функції
        with pyodbc.connect(conn_str, timeout=1):
            return True
    except Exception:
        return False