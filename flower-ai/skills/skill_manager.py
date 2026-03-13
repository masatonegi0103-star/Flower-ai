"""
Skill Manager - Flower自己スキル習得システム（改善版）
"""

import json
import os
import inspect
from typing import Dict, List, Callable, Optional, Any
from datetime import datetime
from flower_os.logger import log, log_error
from config import BASE_DIR

SKILLS_DIR = os.path.join(BASE_DIR, "skills", "learned_skills")
SKILLS_METADATA_FILE = os.path.join(SKILLS_DIR, "skills_metadata.json")

# ディレクトリが存在しないなら作成
os.makedirs(SKILLS_DIR, exist_ok=True)


class SkillDefinition:
    """スキルの定義"""
    
    def __init__(
        self,
        name: str,
        description: str,
        category: str,
        keywords: List[str],
        code: str,
        proficiency: float = 0.5,
        usage_count: int = 0,
        success_rate: float = 0.0
    ):
        self.name = name
        self.description = description
        self.category = category
        self.keywords = keywords
        self.code = code
        self.proficiency = proficiency
        self.usage_count = usage_count
        self.success_rate = success_rate
        self.created_at = datetime.now().isoformat()
        self.last_used = None
    
    def to_dict(self) -> Dict:
        """辞書に変換"""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "keywords": self.keywords,
            "proficiency": self.proficiency,
            "usage_count": self.usage_count,
            "success_rate": self.success_rate,
            "created_at": self.created_at,
            "last_used": self.last_used
        }
    
    @staticmethod
    def from_dict(data: Dict) -> "SkillDefinition":
        """辞書から復元"""
        skill = SkillDefinition(
            name=data["name"],
            description=data["description"],
            category=data["category"],
            keywords=data["keywords"],
            code="",  # コードは別に読み込む
            proficiency=data.get("proficiency", 0.5),
            usage_count=data.get("usage_count", 0),
            success_rate=data.get("success_rate", 0.0)
        )
        skill.created_at = data.get("created_at", datetime.now().isoformat())
        skill.last_used = data.get("last_used")
        return skill


