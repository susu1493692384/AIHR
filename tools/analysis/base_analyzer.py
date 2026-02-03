# tools/analysis/base_analyzer.py
"""分析工具基类"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from core.models import ParsedResume, AnalysisResult, CleanedResume
from core.config import ScoreConfig


class BaseAnalyzer(ABC):
    """分析工具基类"""

    def __init__(self, config: ScoreConfig = None):
        """
        初始化分析器

        Args:
            config: 评分配置（如果为None，自动加载默认配置）
        """
        if config is None:
            # 自动加载默认配置文件
            try:
                self.config = ScoreConfig.from_yaml("config/scoring.yaml")
            except:
                # 如果加载失败，使用空配置
                self.config = ScoreConfig()
        else:
            self.config = config

    @abstractmethod
    def analyze(self, resume: CleanedResume) -> AnalysisResult:
        """
        分析简历

        Args:
            resume: 清洗后的简历

        Returns:
            AnalysisResult: 分析结果
        """
        pass

    @abstractmethod
    def get_dimension_name(self) -> str:
        """获取分析维度名称"""
        pass

    @abstractmethod
    def get_weight(self) -> float:
        """获取该维度的权重"""
        pass

    def _calculate_base_score(self, scores: Dict[str, float], weights: Dict[str, float]) -> float:
        """
        计算基础分数

        Args:
            scores: 各项得分
            weights: 各项权重

        Returns:
            float: 综合分数
        """
        total = sum(score * weights.get(key, 0) for key, score in scores.items())
        return round(total, 2)

    def _extract_insights(self, resume: CleanedResume) -> list[str]:
        """
        提取关键发现

        Args:
            resume: 简历数据

        Returns:
            List[str]: 关键发现列表
        """
        return []

    def _extract_highlights(self, resume: CleanedResume) -> list[str]:
        """
        提取亮点

        Args:
            resume: 简历数据

        Returns:
            List[str]: 亮点列表
        """
        return []

    def _extract_weaknesses(self, resume: CleanedResume) -> list[str]:
        """
        提取不足

        Args:
            resume: 简历数据

        Returns:
            List[str]: 不足列表
        """
        return []
