# tools/analysis/experience_analyzer.py
"""经验背景分析工具"""
from typing import Dict, List, Optional
from core.models import CleanedResume, AnalysisResult, WorkExperience, Education
from core.config import ScoreConfig
from tools.analysis.base_analyzer import BaseAnalyzer


class ExperienceAnalyzer(BaseAnalyzer):
    """
    经验背景分析器 - 综合评估教育背景、工作经验和实习经验

    评分结构 (总分100分):
    - 教育背景 (30分): 学历层次(20分) + 学校层次(10分)
    - 工作经验 (60分): 工作年限(60分)
    - 实习经验 (10分): 实习时长(10分)

    所有评分规则均可在 config/scoring.yaml 中配置
    """

    # ============ 默认配置（当配置文件中未指定时使用）============
    DEFAULT_DEGREE_SCORES = {
        "博士": 20, "phd": 20, "ph.d": 20,
        "硕士": 15, "研究生": 15, "master": 15,
        "本科": 10, "学士": 10, "bachelor": 10,
        "大专": 5, "专科": 5, "associate": 5,
    }

    DEFAULT_SCHOOL_TIER_SCORES = {
        "985": 10, "211": 7, "双一流": 8, "普通": 5,
    }

    DEFAULT_CS_RELATED_MAJORS = [
        "计算机", "软件工程", "人工智能", "数据科学", "机器学习",
        "信息安全", "网络工程", "物联网", "数学", "统计",
        "computer", "software", "ai", "data", "machine learning",
        "information", "network", "math", "statistics"
    ]

    def __init__(self, config: ScoreConfig = None, llm=None):
        super().__init__(config)
        self.dimension_name = "experience"
        self.weight = self.config.weights.get("experience", 0.20)
        self.llm = llm  # LLM实例，用于智能专业相关性判断

        # 从配置加载评分规则，如果配置中没有则使用默认值
        self.degree_scores = (
            self.config.degree_scores
            if self.config.degree_scores
            else self.DEFAULT_DEGREE_SCORES
        )

        self.school_tier_scores = (
            self.config.school_tier_scores
            if self.config.school_tier_scores
            else self.DEFAULT_SCHOOL_TIER_SCORES
        )

        self.cs_related_majors = (
            self.config.cs_related_majors
            if self.config.cs_related_majors
            else self.DEFAULT_CS_RELATED_MAJORS
        )

    def get_dimension_name(self) -> str:
        return self.dimension_name

    def get_weight(self) -> float:
        return self.weight

    def analyze(self, resume: CleanedResume) -> AnalysisResult:
        """
        分析经验背景（综合教育背景、工作经验、实习经验）

        Args:
            resume: 清洗后的简历

        Returns:
            AnalysisResult: 分析结果
        """
        work_history = resume.cleaned_data.work_experience
        education = resume.cleaned_data.education

        # 分离实习和工作经历
        internships, work_experience = self._separate_internships_and_work(work_history)

        detail_scores = self._calculate_detail_scores(education, work_experience, internships)
        total_score = self._calculate_total_score(detail_scores)

        return AnalysisResult(
            dimension=self.dimension_name,
            score=total_score,
            detail_scores=detail_scores,
            insights=self._extract_insights(resume, education, work_experience, internships),
            highlights=self._extract_highlights(resume, education, work_experience, internships),
            weaknesses=self._extract_weaknesses(resume, education, work_experience, internships),
            raw_analysis={
                "job_count": len(work_experience),
                "internship_count": len(internships),
                "education_count": len(education)
            }
        )

    def _separate_internships_and_work(self, work_history: List[WorkExperience]) -> tuple:
        """
        分离实习经历和工作经历

        判断标准：
        1. 职位名称包含"实习"、"intern"
        2. 时长小于6个月

        Args:
            work_history: 所有经历列表

        Returns:
            (实习经历列表, 工作经历列表)
        """
        internships = []
        work = []

        for exp in work_history:
            # 判断是否为实习
            is_internship = (
                "实习" in exp.position.lower() or
                "intern" in exp.position.lower() or
                self._calculate_experience_months(exp) < 6
            )

            if is_internship:
                internships.append(exp)
            else:
                work.append(exp)

        return internships, work

    def _calculate_detail_scores(
        self,
        education: List[Education],
        work_experience: List[WorkExperience],
        internships: List[WorkExperience]
    ) -> Dict[str, float]:
        """
        计算详细得分（教育背景 + 工作经验 + 实习经验）

        Returns:
            Dict: {
                "教育背景_学历层次": X,
                "教育背景_学校层次": X,
                "工作经验_年限": X,
                "工作经验_公司质量": X,
                "工作经验_职位级别": X,
                "工作经验_职业发展": X,
                "实习经验_质量": X,
                "实习经验_时长": X
            }
        """
        detail_scores = {}

        # 1. 教育背景 (30分)
        edu_scores = self._calculate_education_scores(education)
        detail_scores.update(edu_scores)

        # 2. 工作经验 (60分)
        work_scores = self._calculate_work_experience_scores(work_experience)
        detail_scores.update(work_scores)

        # 3. 实习经验 (10分)
        internship_scores = self._calculate_internship_scores(internships)
        detail_scores.update(internship_scores)

        return detail_scores

    def _calculate_total_score(self, detail_scores: Dict[str, float]) -> float:
        """
        计算总分（使用配置的权重 + 归一化到0-100）

        权重配置（experience_dimension_weights）:
        - education: 0.50 (教育背景 50%)
        - work: 0.50 (工作经验 50%)
        - internship: 0.01 (实习经验 1%)

        归一化处理：
        理论最高分从配置文件动态计算
        实际得分 = (原始得分 / 理论最高分) × 100
        """
        # 按维度分组计算总分
        dimension_sums = {
            "education": 0,
            "work": 0,
            "internship": 0
        }

        # 教育背景字段
        education_fields = ["教育背景_学历层次", "教育背景_学校层次"]
        for field in education_fields:
            dimension_sums["education"] += detail_scores.get(field, 0)

        # 工作经验字段
        work_fields = ["工作经验_年限"]
        for field in work_fields:
            dimension_sums["work"] += detail_scores.get(field, 0)

        # 实习经验字段
        internship_fields = ["实习经验_时长"]
        for field in internship_fields:
            dimension_sums["internship"] += detail_scores.get(field, 0)

        # 获取配置的权重
        weights = self.config.experience_dimension_weights

        # 计算加权总分（原始得分）
        weighted_total = (
            dimension_sums["education"] * weights.get("education", 0.50) +
            dimension_sums["work"] * weights.get("work", 0.50) +
            dimension_sums["internship"] * weights.get("internship", 0.01)
        )

        # ✅ 从配置文件动态计算理论最高分
        # 教育背景：最高学历 + 最高学校
        max_degree = max(self.degree_scores.values()) if self.degree_scores else 40
        max_school = max(self.school_tier_scores.values()) if self.school_tier_scores else 20
        max_education = max_degree + max_school

        # 工作经验：从配置读取
        work_scoring = self.config.work_experience_scoring
        max_work = work_scoring.get("max_score", 60)

        # 实习经验：从配置读取
        internship_scoring = self.config.internship_scoring
        max_internship = internship_scoring.get("max_score", 10)

        # 计算理论最高分（用于归一化）
        max_possible = (
            max_education * weights.get("education", 0.50) +
            max_work * weights.get("work", 0.50) +
            max_internship * weights.get("internship", 0.01)
        )

        # 归一化到0-100范围
        if max_possible > 0:
            normalized_total = (weighted_total / max_possible) * 100
        else:
            normalized_total = 0

        return round(min(normalized_total, 100), 2)

    # ============ 教育背景评分 ============

    def _calculate_education_scores(self, education: List[Education]) -> Dict[str, float]:
        """
        计算教育背景得分 (30分)

        - 学历层次 (20分)
        - 学校层次 (10分)
        """
        if not education:
            return {
                "教育背景_学历层次": 0,
                "教育背景_学校层次": 0
            }

        # 取最高学历
        highest_edu = self._get_highest_education(education)

        # 1. 学历层次得分 (20分)
        degree_score = self._calculate_degree_score(highest_edu.degree)

        # 2. 学校层次得分 (10分)
        school_score = self._calculate_school_score(highest_edu.school)

        return {
            "教育背景_学历层次": round(degree_score, 2),
            "教育背景_学校层次": round(school_score, 2)
        }

    def _get_highest_education(self, education: List[Education]) -> Education:
        """获取最高学历"""
        if not education:
            return None

        # 按学历层次排序
        degree_order = {"博士": 4, "硕士": 3, "本科": 2, "大专": 1}
        sorted_edu = sorted(
            education,
            key=lambda e: degree_order.get(e.degree.replace("学位", "").replace("生", ""), 0),
            reverse=True
        )
        return sorted_edu[0]

    def _calculate_degree_score(self, degree: str) -> float:
        """
        计算学历层次得分 (20分)

        - 博士: 20分
        - 硕士: 15分
        - 本科: 10分
        - 大专: 5分
        """
        if not degree:
            return 0

        degree_lower = degree.lower().replace("学位", "").replace("生", "").strip()

        # 精确匹配
        if degree_lower in self.degree_scores:
            return self.degree_scores[degree_lower]

        # 模糊匹配
        for key, value in self.degree_scores.items():
            if key in degree_lower or degree_lower in key:
                return value

        return 0

    def _calculate_school_score(self, school: str) -> float:
        """
        计算学校层次得分（根据配置文件动态评分）

        支持的层次（从配置文件读取）：
        - 985/双一流: 20分
        - 211: 15分
        - 普通本科: 10分
        - 专科: 5分（可扩展）
        """
        if not school:
            return 0

        # 使用配置文件中的学校分级
        if self.config and self.config.school_tier:
            tier = self.config.get_school_tier(school)  # 返回 "985"/"211"/"专科"/"普通"

            # ✅ 修复：使用实际的 tier 从配置中获取分数（支持任意自定义层次）
            if tier in self.school_tier_scores:
                return self.school_tier_scores[tier]
            # 兼容 YAML 可能解析为整数的情况
            elif isinstance(tier, str) and tier.isdigit() and int(tier) in self.school_tier_scores:
                return self.school_tier_scores[int(tier)]

        # 默认返回"普通"的分数
        return self.school_tier_scores.get("普通", 5)

    # ============ 工作经验评分 ============

    def _calculate_work_experience_scores(self, work_experience: List[WorkExperience]) -> Dict[str, float]:
        """
        计算工作经验得分（从配置文件读取评分规则）

        默认配置：
        - 每年 10 分
        - 最高 60 分（6年封顶）
        """
        if not work_experience:
            return {
                "工作经验_年限": 0
            }

        # 从配置文件读取评分规则
        scoring_config = self.config.work_experience_scoring
        score_per_year = scoring_config.get("score_per_year", 10)
        max_score = scoring_config.get("max_score", 60)
        cap_years = scoring_config.get("cap_years", 6)

        # 工作年限评分
        total_months = self._calculate_total_work_months(work_experience)
        years = total_months / 12
        years_score = min(years * score_per_year, max_score)

        return {
            "工作经验_年限": round(years_score, 2)
        }

    # ============ 实习经验评分 ============

    def _calculate_internship_scores(self, internships: List[WorkExperience]) -> Dict[str, float]:
        """
        计算实习经验得分 (10分) - 简化版

        - 实习时长 (10分): 每3个月2.5分，最高10分（12个月以上）
        """
        if not internships:
            return {
                "实习经验_时长": 0
            }

        # 实习时长 (10分)
        duration_score = self._calculate_internship_duration_score(internships)

        return {
            "实习经验_时长": round(duration_score, 2)
        }

    def _calculate_internship_duration_score(self, internships: List[WorkExperience]) -> float:
        """
        计算实习时长得分（从配置文件读取评分规则）

        默认配置：
        - 每月 0.83 分（10分/12月）
        - 最高 10 分（12个月封顶）
        """
        # 从配置文件读取评分规则
        scoring_config = self.config.internship_scoring
        score_per_month = scoring_config.get("score_per_month", 0.83)
        max_score = scoring_config.get("max_score", 10)
        cap_months = scoring_config.get("cap_months", 12)

        total_months = sum(self._calculate_experience_months(exp) for exp in internships)
        score = total_months * score_per_month
        return min(score, max_score)

    def _calculate_total_work_months(self, work_experience: List[WorkExperience]) -> int:
        """计算总工作月数（仅工作经历，不包括实习）"""
        total = 0
        for exp in work_experience:
            total += self._calculate_experience_months(exp)
        return total

    def _calculate_experience_months(self, exp: WorkExperience) -> int:
        """计算单个经历的月数"""
        if not exp.start_time or exp.start_time == "未知时间":
            return 0

        try:
            start_parts = exp.start_time.split("-")
            start_year = int(start_parts[0])
            start_month = int(start_parts[1])

            if exp.end_time == "至今":
                from datetime import datetime
                end_year = datetime.now().year
                end_month = datetime.now().month
            elif exp.end_time:
                end_parts = exp.end_time.split("-")
                end_year = int(end_parts[0])
                end_month = int(end_parts[1])
            else:
                return 0

            months = (end_year - start_year) * 12 + (end_month - start_month)
            return max(months, 0)
        except (ValueError, IndexError):
            return 0

    def _extract_insights(
        self,
        resume: CleanedResume,
        education: List[Education],
        work_experience: List[WorkExperience],
        internships: List[WorkExperience]
    ) -> List[str]:
        """提取关键发现"""
        insights = []

        # 教育背景
        if education:
            highest_edu = self._get_highest_education(education)
            insights.append(f"最高学历：{highest_edu.degree} - {highest_edu.school}")

            # 211/985学校
            if self.config and self.config.school_tier:
                tier = self.config.get_school_tier(highest_edu.school)
                if tier in ["985", "211"]:
                    insights.append(f"毕业于{tier}院校")
        else:
            insights.append("未提供教育背景信息")

        # 工作经验
        if work_experience:
            total_months = self._calculate_total_work_months(work_experience)
            years = total_months // 12
            insights.append(f"工作经验约 {years} 年")

            if len(work_experience) >= 3:
                insights.append(f"有 {len(work_experience)} 段工作经历")
        else:
            insights.append("无正式工作经验")

        # 实习经验
        if internships:
            insights.append(f"有 {len(internships)} 段实习经历")
        elif not work_experience:
            insights.append("无实习或工作经验")

        return insights

    def _extract_highlights(
        self,
        resume: CleanedResume,
        education: List[Education],
        work_experience: List[WorkExperience],
        internships: List[WorkExperience]
    ) -> List[str]:
        """提取亮点"""
        highlights = []

        # 教育背景亮点
        if education:
            highest_edu = self._get_highest_education(education)
            degree = highest_edu.degree

            # 高学历
            if "博士" in degree or "phd" in degree.lower():
                highlights.append("拥有博士学位")

            # 985/211学校
            if self.config and self.config.school_tier:
                tier = self.config.get_school_tier(highest_edu.school)
                if tier == "985":
                    highlights.append("毕业于985院校")
                elif tier == "211":
                    highlights.append("毕业于211院校")

            # 专业相关性判断（集成JobMatcher的智能判断）
            if highest_edu.major:
                # 尝试使用JobMatcher进行专业相关性判断
                major_relevance = self._check_major_relevance(
                    highest_edu.major,
                    education
                )

                if major_relevance >= 70:
                    highlights.append("专业背景相关")
                elif major_relevance >= 50:
                    highlights.append("专业有一定关联")

        # 工作经验亮点
        if work_experience:
            # 大厂经历
            big_companies = ["阿里", "腾讯", "百度", "字节", "华为", "美团", "京东", "谷歌", "微软", "亚马逊"]
            for exp in work_experience:
                if any(company in exp.company for company in big_companies):
                    highlights.append(f"有 {exp.company} 工作经历")
                    break

            # 管理经验
            for exp in work_experience:
                if any(k in exp.position for k in ["经理", "总监", "主管", "负责人", "lead"]):
                    highlights.append("具有管理经验")
                    break

        # 实习经验亮点
        if internships and not work_experience:
            total_internship_months = sum(self._calculate_experience_months(exp) for exp in internships)
            if total_internship_months >= 6:
                highlights.append("实习经验丰富（6个月以上）")

        return highlights

    def _extract_weaknesses(
        self,
        resume: CleanedResume,
        education: List[Education],
        work_experience: List[WorkExperience],
        internships: List[WorkExperience]
    ) -> List[str]:
        """提取不足"""
        weaknesses = []

        # 教育背景不足
        if not education:
            weaknesses.append("缺少教育背景信息")
        else:
            highest_edu = self._get_highest_education(education)
            degree_score = self._calculate_degree_score(highest_edu.degree)
            if degree_score < 10:
                weaknesses.append("学历层次有待提升")

        # 工作经验不足
        if not work_experience and not internships:
            weaknesses.append("缺少实习或工作经验")
            return weaknesses

        if work_experience:
            total_months = self._calculate_total_work_months(work_experience)
            if total_months < 12:
                weaknesses.append("工作经验不足1年")

            # 频繁跳槽
            if len(work_experience) >= 4:
                weaknesses.append("工作经历较为频繁")
        elif internships:
            # 仅有实习经验
            total_internship_months = sum(self._calculate_experience_months(exp) for exp in internships)
            if total_internship_months < 3:
                weaknesses.append("实习经验较短（少于3个月）")

        return weaknesses

    def _check_major_relevance(
        self,
        major: str,
        education: List[Education],
        job_requirements: str = ""
    ) -> float:
        """
        检查专业相关性（集成JobMatcher的智能判断）

        Args:
            major: 专业名称
            education: 教育背景列表
            job_requirements: 岗位要求（可选，如果没有提供则使用默认IT岗位要求）

        Returns:
            专业相关性分数（0-100）
        """
        try:
            # 延迟导入避免循环依赖
            from tools.matching import LLMJobMatcher

            # 构建简历数据
            resume_data = {
                "education": [
                    {
                        "degree": edu.degree,
                        "major": edu.major,
                        "school": edu.school
                    }
                    for edu in education
                ]
            }

            # 如果没有提供岗位要求，使用默认的IT岗位要求
            if not job_requirements:
                job_requirements = (
                    "岗位职责：负责软件系统的设计、开发和维护。"
                    "技能要求：Java, Python, JavaScript, 数据库, 算法, 数据结构。"
                )

            # 创建 LLM 匹配器
            matcher = LLMJobMatcher(self.llm)

            # 调用LLM进行匹配分析
            match_result = matcher.match_resume_to_job(
                resume_data=resume_data,
                job_requirements=job_requirements
            )

            # 从 education_analysis 中提取专业相关性
            edu_analysis = match_result.get("education_analysis", {})
            if edu_analysis.get("major_match"):
                # 专业匹配，返回较高分数
                return 85.0
            elif match_result.get("match_score", 0) >= 60:
                # 整体匹配度尚可
                return match_result.get("match_score", 60) * 0.8
            else:
                # 默认分数
                return 50.0

        except Exception as e:
            # 如果调用失败，降级到原有的关键词判断
            print(f"[WARNING] LLM专业相关性判断失败: {e}，降级到关键词判断")
            return self._check_major_relevance_with_keywords(major)

    def _check_major_relevance_with_keywords(self, major: str) -> float:
        """
        使用关键词判断专业相关性（降级方案）

        Args:
            major: 专业名称

        Returns:
            专业相关性分数（0-100）
        """
        if not major:
            return 50.0

        major_lower = major.lower()

        # 检查是否是CS相关专业
        if any(cs in major_lower for cs in self.cs_related_majors):
            return 80.0

        # 检查是否是通用理工科专业
        general_stem = ["数学", "物理", "化学", "生物", "统计", "math", "physics", "statistics"]
        if any(stem in major_lower for stem in general_stem):
            return 60.0

        # 默认给中等分
        return 50.0
