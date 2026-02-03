# tools/analysis/converter.py
"""数据转换工具 - 将 Dict 格式的简历数据转换为新版模型对象"""
from typing import Dict, Any, List, Optional, Set
from core.models import (
    ParsedResume, CleanedResume,
    PersonalInfo, Education, WorkExperience, Project, Skill
)
from core.config import ScoreConfig


def dict_to_parsed_resume(data: Dict[str, Any], config: "ScoreConfig" = None) -> ParsedResume:
    """
    将字典格式的简历数据转换为 ParsedResume 对象

    Args:
        data: 字典格式的简历数据
        config: 评分配置对象（如果为None，自动加载）

    Returns:
        ParsedResume: 解析后的简历对象
    """
    # 加载配置
    if config is None:
        from core.config import ScoreConfig
        config = ScoreConfig.from_yaml("config/scoring.yaml")

    # 个人信息
    personal_info = _parse_personal_info(data.get("personal_info", {}))

    # 教育经历
    education = _parse_education(data.get("education", []))

    # 工作经历
    work_experience = _parse_work_experience(data.get("work_experience", []))

    # 项目经验
    projects = _parse_projects(data.get("projects", []))

    # 收集验证过的技术（用于智能填充）
    verified_techs = _collect_verified_technologies(work_experience, projects)

    # 技能（增强版）
    skills_data = data.get("skills", [])

    # 如果skills为空，从项目中提取技能
    if not skills_data and projects:
        skills_data = _extract_skills_from_projects(projects, config)

    skills = _parse_and_enhance_skills(skills_data, verified_techs, config)

    return ParsedResume(
        file_name=data.get("file_name", ""),
        file_type=data.get("file_type", ""),
        personal_info=personal_info,
        education=education,
        work_experience=work_experience,
        projects=projects,
        skills=skills,
        others=data.get("others", {})
    )


def dict_to_cleaned_resume(data: Dict[str, Any], config: "ScoreConfig" = None) -> CleanedResume:
    """
    将字典格式的简历数据转换为 CleanedResume 对象
    并智能填充 Skill 的 verified 和 market_demand 字段

    Args:
        data: 字典格式的简历数据
        config: 评分配置对象（如果为None，自动加载）

    Returns:
        CleanedResume: 清洗后的简历对象
    """
    # 加载配置
    if config is None:
        from core.config import ScoreConfig
        config = ScoreConfig.from_yaml("config/scoring.yaml")

    # 先转换基础数据
    work_experience = _parse_work_experience(data.get("work_experience", []))
    projects = _parse_projects(data.get("projects", []))

    # 收集所有验证过的技术（从工作经历和项目中）
    verified_techs = _collect_verified_technologies(work_experience, projects)

    # 解析技能并增强
    skills_data = data.get("skills", [])

    # 如果skills为空，从项目中提取技能
    if not skills_data and projects:
        skills_data = _extract_skills_from_projects(projects, config)

    skills = _parse_and_enhance_skills(skills_data, verified_techs, config)

    parsed = ParsedResume(
        file_name=data.get("file_name", ""),
        file_type=data.get("file_type", ""),
        personal_info=_parse_personal_info(data.get("personal_info", {})),
        education=_parse_education(data.get("education", [])),
        work_experience=work_experience,
        projects=projects,
        skills=skills,
        others=data.get("others", {})
    )

    return CleanedResume(
        original=parsed,
        cleaned_data=parsed
    )


def _parse_personal_info(data: Dict[str, Any]) -> Optional[PersonalInfo]:
    """解析个人信息"""
    if not data or not data.get("name"):
        return None
    return PersonalInfo(
        name=data.get("name", ""),
        phone=data.get("phone"),
        email=data.get("email"),
        location=data.get("location"),
        birth_date=data.get("birth_date"),
        gender=data.get("gender")
    )


def _parse_education(data: List[Dict[str, Any]]) -> List[Education]:
    """解析教育经历"""
    if not data:
        return []
    return [
        Education(
            school=item.get("school", ""),
            major=item.get("major", ""),
            degree=item.get("degree", ""),
            start_time=item.get("start_time", ""),
            end_time=item.get("end_time"),
            gpa=item.get("gpa"),
            description=item.get("description")
        )
        for item in data
    ]


def _parse_work_experience(data: List[Dict[str, Any]]) -> List[WorkExperience]:
    """解析工作经历"""
    if not data:
        return []
    return [
        WorkExperience(
            company=item.get("company", ""),
            position=item.get("position", ""),
            start_time=item.get("start_time", ""),
            end_time=item.get("end_time"),
            industry=item.get("industry"),
            company_scale=item.get("company_scale"),
            description=item.get("description", ""),
            achievements=item.get("achievements", [])
        )
        for item in data
    ]


