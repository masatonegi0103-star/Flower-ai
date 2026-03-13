"""
Tool Runner - 作成したツールを実行
"""

import os
from typing import Optional
from flower_os.logger import log, log_error
from config import BASE_DIR

TOOLS_DIR = os.path.join(BASE_DIR, "tools", "created_tools")

def run_tool(tool_name: str, *args, **kwargs) -> Optional[str]:
    """
    ツールを実行
    
    Args:
        tool_name: ツール名
        *args: 位置引数
        **kwargs: キーワード引数
        
    Returns:
        実行結果
    """
    try:
        tool_file = os.path.join(TOOLS_DIR, f"{tool_name}.py")
        
        if not os.path.exists(tool_file):
            log_error(f"ツールが見つかりません: {tool_name}")
            return None
        
        # ツールコードを読み込み
        with open(tool_file, "r", encoding="utf-8") as f:
            code = f.read()
        
        # コードを実行
        namespace = {}
        exec(code, namespace)
        
        if "run" not in namespace:
            log_error(f"ツールに run 関数がありません: {tool_name}")
            return None
        
        run_func = namespace["run"]
        result = run_func(*args, **kwargs)
        
        log(f"ツール実行成功: {tool_name}")
        return str(result)
    
    except Exception as e:
        log_error(f"ツール実行エラー: {e}")
        return None

def list_tools() -> list:
    """作成されたツール一覧を取得"""
    try:
        if not os.path.exists(TOOLS_DIR):
            return []
        
        tools = [f[:-3] for f in os.listdir(TOOLS_DIR) if f.endswith(".py")]
        return tools
    
    except Exception as e:
        log_error(f"ツール一覧取得エラー: {e}")
        return []