import json
from pathlib import Path
from cryptography.fernet import Fernet
from core.config_paths import CONFIG_DIR

KEY = b'HvoeLHA3mgGxpyrrEl0w36H38P2ihb8XBENTJr-eNAM='

def save_encrypted_value(db_name: str, db_user: str, db_pass: str) -> str:

    fernet = Fernet(KEY)

    data = {"pass": db_pass, "user": db_user}
    json_data = json.dumps(data).encode()

    # 🔒 Шифрування
    encrypted = fernet.encrypt(json_data)

    enc_path = CONFIG_DIR / "enc" / f"{db_name}.enc"

    try:
 # 💾 Збереження у файл
        with open(enc_path, "wb") as f:
            f.write(encrypted)
    except Exception as e:
        print(f"Помилка шифрування пароля: {e}")
        return ""

def load_password_for_db(db_name: str) -> str:
    """
    Завантажує та розшифровує пароль для бази за її id.
    """
    # Формуємо шлях до файлу з паролем
    enc_path = CONFIG_DIR / "enc" / f"{db_name}.enc"
    if not enc_path.exists():
        return {}
    fernet = Fernet(KEY)
    with open(enc_path, "rb") as f:
        encrypted = f.read()
    try:
        decrypted = fernet.decrypt(encrypted)
        return json.loads(decrypted)
    except Exception as e:
        print(f"Помилка розшифрування пароля: {e}")
        return {}