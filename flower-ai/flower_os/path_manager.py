"""
Path Management Module
"""

import os
from config import BASE_DIR, BRAIN_PATH, MEMORY_PATH

def get_brain_path() -> str:
    """脳モジュールのパスを取得"""
    return BRAIN_PATH

def get_memory_path() -> str:
    """メモリモジュールのパスを取得"""
    return MEMORY_PATH

def get_base_dir() -> str:
    """プロジェクトのベースディレクトリを取得"""
    return BASE_DIR

def ensure_dir_exists(dir_path: str) -> None:
    """ディレクトリが存在することを確認"""
    os.makedirs(dir_path, exist_ok=True)

# エイリアス（互換性）
brain_path = get_brain_path()
memory_path = get_memory_path()
base_dir = get_base_dir()