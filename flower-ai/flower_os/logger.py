"""
Flower Logger Module
"""

import os
import datetime
from config import LOG_DIR, LOG_FILE

# Create logs directory if it doesn't exist
os.makedirs(LOG_DIR, exist_ok=True)

def log(message: str, level: str = "INFO") -> None:
    """
    ログメッセージを記録する
    
    Args:
        message: ログメッセージ
        level: ログレベル (INFO, ERROR, WARNING)
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] [{level}] {message}"
    
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_message + "\n")
        print(log_message)
    except Exception as e:
        print(f"ログ記録エラー: {e}")

def log_error(message: str) -> None:
    """エラーログを記録"""
    log(message, "ERROR")

def log_warning(message: str) -> None:
    """警告ログを記録"""
    log(message, "WARNING")