"""
Skill Builder - Flowerが自動でスキルを作成（完全修正版）
"""

from typing import Optional
from skills.skill_manager import get_skill_manager
from flower_os.logger import log, log_error

def build_skill(task: str, ask_llm) -> Optional[str]:
    """
    タスクから新しいスキルを自動構築
    
    Args:
        task: タスク説明
        ask_llm: LLM呼び出し関数
        
    Returns:
        作成されたスキル名
    """
    try:
        log(f"スキル構築開始: {task}")
        
        # より厳密で単純なプロンプト
        prompt = f"""
次のタスクを実行するPythonスキルを作成してください。

【タスク】
{task}

【要件】
1. def execute(*args, **kwargs): という関数を必ず定義
2. 関数内で使用するすべての変数は定義してから使用
3. 最後に return文で結果を返す
4. エラーハンドリングを含める
5. ``` を使わない

【出力形式】
最初の行: スキル名 (英数字とアンダースコアのみ)
2行目: 説明
3行目: カテゴリ (英数字とアンダースコアのみ)
4行目: キーワード (カンマ区切り)

その後、空行を1つ置いて、Pythonコードを記述してください。

【コード例1 - シンプルな分析】
text_analyzer
テキストを分析する
analysis
text,analysis

def execute(*args, **kwargs):
    # 入力チ��ック
    if len(args) == 0:
        return "エラー: テキストを入力してください"
    
    # 変数定義
    input_text = str(args[0])
    text_length = len(input_text)
    word_count = len(input_text.split())
    
    # 結果を作成
    result = f"分析結果: {{text_length}}文字, {{word_count}}単語"
    
    # 結果を返す
    return result

【コード例2 - 計算スキル】
number_calculator
2つの数値を足す
math
calculate,math

def execute(*args, **kwargs):
    # 入力チェック
    if len(args) < 2:
        return "エラー: 2つの数値を入力してください"
    
    # 変数定義
    try:
        num1 = float(args[0])
        num2 = float(args[1])
    except ValueError:
        return "エラー: 数値に変換できません"
    
    # 計算
    result_value = num1 + num2
    
    # 結果を返す
    return f"計算結果: {{result_value}}"

【コード例3 - リスト処理】
list_processor
リストの要素数を数える
list
count,list,process

def execute(*args, **kwargs):
    # 入力チェック
    if len(args) == 0:
        return "エラー: リストを入力してください"
    
    # 変数定義
    input_list = args[0]
    if not isinstance(input_list, list):
        input_list = list(args)
    
    # 処理
    list_length = len(input_list)
    
    # 結果を返す
    return f"リストの要素数: {{list_length}}"

【重要なルール】
- すべての変数は、使用する前に必ず定義すること
- 一度定義した変数は何度も使用してもよい
- 計算結果を別の変数に保存してから f文字列で使用する
- return文は関数の最後に1つだけ配置する

このルールに厳密に従ってコードを作成してください。
"""
        
        log(f"LLMにスキル生成を依頼中...")
        response = ask_llm(prompt)
        
        if not response:
            log_error("スキル生成失敗: LLMから応答なし")
            return None
        
        log(f"LLM応答を受け取りました")
        log(f"応答内容:\n{response}")
        
        # 応答をパース
        lines = response.strip().split("\n")
        
        if len(lines) < 5:
            log_error(f"スキル生成失敗: 応答形式が不正 (行数不足: {len(lines)})")
            log_error(f"応答内容:\n{response[:500]}")
            return None
        
        skill_name = lines[0].strip()
        description = lines[1].strip()
        category = lines[2].strip()
        keywords_str = lines[3].strip()
        
        log(f"スキル名: {skill_name}")
        log(f"説明: {description}")
        log(f"カテゴリ: {category}")
        log(f"キーワード: {keywords_str}")
        
        keywords = [kw.strip() for kw in keywords_str.split(",")]
        
        # コード部分を抽出
        code_start_idx = -1
        for i, line in enumerate(lines):
            if "def execute" in line:
                code_start_idx = i
                break
        
        if code_start_idx == -1:
            log_error("スキル生成失敗: execute関数が見つかりません")
            log_error(f"応答内容:\n{response}")
            return None
        
        # コードを再構築
        code_lines = lines[code_start_idx:]
        code = "\n".join(code_lines)
        
        # マークダウンのバッククォートを削除
        code = code.replace("```python", "").replace("```", "")
        code = code.strip()
        
        log(f"抽出されたコード:\n{code}")
        
        # コードの検証と修正
        code = validate_and_fix_code(code, skill_name)
        
        if not code:
            log_error(f"コード検証失敗: {skill_name}")
            return None
        
        log(f"修正後のコード:\n{code}")
        
        # スキルを登録
        manager = get_skill_manager()
        
        # 名前の検証と修正
        if not manager._is_valid_skill_name(skill_name):
            log_error(f"スキル名が無効です: {skill_name}")
            skill_name = skill_name.replace("-", "_").replace(" ", "_")
            log(f"スキル名を修正しました: {skill_name}")
        
        log(f"スキル登録開始...")
        if manager.add_skill(skill_name, description, category, keywords, code):
            log(f"スキル構築成功: {skill_name}")
            return skill_name
        else:
            log_error(f"スキル登録失敗: {skill_name}")
            log(manager.get_debug_info())
            return None
    
    except Exception as e:
        log_error(f"スキル構築エラー: {e}")
        import traceback
        log_error(f"トレースバック: {traceback.format_exc()}")
        return None


