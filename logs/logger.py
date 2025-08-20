
import datetime
import os
from core.i18n.localizer import Localizer

LOG_PATH = "logs/bootstrap.log"
localizer = Localizer()  # або "en", залежно від конфігурації

def log_event(key: str):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = localizer.t(key)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")        