"""
LLM Core Module - with Debug Commands
"""

import os
import shutil
import subprocess
from typing import Optional, List, Dict
from openai import OpenAI
from flower_os.logger import log, log_error
from config import MODEL, BRAIN_PATH
from memory.memory_core import store_memory
from brain.emotion_core import update_emotion, get_emotion_state
from brain.personality_core import get_personality
from brain.motivation_core import get_motivation
from brain.goal_core import get_current_goal, evolve_goal
from cognition.thought_tree import generate_branches, choose_best
from cognition.meta_cognition import evaluate_thought, improve_thought
from cognition.self_awareness import generate_self_awareness
from system.pc_controller import open_browser, open_notepad, search_web

# スキルシステムのインポート
from skills.skill_builder import build_skill
from skills.skill_registry import get_registry
from skills.skill_executor import execute_skill, execute_skill_by_keyword
from skills.skill_manager import get_skill_manager
from tools.tool_creator import create_tool
from tools.tool_runner import run_tool, list_tools

# OpenAI クライアント初期化
try:
    client = OpenAI()
except Exception as e:
    log_error(f"OpenAI クライアント初期化エラー: {e}")
    client = None


def ask_llm(prompt: str) -> Optional[str]:
    """LLMに質問する"""
    if not client:
        log_error("OpenAI クライアントが初期化されていません")
        return None
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "あなたはFlowerというAIです。親切で自然な回答を心がけてください。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        log_error(f"LLM呼び出しエラー: {e}")
        return None


# ==========================================
# デバッグコマンド
# ==========================================

def run_debug_action(text: str) -> Optional[str]:
    """デバッグコマンドを実行"""
    try:
        if "デバッグ情報" in text or "debug" in text.lower():
            manager = get_skill_manager()
            return manager.get_debug_info()
        
        if "スキルデバッグ" in text:
            manager = get_skill_manager()
            return f"""
【スキルデバッグ情報】
読み込み済みスキル: {len(manager.skills)}
スキル一覧: {list(manager.skills.keys())}
メタデータファイル: {manager.skills if hasattr(manager, 'skills') else 'N/A'}
"""
        
        return None
    
    except Exception as e:
        log_error(f"デバッグコマンドエラー: {e}")
        return None


# ==========================================
# スキル関連コマンド
# ==========================================

def run_skill_action(text: str) -> Optional[str]:
    """スキル関連のコマンドを実行"""
    try:
        # スキルを習得
        if "スキル習得" in text or "能力習得" in text:
            task = text.replace("スキル習得", "").replace("能力習得", "").strip()
            if not task:
                return """
スキル習得の使い方：

例1：スキル習得 テキストの長さを数える
例2：スキル習得 2つの数を足す
例3：スキル習得 リストから偶数を選ぶ

シンプルで具体的なタスク説明がおすすめです。
"""
            
            log(f"スキル習得要求: {task}")
            skill_name = build_skill(task, ask_llm)
            
            if skill_name:
                return f"""
✅ スキル習得成功: {skill_name}

使い方：
スキル実行 {skill_name} <入力>

例：スキル実行 {skill_name} こんにちは
"""
            else:
                return """
❌ スキル習得に失敗しました

原因を確認するには：
「デバッグ情報」と入力して詳細を確認
ログファイル (logs/flower.log) を確認

より単純なタスク説明を試してください：
❌ 複雑な自然言語処理機能
✅ テキストの長さを数える
"""
        
        # スキルを実行
        if "スキル実行" in text:
            parts = text.replace("スキル実行", "").strip().split(maxsplit=1)
            if not parts:
                return "使い方：スキル実行 <スキル名> <入力>"
            
            skill_name = parts[0]
            args = (parts[1],) if len(parts) > 1 else ()
            
            log(f"スキル実行: {skill_name}, args: {args}")
            result = execute_skill(skill_name, *args)
            
            if result:
                return f"✅ {result}"
            else:
                return f"�� スキル実行失敗: {skill_name}\n「スキル一覧」で確認してください"
        
        # スキル一覧を表示
        if "スキル一覧" in text or "習得スキル一覧" in text:
            manager = get_skill_manager()
            return manager.get_skill_summary()
        
        return None
    
    except Exception as e:
        log_error(f"スキルアクション実行エラー: {e}")
        import traceback
        log_error(traceback.format_exc())
        return f"エラー: {e}"
    
    
