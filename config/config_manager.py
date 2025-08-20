from cryptography.fernet import Fernet
import json, os

KEY_PATH = "config/db.key"
CONFIG_PATH = "config/db.enc"

def generate_key():
    key = Fernet.generate_key()
    with open(KEY_PATH, "wb") as f:
        f.write(key)

def load_key():
    if not os.path.exists(KEY_PATH):
        generate_key()
    with open(KEY_PATH, "rb") as f:
        return f.read()

def save_config(data):
    fernet = Fernet(load_key())
    encrypted = fernet.encrypt(json.dumps(data).encode())
    with open(CONFIG_PATH, "wb") as f:
        f.write(encrypted)

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return None
    fernet = Fernet(load_key())
    with open(CONFIG_PATH, "rb") as f:
        decrypted = fernet.decrypt(f.read())
    return json.loads(decrypted.decode())