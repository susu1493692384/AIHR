# tools/analysis/technical_analyzer.py
"""技术能力分析工具"""
from typing import Dict, List, Optional
from core.models import CleanedResume, AnalysisResult, Skill
from core.config import ScoreConfig
from tools.analysis.base_analyzer import BaseAnalyzer


class TechnicalAnalyzer(BaseAnalyzer):
    """技术能力分析器"""

    # 技能等级对应的基础分
    LEVEL_SCORES = {
        "精通": 80,
        "熟练": 60,
        "熟悉": 40,
        "了解": 20,
    }

    # 熟练度权重（重要程度）
    LEVEL_WEIGHTS = {
        "精通": 1.5,  # 核心技能，权重最高
        "熟练": 1.0,  # 主要技能
        "熟悉": 0.7,  # 可用技能
        "了解": 0.5,  # 入门技能
    }

    def __init__(self, config: ScoreConfig = None):
        """
        初始化技术能力分析器

        Args:
            config: 评分配置
        """
        super().__init__(config)
        self.dimension_name = "technical"
        self.weight = self.config.weights.get("technical", 0.25)

    def get_dimension_name(self) -> str:
        """获取分析维度名称"""
        return self.dimension_name

    def get_weight(self) -> float:
        """获取该维度的权重"""
        return self.weight

    def analyze(self, resume: CleanedResume) -> AnalysisResult:
        """
        分析技术能力（按熟练度加权平均）

        Args:
            resume: 清洗后的简历

        Returns:
            AnalysisResult: 分析结果
        """
        skills = resume.cleaned_data.skills

        # 1. 计算展示维度（用于诊断分析）
        detail_scores = self._calculate_detail_scores(skills)

        # 2. 计算总分（按熟练度加权平均）
        total_score, skill_breakdown = self._calculate_total_score(skills)

        # 3. 提取关键发现（规则）
        insights = self._extract_insights(resume)

        # 4. 提取亮点（规则）
        highlights = self._extract_highlights(resume)

        # 5. 提取不足（规则）
        weaknesses = self._extract_weaknesses(resume)

        return AnalysisResult(
            dimension=self.dimension_name,
            score=total_score,
            detail_scores=detail_scores,
            insights=insights,
            highlights=highlights,
            weaknesses=weaknesses,
            raw_analysis={
                "skill_count": len(skills),
                "skill_breakdown": skill_breakdown
            }
        )

    def _calculate_detail_scores(self, skills: List[Skill]) -> Dict[str, any]:
        """
        计算展示维度（用于诊断分析，不参与总分计算）

        Args:
            skills: 技能列表

        Returns:
            Dict: 展示维度统计信息
        """
        if not skills:
            return {
                "技能总数": 0,
                "精通": 0,
                "熟练": 0,
                "熟悉": 0,
                "了解": 0,
                "验证技能": 0,
                "验证比例": "0%"
            }

        # 1. 技能总数
        total_count = len(skills)

        # 2. 熟练等级分布
        level_distribution = {
            "精通": 0,
            "熟练": 0,
            "熟悉": 0,
            "了解": 0
        }
        for skill in skills:
            level = skill.level if skill.level in level_distribution else "了解"
            level_distribution[level] += 1

        # 3. 验证技能统计
        verified_skills = [s for s in skills if s.verified]
        verified_count = len(verified_skills)
        verified_ratio = f"{int(verified_count / total_count * 100)}%" if total_count > 0 else "0%"

        return {
            "技能总数": total_count,
            "精通": level_distribution["精通"],
            "熟练": level_distribution["熟练"],
            "熟悉": level_distribution["熟悉"],
            "了解": level_distribution["了解"],
            "验证技能": verified_count,
            "验证比例": verified_ratio
        }

    def _calculate_total_score(self, skills: List[Skill]) -> tuple[float, Dict]:
        """
        计算总分（按熟练度加权平均）

        计算公式：
        - 每个技能的加权分 = 技能等级分 × 熟练度权重
        - 总分 = (所有技能的加权分之和 / 所有权重之和) / 最高分 × 100

        Args:
            skills: 技能列表

        Returns:
            tuple[float, Dict]: (总分, 技能得分明细)
        """
        if not skills:
            return 0.0, {}

        # 计算加权总和
        weighted_sum = 0.0
        weight_sum = 0.0
        skill_breakdown = []

        for skill in skills:
            level_score = self.LEVEL_SCORES.get(skill.level, 40)
            weight = self.LEVEL_WEIGHTS.get(skill.level, 0.7)

            weighted_score = level_score * weight
            weighted_sum += weighted_score
            weight_sum += weight

            skill_breakdown.append({
                "name": skill.name,
                "level": skill.level,
                "level_score": level_score,
                "weight": weight,
                "weighted_score": round(weighted_score, 2)
            })

        # 计算加权平均分
        avg_weighted_score = weighted_sum / weight_sum if weight_sum > 0 else 0

        # 归一化到 0-100
        # 最高分是精通（80分），所以满分是80
        max_score = 80
        final_score = (avg_weighted_score / max_score * 100) if max_score > 0 else 0

        return round(min(final_score, 100), 2), {
            "skills": skill_breakdown,
            "weighted_sum": round(weighted_sum, 2),
            "weight_sum": round(weight_sum, 2),
            "avg_weighted_score": round(avg_weighted_score, 2)
        }

    def _extract_insights(self, resume: CleanedResume) -> List[str]:
        """提取关键发现"""
        insights = []
        skills = resume.cleaned_data.skills

        if not skills:
            insights.append("未发现明确的技能信息")
            return insights

        # 技能数量
        if len(skills) >= 5:
            insights.append(f"技能覆盖面广，共掌握 {len(skills)} 项技能")
        elif len(skills) >= 3:
            insights.append(f"技能覆盖适中，共掌握 {len(skills)} 项技能")
        else:
            insights.append(f"技能数量较少，仅 {len(skills)} 项")

        # 技能熟练度
        advanced_skills = [s for s in skills if s.level in ["精通", "熟练"]]
        if advanced_skills:
            insights.append(f"有 {len(advanced_skills)} 项技能达到熟练以上水平")

        return insights

    def _extract_highlights(self, resume: CleanedResume) -> List[str]:
        """提取亮点"""
        highlights = []
        skills = resume.cleaned_data.skills

        # 精通技能
        expert_skills = [s for s in skills if s.level == "精通"]
        if expert_skills:
            names = [s.name for s in expert_skills]
            highlights.append(f"精通 {', '.join(names)}")

        # 验证过的技能
        verified_skills = [s for s in skills if s.verified]
        if verified_skills and len(verified_skills) >= 3:
            highlights.append(f"有 {len(verified_skills)} 项技能在实际项目中得到验证")

        return highlights

    def _extract_weaknesses(self, resume: CleanedResume) -> List[str]:
        """提取不足"""
        weaknesses = []
        skills = resume.cleaned_data.skills

        if not skills:
            weaknesses.append("技能信息缺失")
            return weaknesses

        # 技能数量少
        if len(skills) < 3:
            weaknesses.append("技能数量偏少，建议扩展技术栈")

        # 初级技能多
        beginner_skills = [s for s in skills if s.level == "了解"]
        if len(beginner_skills) > len(skills) * 0.5:
            weaknesses.append("多数技能处于了解水平，建议深入学习")

        return weaknesses
