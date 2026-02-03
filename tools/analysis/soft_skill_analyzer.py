# tools/analysis/soft_skill_analyzer.py
"""软技能分析工具"""
from typing import Dict, List
from core.models import CleanedResume, AnalysisResult
from core.config import ScoreConfig
from tools.analysis.base_analyzer import BaseAnalyzer


class SoftSkillAnalyzer(BaseAnalyzer):
    """软技能分析器"""

    # 软技能关键词
    SOFT_SKILL_KEYWORDS = {
        "团队协作": ["团队", "协作", "配合", "沟通"],
        "领导力": ["领导", "管理", "带领", "负责", "主管"],
        "沟通能力": ["沟通", "交流", "表达", "协调"],
        "学习能力": ["学习", "掌握", "研究", "探索"],
        "问题解决": ["解决", "优化", "改进", "处理"],
        "创新": ["创新", "改进", "优化", "提出"],
        "抗压": ["压力", "挑战", "应对", "克服"],
    }

    def __init__(self, config: ScoreConfig = None):
        super().__init__(config)
        self.dimension_name = "soft_skill"
        self.weight = self.config.weights.get("soft_skill", 0.15)

    def get_dimension_name(self) -> str:
        return self.dimension_name

    def get_weight(self) -> float:
        return self.weight

    def analyze(self, resume: CleanedResume) -> AnalysisResult:
        """分析软技能"""
        all_text = self._extract_all_text(resume)

        detail_scores = self._calculate_detail_scores(all_text)
        total_score = self._calculate_total_score(all_text)

        return AnalysisResult(
            dimension=self.dimension_name,
            score=total_score,
            detail_scores=detail_scores,
            insights=self._extract_insights(resume),
            highlights=self._extract_highlights(resume),
            weaknesses=self._extract_weaknesses(resume),
            raw_analysis={"soft_skill_keywords_found": len(self._found_skills(all_text))}
        )

    def _calculate_detail_scores(self, text: str) -> Dict[str, float]:
        """计算详细得分"""
        found_skills = self._found_skills(text)

        # 根据找到的软技能数量评分
        skill_count = len(found_skills)
        coverage_score = min(skill_count * 5, 25)

        # 团队协作评分
        teamwork_score = self._calculate_category_score(text, "团队协作")

        # 领导力评分
        leadership_score = self._calculate_category_score(text, "领导力")

        # 沟通能力评分
        communication_score = self._calculate_category_score(text, "沟通能力")

        return {
            "覆盖面": round(coverage_score, 2),
            "团队协作": round(teamwork_score, 2),
            "领导力": round(leadership_score, 2),
            "沟通能力": round(communication_score, 2)
        }

    def _calculate_total_score(self, text: str) -> float:
        """计算总分"""
        detail_scores = self._calculate_detail_scores(text)
        total = sum(detail_scores.values())
        return round(min(total, 100), 2)

    def _found_skills(self, text: str) -> List[str]:
        """找到的软技能列表"""
        found = []
        for skill, keywords in self.SOFT_SKILL_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                found.append(skill)
        return found

    def _calculate_category_score(self, text: str, category: str) -> float:
        """计算某个类别的得分"""
        keywords = self.SOFT_SKILL_KEYWORDS.get(category, [])
        count = sum(1 for kw in keywords if kw in text)
        return min(count * 10, 25)

    def _extract_all_text(self, resume: CleanedResume) -> str:
        """提取所有文本"""
        parts = []

        # 个人信息
        if resume.cleaned_data.personal_info:
            parts.append(resume.cleaned_data.personal_info.name or "")

        # 工作经历描述
        for exp in resume.cleaned_data.work_experience:
            if exp.description:
                parts.append(exp.description)
            if exp.achievements:
                parts.extend(exp.achievements)

        # 项目描述
        for proj in resume.cleaned_data.projects:
            if proj.description:
                parts.append(proj.description)
            if proj.achievements:
                parts.extend(proj.achievements)

        return " ".join(parts)

    def _extract_insights(self, resume: CleanedResume) -> List[str]:
        """提取关键发现"""
        insights = []
        all_text = self._extract_all_text(resume)

        found_skills = self._found_skills(all_text)
        if found_skills:
            insights.append(f"展现出的软技能: {', '.join(found_skills[:3])}")
        else:
            insights.append("软技能信息较少")

        return insights

    def _extract_highlights(self, resume: CleanedResume) -> List[str]:
        """提取亮点"""
        highlights = []
        all_text = self._extract_all_text(resume)

        # 检查领导力相关
        leadership_keywords = self.SOFT_SKILL_KEYWORDS.get("领导力", [])
        if any(kw in all_text for kw in leadership_keywords):
            highlights.append("展现出领导潜质")

        # 检查团队协作
        teamwork_keywords = self.SOFT_SKILL_KEYWORDS.get("团队协作", [])
        teamwork_count = sum(1 for kw in teamwork_keywords if kw in all_text)
        if teamwork_count >= 2:
            highlights.append("强调团队协作能力")

        return highlights

    def _extract_weaknesses(self, resume: CleanedResume) -> List[str]:
        """提取不足"""
        weaknesses = []
        all_text = self._extract_all_text(resume)

        found_skills = self._found_skills(all_text)

        if len(found_skills) < 3:
            weaknesses.append("软技能描述较为缺乏")

        # 检查是否有具体描述
        if len(all_text) < 100:
            weaknesses.append("经历描述较为简短")

        return weaknesses
