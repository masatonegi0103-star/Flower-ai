"""
Skill Registry - スキルの登録と検索
"""

from typing import Dict, List, Optional
from skills.skill_manager import get_skill_manager, SkillDefinition
from flower_os.logger import log

class SkillRegistry:
    """スキルレジストリ"""
    
    def __init__(self):
        self.manager = get_skill_manager()
    
    def register_skill(
        self,
        name: str,
        description: str,
        category: str,
        keywords: List[str],
        code: str
    ) -> bool:
        """スキルを登録"""
        return self.manager.add_skill(name, description, category, keywords, code)
    
    def find_skill(self, keyword: str) -> Optional[SkillDefinition]:
        """キーワードでスキルを検索"""
        skills = self.manager.get_skills_by_keywords([keyword])
        if skills:
            return list(skills.values())[0]
        return None
    
    def find_skills(self, keywords: List[str]) -> Dict[str, SkillDefinition]:
        """複数のキーワードでスキルを検索"""
        return self.manager.get_skills_by_keywords(keywords)
    
    def list_skills(self) -> List[str]:
        """スキル一覧を取得"""
        return list(self.manager.get_all_skills().keys())
    
    def list_skills_by_category(self, category: str) -> List[str]:
        """カテゴリ別にスキルを取得"""
        return list(self.manager.get_skills_by_category(category).keys())
    
    def get_skill_info(self, name: str) -> Optional[Dict]:
        """スキル情報を取得"""
        skill = self.manager.get_skill(name)
        if skill:
            return skill.to_dict()
        return None

# グローバルレジストリ
_registry = SkillRegistry()

def get_registry() -> SkillRegistry:
    """レジストリを取得"""
    return _registry

def load_skills() -> Dict[str, SkillDefinition]:
    """すべてのスキルを読み込む"""
    return _registry.manager.get_all_skills()