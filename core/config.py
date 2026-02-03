# core/config.py
from dataclasses import dataclass, field
from typing import Dict, List
import yaml
from pathlib import Path


@dataclass
class ScoreConfig:
    """评分配置类"""
    weights: Dict[str, float] = field(default_factory=lambda: {
        "technical": 0.25,
        "experience": 0.20,
        "project": 0.40,
        "soft_skill": 0.15
    })
    school_tier: Dict[str, list] = field(default_factory=dict)

    # 经验背景评分配置
    experience_dimension_weights: Dict[str, float] = field(default_factory=lambda: {
        "education": 0.30,
        "work": 0.60,
        "internship": 0.10
    })
    degree_scores: Dict[str, float] = field(default_factory=dict)
    school_tier_scores: Dict[str, float] = field(default_factory=dict)
    cs_related_majors: List[str] = field(default_factory=list)

    # 工作经验评分配置
    work_experience_scoring: Dict[str, float] = field(default_factory=lambda: {
        "score_per_year": 10,
        "max_score": 60,
        "cap_years": 6
    })

    # 实习经验评分配置
    internship_scoring: Dict[str, float] = field(default_factory=lambda: {
        "score_per_month": 0.83,
        "max_score": 10,
        "cap_months": 12
    })

    # 注意：项目评分已改用极简评分器（SimpleProjectAnalyzer）
    # 评分规则已内置在代码中，无需额外配置

    @classmethod
    def from_yaml(cls, path: str) -> "ScoreConfig":
        """从YAML文件加载配置"""
        config_file = Path(path)
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {path}")

        with open(config_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        return cls(
            weights=data.get("weights", {}),
            school_tier=data.get("school_tier", {}),
            # 经验背景评分配置
            experience_dimension_weights=data.get("experience_dimension_weights", {}),
            degree_scores=data.get("degree_scores", {}),
            school_tier_scores=data.get("school_tier_scores", {}),
            cs_related_majors=data.get("cs_related_majors", []),
            # 工作经验评分配置
            work_experience_scoring=data.get("work_experience_scoring", {}),
            # 实习经验评分配置
            internship_scoring=data.get("internship_scoring", {})
            # 注意：项目评分已改用极简评分器（SimpleProjectAnalyzer）
            # 评分规则已内置在代码中，无需额外配置
        )

    def to_yaml(self, path: str) -> None:
        """保存配置到YAML文件"""
        data = {
            "weights": self.weights,
            "school_tier": self.school_tier,
            # 经验背景评分配置
            "experience_dimension_weights": self.experience_dimension_weights,
            "degree_scores": self.degree_scores,
            "school_tier_scores": self.school_tier_scores,
            "cs_related_majors": self.cs_related_majors
            # 注意：项目评分已改用极简评分器（SimpleProjectAnalyzer）
            # 评分规则已内置在代码中，无需额外配置
        }

        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

    def get_school_tier(self, school_name: str) -> str:
        """获取学校层次"""
        for tier, schools in self.school_tier.items():
            if any(s in school_name for s in schools):
                return tier
        return "普通"
