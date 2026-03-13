def execute(*args, **kwargs):
    # 入力チェック
    if len(args) < 2:
        return "エラー: 検索対象のテキストと検索語を入力してください"
    
    # 変数定義
    target_text = str(args[0])
    search_term = str(args[1])
    
    # 検索処理
    try:
        occurrences = target_text.lower().count(search_term.lower())
    except Exception as e:
        return f"エラー: 検索中に問題が発生しました - {str(e)}"
    
    # 結果を作成
    result = f"'{search_term}' はテキスト内に {occurrences} 回見つかりました"
    
    # 結果を返す
    return result