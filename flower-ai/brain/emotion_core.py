import json
import os
from typing import Dict
from flower_os.logger import log
from config import BRAIN_PATH

EMOTION_FILE = os.path.join(BRAIN_PATH, "emotion_state.json")
DEFAULT_EMOTION = {
    "joy": 0.5,
    "sadness": 0.0,
    "anger": 0.0,
    "fear": 0.0,
    "surprise": 0.0,
    "neutrality": 0.5
}

class EmotionCore:
    def __init__(self):
        self.emotions = self._load_emotions()
    
    def _load_emotions(self) -> Dict[str, float]:
        try:
            if os.path.exists(EMOTION_FILE):
                with open(EMOTION_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            log(f"感情状態ロードエラー: {e}")
        return DEFAULT_EMOTION.copy()
    
    def _save_emotions(self) -> None:
        try:
            os.makedirs(os.path.dirname(EMOTION_FILE), exist_ok=True)
            with open(EMOTION_FILE, "w", encoding="utf-8") as f:
                json.dump(self.emotions, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log(f"感情状態保存エラー: {e}")
    
    def update_emotion(self, emotion_type: str, delta: float) -> None:
        if emotion_type in self.emotions:
            self.emotions[emotion_type] = max(0.0, min(1.0, self.emotions[emotion_type] + delta))
            self._save_emotions()
    
    def get_dominant_emotion(self) -> str:
        return max(self.emotions, key=self.emotions.get)
    
    def get_all_emotions(self) -> Dict[str, float]:
        return self.emotions.copy()

_emotion_core = EmotionCore()

def get_emotion_state() -> str:
    return _emotion_core.get_dominant_emotion()

def update_emotion(text: str, sentiment: float = 0.1) -> None:
    try:
        if "悲しい" in text or "つらい" in text:
            _emotion_core.update_emotion("sadness", sentiment)
        elif "嬉しい" in text or "楽しい" in text:
            _emotion_core.update_emotion("joy", sentiment)
        elif "怒り" in text or "ムカつく" in text:
            _emotion_core.update_emotion("anger", sentiment)
        else:
            _emotion_core.update_emotion("neutrality", 0.05)
    except Exception as e:
        log(f"感情更新エラー: {e}")