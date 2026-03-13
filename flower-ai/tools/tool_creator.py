"""
Tool Creator - Flowerが自動でツールを作成
"""

import json
import os
from typing import Optional
from flower_os.logger import log, log_error
from config import BASE_DIR

TOOLS_DIR = os.path.join(BASE_DIR, "tools", "created_tools")
TOOLS_METADATA_FILE = os.path.join(TOOLS_DIR, "tools_metadata.json")

os.makedirs(TOOLS_DIR, exist_ok=True)

def create_tool(task: str, ask_llm) -> Optional[str]:
    """
    タスクから新しいツールを自動作成
    
    Args:
        task: ツール説明
        ask_llm: LLM呼び出し関数
        
    Returns:
        作成されたツール名
    """
    try:
        log(f"ツール作成開始: {task}")
        
        prompt = f"""
次のタスクを実行するPythonツールを作成してください。

タスク: {task}

要件:
1. 実行可能なPythonコード
2. run(*args, **kwargs) という関数を必ず定義
3. run関数の戻り値は文字列で結果を返す
4. エラーハンドリングを含める
5. ``` を使わない

出力形式:
最初の行：ツール名
2行目���説明

コード:
def run(*args, **kwargs):
    # 実装
    return "結果"
"""
        
        response = ask_llm(prompt)
        if not response:
            return None
        
        lines = response.strip().split("\n")
        if len(lines) < 3:
            return None
        
        tool_name = lines[0].strip()
        description = lines[1].strip()
        
        code_start = response.find("def run")
        if code_start == -1:
            return None
        
        code = response[code_start:].split("```")[0].strip()
        
        # ツールを保存
        tool_file = os.path.join(TOOLS_DIR, f"{tool_name}.py")
        with open(tool_file, "w", encoding="utf-8") as f:
            f.write(code)
        
        # メタデータを保存
        metadata = {}
        if os.path.exists(TOOLS_METADATA_FILE):
            with open(TOOLS_METADATA_FILE, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        
        metadata[tool_name] = {
            "name": tool_name,
            "description": description,
            "created_at": __import__("datetime").datetime.now().isoformat()
        }
        
        with open(TOOLS_METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        log(f"ツール作成成功: {tool_name}")
        return tool_name
    
    except Exception as e:
        log_error(f"ツール作成エラー: {e}")
        return None