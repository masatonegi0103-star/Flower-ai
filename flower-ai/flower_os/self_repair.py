"""
System Self-Repair Module
"""

import os
import sys
from flower_os.logger import log, log_error

def repair() -> bool:
    """
    システムの整合性チェックと修復
    
    Returns:
        bool: 修復が成功したかどうか
    """
    try:
        log("自己修復プロセス開始")
        
        # 必要なディレクトリの作成
        required_dirs = [
            "logs",
            "brain",
            "memory",
            "cognition",
            "system",
            "flower_os"
        ]
        
        for dir_name in required_dirs:
            dir_path = os.path.join(os.path.dirname(__file__), "..", dir_name)
            os.makedirs(dir_path, exist_ok=True)
        
        log("自己修復プロセス完了")
        return True
        
    except Exception as e:
        log_error(f"自己修復エラー: {e}")
        return False

def check_dependencies() -> bool:
    """
    依存関係の確認
    
    Returns:
        bool: すべての依存関係が満たされているかどうか
    """
    try:
        import openai
        log("依存関係チェック: OK")
        return True
    except ImportError:
        log_error("必須パッケージが不足しています。 pip install -r requirements.txt を実行してください。")
        return False