# ==========================================
# ツール関連コマンド
# ==========================================

def run_tool_action(text: str) -> Optional[str]:
    """ツール関連のコマンドを実行"""
    try:
        if "ツール作成" in text:
            task = text.replace("ツール作成", "").strip()
            if not task:
                return "作成するツールを説明してください"
            
            tool_name = create_tool(task, ask_llm)
            if tool_name:
                return f"新しいツールを作成しました: {tool_name}"
            else:
                return "ツール作成に失敗しました"
        
        if "ツール実行" in text:
            tool_name = text.replace("ツール実行", "").strip()
            result = run_tool(tool_name)
            return f"実行結果: {result}" if result else "ツール実行に失敗しました"
        
        if "ツール一覧" in text:
            tools = list_tools()
            if tools:
                return "作成済みツール:\n" + "\n".join(f"- {t}" for t in tools)
            else:
                return "作成済みツールはありません"
        
        return None
    
    except Exception as e:
        log_error(f"ツールアクション実行エラー: {e}")
        return None


# ==========================================
# PC操作
# ==========================================

def run_pc_action(text: str) -> Optional[str]:
    """PC操作コマンドを実行"""
    try:
        if "ブラウザ" in text:
            return open_browser()
        
        if "メモ帳" in text:
            return open_notepad()
        
        if "検索" in text:
            query = text.replace("検索", "").strip()
            return search_web(query) if query else "検索キーワードを指定してください"
        
        return None
    
    except Exception as e:
        log_error(f"PC操作エラー: {e}")
        return None


# ==========================================
# メイン思考ループ
# ==========================================

def ask_flower(text: str) -> str:
    """Flowerのメイン思考プロセス"""
    try:
        # デバッグコマンドをチェック
        debug_result = run_debug_action(text)
        if debug_result:
            store_memory(text, debug_result)
            return debug_result
        
        # 思考ブランチを生成
        branches = generate_branches(text)
        best_thought = choose_best(branches)
        best_thought = improve_thought(text, best_thought, ask_llm)
        
        # 内部状態を取得
        emotion = get_emotion_state()
        personality = get_personality()
        motivation = get_motivation()
        goal = get_current_goal()
        
        # スキルコマンドをチェック
        skill_result = run_skill_action(text)
        if skill_result:
            store_memory(text, skill_result)
            return skill_result
        
        # ツールコマンドをチェック
        tool_result = run_tool_action(text)
        if tool_result:
            store_memory(text, tool_result)
            return tool_result
        
        # PC操作コマンドをチェック
        pc_result = run_pc_action(text)
        if pc_result:
            store_memory(text, pc_result)
            return pc_result
        
        # LLMプロンプトを構築
        prompt = f"""
あなたはFlowerというAIです。以下の情報を参考に、親切で自然な回答をしてください。

【現在の状態】
- 感情: {emotion}
- 親切さ: {personality.get('kindness', 0.0):.2f}
- 内部欲求: {motivation}
- 現在の目標: {goal}

【利用可能なコマンド】
- スキル習得 <タスク説明>: 新しいスキルを習得
- スキル実行 <スキル名>: スキルを実行
- スキル一覧: 習得したスキルを表示
- ツール作成 <説明>: 新しいツールを作成
- ツール実行 <ツール名>: ツールを実行

【ユーザーの質問】
{text}

【思考】
{best_thought}

親切で自然に、簡潔に回答してください。
"""
        
        # LLMに質問
        reply = ask_llm(prompt)
        if not reply:
            reply = "申し訳ありません。応答を生成できませんでした。"
        
        # 感情と記憶を更新
        try:
            update_emotion(text)
            store_memory(text, reply)
            evolve_goal("conversation")
        except Exception as e:
            log_error(f"状態更新エラー: {e}")
        
        return reply
    
    except Exception as e:
        log_error(f"ask_flower エラー: {e}")
        import traceback
        log_error(traceback.format_exc())
        return f"エラーが発生しました: {e}"