def _parse_projects(data: List[Dict[str, Any]]) -> List[Project]:
    """解析项目经验"""
    if not data:
        return []
    return [
        Project(
            name=item.get("name", ""),
            role=item.get("role", ""),
            start_time=item.get("start_time", ""),
            end_time=item.get("end_time"),
            team_size=item.get("team_size"),
            tech_stack=item.get("tech_stack", []),
            description=item.get("description", ""),
            achievements=item.get("achievements", [])
        )
        for item in data
    ]


def _collect_verified_technologies(
    work_experience: List[WorkExperience],
    projects: List[Project]
) -> Set[str]:
    """
    从工作经历和项目中收集验证过的技术

    Args:
        work_experience: 工作经历列表
        projects: 项目列表

    Returns:
        Set[str]: 验证过的技术名称集合（小写）
    """
    verified = set()

    # 从工作经历描述中提取
    for work in work_experience:
        # 从 tech_stack 中提取（如果有）
        if hasattr(work, 'tech_stack') and work.tech_stack:
            for tech in work.tech_stack:
                verified.add(tech.lower())

        # 从 description 中提取关键词
        description = (work.description or "").lower()

    # 从项目中提取
    for project in projects:
        # 从 tech_stack 中提取
        if project.tech_stack:
            for tech in project.tech_stack:
                verified.add(tech.lower())

        # 从 description 中提取关键词
        description = (project.description or "").lower()

    return verified


def _extract_skills_from_projects(projects: List[Project], config: "ScoreConfig" = None) -> List[Dict[str, Any]]:
    """
    从项目经验中提取技能信息

    当简历中没有单独的技能章节时，从项目的tech_stack中提取技能

    Args:
        projects: 项目列表
        config: 评分配置对象（未使用，保留参数兼容性）

    Returns:
        技能列表，格式: [{"name": "技能名", "level": "熟练度"}]
    """
    if not projects:
        return []

    extracted_skills = {}  # 使用字典去重

    for project in projects:
        # 从tech_stack中提取
        tech_stack = project.tech_stack or []
        for tech in tech_stack:
            if tech and isinstance(tech, str):
                tech_lower = tech.lower().strip()
                if tech_lower and tech_lower not in extracted_skills:
                    extracted_skills[tech_lower] = {
                        "name": tech.strip(),
                        "level": "熟练"  # 项目中使用的技能默认为"熟练"
                    }

    # 转换为列表并按名称排序
    skill_list = list(extracted_skills.values())
    skill_list.sort(key=lambda x: x.get("name", ""))

    return skill_list


def _parse_and_enhance_skills(
    skills_data: List[Dict[str, Any]],
    verified_techs: Set[str],
    config: "ScoreConfig" = None
) -> List[Skill]:
    """
    解析技能列表并智能填充 verified 和 market_demand 字段

    Args:
        skills_data: 原始技能数据列表
        verified_techs: 验证过的技术集合
        config: 评分配置对象（如果为None，自动加载）

    Returns:
        List[Skill]: 增强后的技能列表
    """
    if not skills_data:
        return []

    # 加载配置（如果未提供）
    if config is None:
        try:
            from core.config import ScoreConfig
            config = ScoreConfig.from_yaml("config/scoring.yaml")
        except:
            config = None

    skills = []
    for item in skills_data:
        if not isinstance(item, dict):
            continue

        skill_name = item.get("name", "")
        if not skill_name:
            continue

        # 智能判断 verified：如果在工作经历/项目的tech_stack中出现过，则为True
        verified = item.get("verified", False)
        if not verified and verified_techs:
            verified = skill_name.lower() in verified_techs

        skills.append(Skill(
            name=skill_name,
            level=item.get("level", "了解"),
            verified=verified
        ))

    return skills


def _parse_skills(data: List[Dict[str, Any]]) -> List[Skill]:
    """解析技能"""
    if not data:
        return []
    return [
        Skill(
            name=item.get("name", ""),
            level=item.get("level", "了解"),
            verified=item.get("verified", False)
        )
        for item in data
    ]


def analysis_result_to_dict(result) -> Dict[str, Any]:
    """
    将 AnalysisResult 对象转换为字典格式

    Args:
        result: AnalysisResult 对象

    Returns:
        Dict: 字典格式的分析结果
    """
    return {
        "score": result.score,
        "detail_scores": result.detail_scores,
        "raw_analysis": result.raw_analysis,
        "analysis": {
            "key_findings": result.insights,
            "strengths": result.highlights,
            "weaknesses": result.weaknesses
        },
        "strengths": result.highlights,
        "weaknesses": result.weaknesses,
        "key_findings": result.insights
    }
