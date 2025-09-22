import json
from pathlib import Path
from collections import OrderedDict

class DatabaseListStorage:
    def __init__(self, databases_list_path):
        self.databases_list_path = Path(databases_list_path)
        self.ensure_file_exists()

    def ensure_file_exists(self):
        # Цей метод перевіряє, чи існує папка та файл для зберігання списку баз.
        # Якщо папка не існує — створює її.
        # Якщо файл не існує — створює порожній файл з вмістом {} (порожній JSON-об'єкт).
        if not self.databases_list_path.parent.exists():
            self.databases_list_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.databases_list_path.exists():
            with self.databases_list_path.open("w", encoding="utf-8") as f:
                f.write("{}")

    def get_db_info(self, db_name: str) -> dict:
        # Повертає словник з інформацією про базу за її ім'ям.
        all_databases = self.load()
        return all_databases.get(db_name, {})

    def get_db_info_by_id(self, db_id: str) -> dict | None:
        if db_id is None:
            return None
        
        all_databases = self.load()
        for db_name, db_info in all_databases.items():
            if db_info.get("id") == db_id:
                db_info_with_name = db_info.copy()
                db_info_with_name["name"] = db_name
                return db_info_with_name
        return None    

    def load(self) -> dict:
        try:
            with self.databases_list_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Помилка завантаження баз: {e}")
            return {}

    def save(self, databases: dict):
        try:
            with self.databases_list_path.open("w", encoding="utf-8") as f:
                json.dump(databases, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Помилка збереження баз: {e}")

    def rename(self, old_name: str, new_name: str):
        databases = self.load()
        if old_name in databases and new_name not in databases:
            keys = list(databases.keys())
            idx = keys.index(old_name)
            value = databases.pop(old_name)
            items = list(databases.items())
            items.insert(idx, (new_name, value))
            databases = OrderedDict(items)
            self.save(databases)
            return True
        return False

    def delete(self, db_name: str):
        databases = self.load()
        if db_name in databases:
            databases.pop(db_name, None)
            self.save(databases)
            return True
        return False

    # def add(self, db_name: str, db_info: dict):
    #     databases = self.load()
    #     databases[db_name] = db_info
    #     self.save(databases)
    #     return True

class LastSelectedDbStorage:
    def __init__(self, last_selected_db_path):
        self.last_selected_db_path = Path(last_selected_db_path)
        self.ensure_file_exists()

    def ensure_file_exists(self):
        if not self.last_selected_db_path.parent.exists():
            self.last_selected_db_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.last_selected_db_path.exists():
            with self.last_selected_db_path.open("w", encoding="utf-8") as f:
                f.write("{}")

    def load(self) -> dict:
        try:
            with self.last_selected_db_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                return {
                    "db_id": data.get("db_id", None),
                    "user": data.get("user", None)
                }
        except Exception as e:
            print(f"Помилка завантаження last_selected_db: {e}")
        return None

    def save(self, db_id: str, db_user: str):
        try:
            with self.last_selected_db_path.open("w", encoding="utf-8") as f:
                json.dump({"db_id": db_id, "user": db_user}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Помилка збереження last_selected_db: {e}")
        return None
