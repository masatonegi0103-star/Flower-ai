"""
Memory Core Module
"""

import json
import os
from datetime import datetime
from config import MEMORY_PATH

MEMORY_FILE = os.path.join(MEMORY_PATH, "memory.json")

class MemoryCore:
    """メモリ管理システム"""
    
    def __init__(self):
        self.memories = self._load_memories()
    
    def _load_memories(self) -> list:
        """メモリを読み込む"""
        try:
            if os.path.exists(MEMORY_FILE):
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def _save_memories(self) -> None:
        """メモリを保存"""
        try:
            os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.memories, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def store(self, user_input: str, ai_response: str) -> None:
        """対話を記憶"""
        memory = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "ai": ai_response
        }
        self.memories.append(memory)
        self._save_memories()

_memory_core = MemoryCore()

def store_memory(user_input: str, ai_response: str) -> None:
    """メモリに対話を保存"""
    _memory_core.store(user_input, ai_response)