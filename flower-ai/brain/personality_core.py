"""
Personality Core Module
"""

import json
import os
from typing import Dict
from config import BRAIN_PATH

PERSONALITY_FILE = os.path.join(BRAIN_PATH, "personality_state.json")

DEFAULT_PERSONALITY = {
    "kindness": 0.8,
    "curiosity": 0.7,
    "assertiveness": 0.5,
    "patience": 0.7,
    "humility": 0.6
}

class PersonalityCore:
    """性格管理システム"""
    
    def __init__(self):
        self.personality = self._load_personality()
    
    def _load_personality(self) -> Dict[str, float]:
        """性格を読み込む"""
        try:
            if os.path.exists(PERSONALITY_FILE):
                with open(PERSONALITY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except:
            pass
        
        return DEFAULT_PERSONALITY.copy()
    
    def _save_personality(self) -> None:
        """性格を保存"""
        try:
            os.makedirs(os.path.dirname(PERSONALITY_FILE), exist_ok=True)
            with open(PERSONALITY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.personality, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def get_all(self) -> Dict[str, float]:
        """すべての性格特性を取得"""
        return self.personality.copy()

# グローバルインスタンス
_personality_core = PersonalityCore()

def get_personality() -> Dict[str, float]:
    """現在の性格を取得"""
    return _personality_core.get_all()