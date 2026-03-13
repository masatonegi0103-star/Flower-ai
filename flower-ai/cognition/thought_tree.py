"""
Thought Tree Generation Module
"""

from typing import List

def generate_branches(text: str) -> List[str]:
    """
    入力テキストから複数の思考ブランチを生成
    
    Args:
        text: ユーザー入力
        
    Returns:
        思考ブランチのリスト
    """
    try:
        # シンプルな思考ブランチ生成
        branches = [
            f"直接的な回答: {text}に対する一般的な回答を考える",
            f"深掘り: {text}の背景にある理由を考える",
            f"実践的: {text}に対する実用的なアドバイスを考える"
        ]
        return branches
    except:
        return ["テキストを処理できませんでした"]

def choose_best(branches: List[str]) -> str:
    """
    最良の思考ブランチを選択
    
    Args:
        branches: 思考ブランチのリスト
        
    Returns:
        選択された思考
    """
    if not branches:
        return "深く考える必要があります"
    return branches[0]  # シンプルに最初を選択