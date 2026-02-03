# tools/analysis/__init__.py
"""分析工具模块"""

# 新版分析器（使用 OOP 设计）
from tools.analysis.technical_analyzer import TechnicalAnalyzer
from tools.analysis.experience_analyzer import ExperienceAnalyzer
from tools.analysis.project_analyzer_simple import SimpleProjectAnalyzer
from tools.analysis.soft_skill_analyzer import SoftSkillAnalyzer

__all__ = [
    "TechnicalAnalyzer",
    "ExperienceAnalyzer",
    "SimpleProjectAnalyzer",
    "SoftSkillAnalyzer",
]
