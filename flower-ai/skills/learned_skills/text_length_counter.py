def execute(*args, **kwargs):
    # 入力チェック
    if len(args) == 0:
        return "エラー: テキストを入力してください"
    
    # 変数定義
    input_text = str(args[0])
    
    # テキストの長さを計算
    text_length = len(input_text)
    
    # 結果を作成
    result = f"テキストの長さ: {text_length}文字"
    
    # 結果を返す
    return result