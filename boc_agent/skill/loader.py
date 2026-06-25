import os
from typing import Optional
from boc_agent.skill.models import Skill
from boc_agent.skill.parser import parse_skill_markdown
from boc_agent.skill.validator import validate_and_build_skill

class SkillLoader:
    _instance: Optional["SkillLoader"] = None
    _cached_skill: Optional[Skill] = None
    _loaded_path: Optional[str] = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SkillLoader, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def load_from_file(self, file_path: Optional[str] = None, force_reload: bool = False) -> Skill:
        """Loads, parses, validates, and caches the Skill configuration."""
        if file_path is None:
            file_path = os.getenv("BOC_SKILL_FILE_PATH", "SKILL.md")

        if self._cached_skill and self._loaded_path == file_path and not force_reload:
            return self._cached_skill

        # Try relative to current working directory, otherwise look in parent dirs if not found
        target_path = file_path
        if not os.path.exists(target_path):
            # Fallback search up to 2 directories (e.g. if running tests from tests/ folder)
            lookups = [
                os.path.join("..", file_path),
                os.path.join("..", "..", file_path)
            ]
            for candidate in lookups:
                if os.path.exists(candidate):
                    target_path = candidate
                    break

        if not os.path.exists(target_path):
            raise FileNotFoundError(f"SKILL.md not found at path: {file_path}")

        with open(target_path, "r", encoding="utf-8") as f:
            content = f.read()

        frontmatter, sections = parse_skill_markdown(content)
        skill = validate_and_build_skill(frontmatter, sections)
        
        self._cached_skill = skill
        self._loaded_path = file_path
        return skill

    def get_skill(self, file_path: Optional[str] = None) -> Skill:
        """Retrieves the cached Skill, loading it from disk if not already cached."""
        return self.load_from_file(file_path)

def get_active_skill(file_path: Optional[str] = None) -> Skill:
    """Helper function to load the active Skill contract."""
    return SkillLoader().get_skill(file_path)
