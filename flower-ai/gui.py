"""
Flower AI GUI Module
"""

import tkinter as tk
from tkinter import scrolledtext
import threading
from queue import Queue
from llm_core import ask_flower
from brain.emotion_core import get_emotion_state
from brain.personality_core import get_personality
from flower_os.logger import log, log_error

class FlowerGUI:
    """Flower AIのメインGUIクラス"""
    
    def __init__(self):
        """GUIの初期化"""
        self.root = tk.Tk()
        self.root.title("Flower AI v8")
        self.root.geometry("800x600")
        
        # スレッド間通信用キュー
        self.message_queue = Queue()
        
        # チャットウィンドウ
        self.chat = scrolledtext.ScrolledText(
            self.root,
            height=20,
            width=80,
            state=tk.DISABLED
        )
        self.chat.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # 入力フィールド
        self.entry = tk.Entry(self.root, width=70, font=("Arial", 12))
        self.entry.pack(padx=10, pady=5)
        self.entry.bind("<Return>", lambda e: self.send())
        
        # 送信ボタン
        send_btn = tk.Button(self.root, text="Send", command=self.send, width=15)
        send_btn.pack(pady=5)
        
        # ステータスバー
        self.status = tk.Label(self.root, text="", bg="lightgray")
        self.status.pack(fill=tk.X, padx=5, pady=5)
        
        # 定期的なステータス更新
        self.update_status()
        
        # キューの定期チェック
        self.check_message_queue()
        
        log("GUI初期化完了")
    
    def update_status(self):
        """ステータスを更新"""
        try:
            emo = get_emotion_state()
            pers = get_personality()
            txt = f"Emotion: {emo} | Kindness: {pers.get('kindness', 0.0):.2f} | Status: Ready"
            self.status.config(text=txt)
        except Exception as e:
            log_error(f"ステータス更新エラー: {e}")
        
        self.root.after(3000, self.update_status)
    
    def check_message_queue(self):
        """バックグラウンドスレッドからのメッセージをチェック"""
        try:
            while not self.message_queue.empty():
                msg = self.message_queue.get_nowait()
                self._append_to_chat(msg)
        except:
            pass
        
        self.root.after(100, self.check_message_queue)
    
    def _append_to_chat(self, message: str):
        """チャットにメッセージを追加"""
        try:
            self.chat.config(state=tk.NORMAL)
            self.chat.insert(tk.END, message + "\n")
            self.chat.see(tk.END)
            self.chat.config(state=tk.DISABLED)
        except Exception as e:
            log_error(f"チャット追加エラー: {e}")
    
    def send(self):
        """メッセージを送信"""
        try:
            text = self.entry.get()
            if not text.strip():
                return
            
            self.entry.delete(0, tk.END)
            
            # ユーザーメッセージを表示
            self._append_to_chat(f"\nYou: {text}")
            
            # バックグラウンドで応答を生成
            thread = threading.Thread(target=self._get_response, args=(text,), daemon=True)
            thread.start()
            
        except Exception as e:
            log_error(f"送信エラー: {e}")
            self._append_to_chat(f"エラーが発生しました: {e}")
    
    def _get_response(self, text: str):
        """バックグラウンドで応答を取得"""
        try:
            reply = ask_flower(text)
            if reply:
                self.message_queue.put(f"Flower: {reply}")
            else:
                self.message_queue.put("Flower: 応答を生成できませんでした")
        except Exception as e:
            log_error(f"応答生成エラー: {e}")
            self.message_queue.put(f"Flower: エラーが発生しました - {e}")
    
    def run(self):
        """GUIを実行"""
        self.root.mainloop()