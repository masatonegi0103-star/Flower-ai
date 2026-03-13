"""
Flower AI Main Entry Point
"""

import threading
import sys
from gui import FlowerGUI
from flower_os.logger import log, log_error
from flower_os.self_repair import repair, check_dependencies

def main():
    """メイン実行関数"""
    try:
        # ログに開始を記録
        log("=== Flower AI 起動開始 ===")
        
        # 依存関係チェック
        if not check_dependencies():
            log_error("依存関係のチェックに失敗しました")
            sys.exit(1)
        
        # システム修復
        if not repair():
            log_error("システム修復に失敗しました")
            sys.exit(1)
        
        # GUIを起動
        log("GUIを初期化中...")
        gui = FlowerGUI()
        
        log("Flower AIの起動に成功しました")
        log("=== GUI実行開始 ===")
        
        # GUI実行
        gui.run()
        
        log("=== Flower AI 終了 ===")
    
    except Exception as e:
        log_error(f"メイン実行エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()