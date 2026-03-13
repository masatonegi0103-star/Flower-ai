"""
PC Control Module
"""

import subprocess
import webbrowser
from flower_os.logger import log, log_error

def open_browser(url: str = "https://www.google.com") -> str:
    """ブラウザを開く"""
    try:
        webbrowser.open(url)
        return f"ブラウザを開きました: {url}"
    except Exception as e:
        log_error(f"ブラウザ起動エラー: {e}")
        return "ブラウザを開けませんでした"

def open_notepad(filename: str = "note.txt") -> str:
    """メモ帳を開く"""
    try:
        subprocess.Popen(["notepad", filename])
        return f"メモ帳を開きました: {filename}"
    except Exception as e:
        log_error(f"メモ帳起動エラー: {e}")
        return "メモ帳を開けませんでした"

def search_web(query: str) -> str:
    """Webを検索"""
    try:
        search_url = f"https://www.google.com/search?q={query}"
        webbrowser.open(search_url)
        return f"検索しました: {query}"
    except Exception as e:
        log_error(f"Web検索エラー: {e}")
        return "検索できませんでした"