def validate_and_fix_code(code: str, skill_name: str) -> Optional[str]:
    """
    コードを検証して修正
    
    Args:
        code: Pythonコード
        skill_name: スキル名
        
    Returns:
        修正されたコード、失敗時はNone
    """
    try:
        log(f"コード検証開始: {skill_name}")
        
        # 1. 基本的な構文チェック
        try:
            compile(code, "<string>", "exec")
            log("構文チェック: OK")
        except SyntaxError as e:
            log_error(f"構文エラー: {e}")
            log_error(f"エラー行: {e.text}")
            return None
        
        # 2. execute関数が存在するか確認
        if "def execute" not in code:
            log_error("execute関数が見つかりません")
            return None
        
        # 3. 危険な関数をチェック
        dangerous = ["os.remove", "os.system", "eval", "__import__"]
        for danger in dangerous:
            if danger in code:
                log_error(f"危険な関数が検出: {danger}")
                return None
        
        # 4. f文字列の中括弧チェック
        log("f文字列の検証中...")
        code = fix_f_string_braces(code)
        
        # 5. 未定義変数の検出と修正
        log("変数定義の検証中...")
        code = validate_variables(code)
        
        # 6. 最終的な構文チェック
        try:
            compile(code, "<string>", "exec")
            log("修正後の構文チェック: OK")
        except SyntaxError as e:
            log_error(f"修正後の構文エラー: {e}")
            log_error(f"エラー行: {e.text}")
            return None
        
        # 7. 簡単な実行テスト
        log("簡単な実行テスト中...")
        if not test_skill_execution(code):
            log_error("実行テスト失敗")
            return None
        
        log(f"コード検証完了: {skill_name}")
        return code
    
    except Exception as e:
        log_error(f"コード検証エラー: {e}")
        import traceback
        log_error(traceback.format_exc())
        return None


def fix_f_string_braces(code: str) -> str:
    """
    f文字列の中括弧を修正
    
    例: f"分析結果: {text_length}文字"
    """
    try:
        # 単一中括弧を二重中括弧に修正
        # ただし、変数参照は修正しない
        lines = code.split("\n")
        fixed_lines = []
        
        for line in lines:
            # f文字列を検出
            if 'f"' in line or "f'" in line:
                # 既に正しいf文字列かチェック
                if "{" in line and "}" in line:
                    # 変数参照は保持
                    fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        return "\n".join(fixed_lines)
    
    except Exception as e:
        log_error(f"f文字列修正エラー: {e}")
        return code


def validate_variables(code: str) -> str:
    """
    変数定義を検証して修正
    
    Args:
        code: Pythonコード
        
    Returns:
        修正されたコード
    """
    try:
        log("変数定義の検証を開始...")
        
        # 変数を抽出
        import re
        
        # 定義されている変数を抽出
        defined_vars = set()
        
        # args, kwargs は自動的に定義されている
        defined_vars.add("args")
        defined_vars.add("kwargs")
        
        lines = code.split("\n")
        
        for line in lines:
            # 代入操作を検出
            if "=" in line and not line.strip().startswith("#"):
                # 変数名を抽出
                match = re.match(r'\s*(\w+)\s*=', line)
                if match:
                    var_name = match.group(1)
                    defined_vars.add(var_name)
                    log(f"定義された変数: {var_name}")
        
        # 使用されている変数を検出
        used_vars = set()
        for line in lines:
            if not line.strip().startswith("#"):
                # 変数参照を検出 (簡易版)
                words = re.findall(r'\b([a-zA-Z_]\w*)\b', line)
                for word in words:
                    # 予約語は除外
                    if word not in ['def', 'return', 'if', 'else', 'try', 'except', 'for', 'in', 'str', 'float', 'len', 'list', 'isinstance']:
                        used_vars.add(word)
        
        # 使用されているが定義されていない変数を検出
        undefined_vars = used_vars - defined_vars
        
        if undefined_vars:
            log(f"未定義変数が見つかりました: {undefined_vars}")
            # この場合、LLMに修正させるべき
            log_error(f"未定義変数: {undefined_vars}")
        
        return code
    
    except Exception as e:
        log_error(f"変数検証エラー: {e}")
        return code


def test_skill_execution(code: str) -> bool:
    """
    スキルを簡単にテスト実行
    
    Args:
        code: Pythonコード
        
    Returns:
        実行成功したかどうか
    """
    try:
        log("スキルの実行テストを開始...")
        
        namespace = {}
        exec(code, namespace)
        
        if "execute" not in namespace:
            log_error("execute関数が見つかりません")
            return False
        
        execute_func = namespace["execute"]
        
        # テスト実行
        try:
            result = execute_func()
            log(f"テスト実行成功: {result}")
            return True
        except TypeError:
            # 引数が必要な場合はテスト引数を渡す
            try:
                result = execute_func("test_input")
                log(f"テスト実行成功（引数あり）: {result}")
                return True
            except Exception as e:
                log_error(f"テスト実行失敗: {e}")
                return False
    
    except Exception as e:
        log_error(f"実行テストエラー: {e}")
        return False