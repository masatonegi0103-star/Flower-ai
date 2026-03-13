"""
Skill Executor - スキルの実行と自動選択
"""

from typing import Optional, Any, List
from skills.skill_registry import get_registry
from flower_os.logger import log, log_error

class SkillExecutor:
    """スキル実行エンジン"""
    
    def __init__(self):
        self.registry = get_registry()
    
    def execute(self, skill_name: str, *args, **kwargs) -> Optional[Any]:
        """
        スキルを実行
        
        Args:
            skill_name: スキル名
            *args: 位置引数
            **kwargs: キーワード引数
            
        Returns:
            実行結果
        """
        return self.registry.manager.execute_skill(skill_name, *args, **kwargs)
    
    def execute_by_keyword(self, keyword: str, *args, **kwargs) -> Optional[Any]:
        """
        キーワードからスキルを自動検索して実行
        
        Args:
            keyword: キーワード
            *args: 位置引数
            **kwargs: キーワード引数
            
        Returns:
            実行結果
        """
        skill = self.registry.find_skill(keyword)
        if skill:
            log(f"スキルを自動選択しました: {skill.name}")
            return self.execute(skill.name, *args, **kwargs)
        
        log_error(f"スキルが見つかりません: {keyword}")
        return None
    
    def execute_best_match(self, keywords: List[str], *args, **kwargs) -> Optional[Any]:
        """
        複数のキーワードから最適なスキルを選択して実行
        
        Args:
            keywords: キーワードリスト
            *args: 位置引数
            **kwargs: キーワード引数
            
        Returns:
            実行結果
        """
        skills = self.registry.find_skills(keywords)
        if not skills:
            log_error(f"スキルが見つかりません: {keywords}")
            return None
        
        # 熟練度が最も高いスキルを選択
        best_skill = max(skills.values(), key=lambda s: s.proficiency)
        log(f"最適なスキルを選択しました: {best_skill.name} (熟練度: {best_skill.proficiency:.2f})")
        return self.execute(best_skill.name, *args, **kwargs)

# グローバルエグゼキューター
_executor = SkillExecutor()

def get_executor() -> SkillExecutor:
    """エグゼキューターを取得"""
    return _executor

def execute_skill(skill_name: str, *args, **kwargs) -> Optional[Any]:
    """スキルを実行"""
    return _executor.execute(skill_name, *args, **kwargs)

def execute_skill_by_keyword(keyword: str, *args, **kwargs) -> Optional[Any]:
    """キーワードからスキルを実行"""
    return _executor.execute_by_keyword(keyword, *args, **kwargs)

def execute_best_matching_skill(keywords: List[str], *args, **kwargs) -> Optional[Any]:
    """最適なスキルを実行"""
    return _executor.execute_best_match(keywords, *args, **kwargs)