class SkillManager:
    """スキル管理システムの中核"""
    
    def __init__(self):
        self.skills: Dict[str, SkillDefinition] = {}
        self.skill_functions: Dict[str, Callable] = {}
        self._load_all_skills()
    
    def _load_all_skills(self) -> None:
        """保存されたスキルをすべて読み込む"""
        try:
            if not os.path.exists(SKILLS_METADATA_FILE):
                log("スキルメタデータファイルが見つかりません。新規作成します。")
                return
            
            with open(SKILLS_METADATA_FILE, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            
            for skill_name, skill_data in metadata.items():
                skill = SkillDefinition.from_dict(skill_data)
                
                # コードを読み込む
                code_file = os.path.join(SKILLS_DIR, f"{skill_name}.py")
                if os.path.exists(code_file):
                    with open(code_file, "r", encoding="utf-8") as f:
                        skill.code = f.read()
                    self.skills[skill_name] = skill
                else:
                    log_error(f"スキルコードファイルが見つかりません: {code_file}")
            
            log(f"{len(self.skills)}個のスキルを読み込みました")
        
        except Exception as e:
            log_error(f"スキル読み込みエラー: {e}")
    
    def _save_metadata(self) -> None:
        """メタデータを保存"""
        try:
            os.makedirs(os.path.dirname(SKILLS_METADATA_FILE), exist_ok=True)
            
            metadata = {
                name: skill.to_dict()
                for name, skill in self.skills.items()
            }
            
            with open(SKILLS_METADATA_FILE, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            log(f"メタデータを保存しました: {SKILLS_METADATA_FILE}")
        
        except Exception as e:
            log_error(f"メタデータ保存エラー: {e}")
    
    def add_skill(
        self,
        name: str,
        description: str,
        category: str,
        keywords: List[str],
        code: str
    ) -> bool:
        """
        新しいスキルを追加
        
        Args:
            name: スキル名
            description: 説明
            category: カテゴリ
            keywords: キーワードリスト
            code: Pythonコード
            
        Returns:
            成功したかどうか
        """
        try:
            log(f"スキル追加開始: {name}")
            
            # 名前の検証
            if not self._is_valid_skill_name(name):
                log_error(f"無効なスキル名: {name}")
                return False
            
            # コードの検証
            if not self._validate_skill_code(code):
                log_error(f"無効なスキルコード: {name}")
                return False
            
            # スキルを作成
            skill = SkillDefinition(
                name=name,
                description=description,
                category=category,
                keywords=keywords,
                code=code
            )
            
            # ファイルに保存
            code_file = os.path.join(SKILLS_DIR, f"{name}.py")
            with open(code_file, "w", encoding="utf-8") as f:
                f.write(code)
            
            log(f"スキルコードを保存しました: {code_file}")
            
            # メモリに保存
            self.skills[name] = skill
            self._save_metadata()
            
            log(f"スキルを追加しました: {name}")
            return True
        
        except Exception as e:
            log_error(f"スキル追加エラー: {e}")
            import traceback
            log_error(f"トレースバック: {traceback.format_exc()}")
            return False
    
    def _is_valid_skill_name(self, name: str) -> bool:
        """スキル名が有効かチェック"""
        import re
        is_valid = bool(re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name))
        if not is_valid:
            log_error(f"スキル名は英数字とアンダースコアのみ使用可: {name}")
        return is_valid
    
    def _validate_skill_code(self, code: str) -> bool:
        """スキルコードの基本的な検証"""
        try:
            # 構文チェック
            compile(code, "<string>", "exec")
            log("スキルコード構文チェック: OK")
            
            # execute関数の存在確認
            if "def execute" not in code:
                log_error("スキルコードに 'def execute' 関数が見つかりません")
                return False
            
            # 危険な関数の使用チェック
            dangerous_functions = [
                "os.remove", "os.system", "eval", 
                "__import__", "open("
            ]
            
            dangerous_found = []
            for func in dangerous_functions:
                if func in code:
                    dangerous_found.append(func)
            
            if dangerous_found:
                log_error(f"危険な関数が検出されました: {dangerous_found}")
                return False
            
            log("スキルコード検証: OK")
            return True
        
        except SyntaxError as e:
            log_error(f"スキルコードに構文エラーがあります: {e}")
            return False
        except Exception as e:
            log_error(f"コード検証エラー: {e}")
            return False
    
    def execute_skill(self, name: str, *args, **kwargs) -> Optional[Any]:
        """
        スキルを実行
        
        Args:
            name: スキル名
            *args: 位置引数
            **kwargs: キーワード引数
            
        Returns:
            スキルの実行結果
        """
        try:
            log(f"スキル実行開始: {name}")
            
            if name not in self.skills:
                log_error(f"スキルが見つかりません: {name}")
                log(f"利用可能なスキル: {list(self.skills.keys())}")
                return None
            
            skill = self.skills[name]
            
            if not skill.code:
                log_error(f"スキルコードが空です: {name}")
                return None
            
            # スキルコードを実行
            namespace = {"__builtins__": __builtins__}
            exec(skill.code, namespace)
            
            # execute関数を探す
            if "execute" not in namespace:
                log_error(f"スキルに execute 関数がありません: {name}")
                log(f"利用可能な関数: {list(namespace.keys())}")
                return None
            
            execute_func = namespace["execute"]
            
            # 関数を実行
            log(f"スキルの execute 関数を呼び出し中...")
            result = execute_func(*args, **kwargs)
            
            # 統計を更新
            skill.usage_count += 1
            skill.last_used = datetime.now().isoformat()
            skill.success_rate = (skill.success_rate * (skill.usage_count - 1) + 1.0) / skill.usage_count
            skill.proficiency = min(1.0, skill.proficiency + 0.01)
            self._save_metadata()
            
            log(f"スキル実行成功: {name}")
            return result
        
        except Exception as e:
            log_error(f"スキル実行エラー ({name}): {e}")
            import traceback
            log_error(f"トレースバック: {traceback.format_exc()}")
            
            # 失敗を記録
            if name in self.skills:
                skill = self.skills[name]
                skill.usage_count += 1
                skill.last_used = datetime.now().isoformat()
                if skill.usage_count > 0:
                    skill.success_rate = (skill.success_rate * (skill.usage_count - 1)) / skill.usage_count
                self._save_metadata()
            
            return None
    
    def get_skill(self, name: str) -> Optional[SkillDefinition]:
        """スキルを取得"""
        return self.skills.get(name)
    
    def get_all_skills(self) -> Dict[str, SkillDefinition]:
        """すべてのスキルを取得"""
        return self.skills.copy()
    
    def get_skills_by_category(self, category: str) -> Dict[str, SkillDefinition]:
        """カテゴリ別にスキルを取得"""
        return {
            name: skill
            for name, skill in self.skills.items()
            if skill.category == category
        }
    
    def get_skills_by_keywords(self, keywords: List[str]) -> Dict[str, SkillDefinition]:
        """キーワードで検索"""
        result = {}
        for name, skill in self.skills.items():
            if any(kw in skill.keywords for kw in keywords):
                result[name] = skill
        return result
    
    def delete_skill(self, name: str) -> bool:
        """スキルを削除"""
        try:
            if name not in self.skills:
                return False
            
            # ファイルを削除
            code_file = os.path.join(SKILLS_DIR, f"{name}.py")
            if os.path.exists(code_file):
                os.remove(code_file)
            
            # メモリから削除
            del self.skills[name]
            self._save_metadata()
            
            log(f"スキルを削除しました: {name}")
            return True
        
        except Exception as e:
            log_error(f"スキル削除エラー: {e}")
            return False
    
    def improve_skill(self, name: str) -> bool:
        """スキルを改善"""
        try:
            if name not in self.skills:
                return False
            
            skill = self.skills[name]
            
            # 熟練度を増加
            skill.proficiency = min(1.0, skill.proficiency + 0.05)
            
            self._save_metadata()
            log(f"スキルを改善しました: {name} (熟練度: {skill.proficiency:.2f})")
            return True
        
        except Exception as e:
            log_error(f"スキル改善エラー: {e}")
            return False
    
    def get_skill_summary(self) -> str:
        """スキルの概要を取得"""
        if not self.skills:
            return "習得したスキルはありません"
        
        summary = "【習得スキル一覧】\n"
        for name, skill in self.skills.items():
            summary += f"- {name}: {skill.description}\n"
            summary += f"  カテゴリ: {skill.category}, 熟練度: {skill.proficiency:.2f}, 使用回数: {skill.usage_count}\n"
        
        return summary
    
    def get_debug_info(self) -> str:
        """デバッグ情報を取得"""
        info = f"""
【デバッグ情報】
- スキルディレクトリ: {SKILLS_DIR}
- メタデータファイル: {SKILLS_METADATA_FILE}
- 読み込み済みスキル数: {len(self.skills)}
- スキル名���覧: {list(self.skills.keys())}
- ディレクトリの内容:
"""
        try:
            if os.path.exists(SKILLS_DIR):
                files = os.listdir(SKILLS_DIR)
                for f in files:
                    info += f"  - {f}\n"
            else:
                info += f"  ディレクトリが存在しません\n"
        except Exception as e:
            info += f"  読み込みエラー: {e}\n"
        
        return info


# グローバルインスタンス
_skill_manager = SkillManager()

def get_skill_manager() -> SkillManager:
    """スキルマネージャーを取得"""
    return _skill_manager