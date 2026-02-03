# tools/cleaning/missing_value_handler.py
"""缺失值处理工具"""
from typing import Optional, List, Dict, Any
from core.models import PersonalInfo, Education, WorkExperience, Project, Skill


class MissingValueHandler:
    """缺失值处理工具类"""

    # 默认填充值
    DEFAULT_VALUES = {
        "name": "未知",
        "school": "未知学校",
        "major": "未知专业",
        "company": "未知公司",
        "position": "未知职位",
        "project_name": "未知项目",
        "skill_name": "未知技能",
        "phone": "未填写",
        "email": "未填写",
        "location": "未填写",
        "description": "",
    }

    @staticmethod
    def handle(resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理简历数据中的缺失值（通用方法）

        Args:
            resume_data: 简历数据字典

        Returns:
            处理后的简历数据
        """
        if not resume_data or not isinstance(resume_data, dict):
            return resume_data

        # 处理个人信息
        if "personal_info" in resume_data and isinstance(resume_data["personal_info"], dict):
            resume_data["personal_info"] = MissingValueHandler._handle_personal_info_dict(
                resume_data["personal_info"]
            )

        # 处理教育经历
        if "education" in resume_data and isinstance(resume_data["education"], list):
            resume_data["education"] = [
                MissingValueHandler._handle_education_dict(edu)
                for edu in resume_data["education"]
            ]

        # 处理工作经历
        if "work_experience" in resume_data and isinstance(resume_data["work_experience"], list):
            resume_data["work_experience"] = [
                MissingValueHandler._handle_work_experience_dict(work)
                for work in resume_data["work_experience"]
            ]

        # 处理项目经验
        if "projects" in resume_data and isinstance(resume_data["projects"], list):
            resume_data["projects"] = [
                MissingValueHandler._handle_project_dict(proj)
                for proj in resume_data["projects"]
            ]

        # 处理技能
        if "skills" in resume_data and isinstance(resume_data["skills"], list):
            # 过滤掉无效的技能
            resume_data["skills"] = [
                skill for skill in resume_data["skills"]
                if skill and (isinstance(skill, dict) and skill.get("name"))
            ]

            resume_data["skills"] = [
                MissingValueHandler._handle_skill_dict(skill)
                for skill in resume_data["skills"]
            ]

        return resume_data

    @staticmethod
    def _handle_personal_info_dict(info: Dict[str, Any]) -> Dict[str, Any]:
        """处理个人信息字典的缺失值"""
        if not info:
            return {"name": MissingValueHandler.DEFAULT_VALUES["name"]}

        result = {}
        for key, default_value in [
            ("name", "未知"),
            ("phone", "未填写"),
            ("email", "未填写"),
            ("location", "未填写"),
        ]:
            value = info.get(key)
            if not value or (isinstance(value, str) and not value.strip()):
                result[key] = default_value
            else:
                result[key] = value.strip() if isinstance(value, str) else value

        # 保留其他字段
        for key in ["birth_date", "gender"]:
            if key in info and info[key]:
                result[key] = info[key]

        return result

    @staticmethod
    def _handle_education_dict(edu: Dict[str, Any]) -> Dict[str, Any]:
        """处理教育经历字典的缺失值"""
        if not edu:
            return None

        result = {}
        for key, default_value in [
            ("school", "未知学校"),
            ("major", "未知专业"),
            ("degree", "未知"),
            ("start_time", "未知时间"),
        ]:
            value = edu.get(key)
            if not value or (isinstance(value, str) and not value.strip()):
                result[key] = default_value
            else:
                result[key] = value.strip() if isinstance(value, str) else value

        # 保留其他字段
        for key in ["end_time", "gpa", "description"]:
            if key in edu:
                value = edu[key]
                if key == "end_time" and not value:
                    result[key] = None
                elif key == "gpa" and not value:
                    result[key] = None
                elif key == "description" and not value:
                    result[key] = ""
                else:
                    result[key] = value

        return result

    @staticmethod
    def _handle_work_experience_dict(work: Dict[str, Any]) -> Dict[str, Any]:
        """处理工作经历字典的缺失值"""
        if not work:
            return None

        result = {}
        for key, default_value in [
            ("company", "未知公司"),
            ("position", "未知职位"),
            ("start_time", "未知时间"),
        ]:
            value = work.get(key)
            if not value or (isinstance(value, str) and not value.strip()):
                result[key] = default_value
            else:
                result[key] = value.strip() if isinstance(value, str) else value

        # 保留其他字段
        for key in ["end_time", "industry", "company_scale", "description"]:
            if key in work:
                value = work[key]
                if key in ["end_time", "industry", "company_scale"] and not value:
                    result[key] = None
                elif key == "description" and not value:
                    result[key] = ""
                else:
                    result[key] = value

        # 处理achievements
        if "achievements" in work:
            achievements = work["achievements"]
            if isinstance(achievements, list):
                result["achievements"] = [a for a in achievements if a]
            else:
                result["achievements"] = []
        else:
            result["achievements"] = []

        return result

    @staticmethod
    def _handle_project_dict(proj: Dict[str, Any]) -> Dict[str, Any]:
        """处理项目经验字典的缺失值"""
        if not proj:
            return None

        result = {}
        for key, default_value in [
            ("name", "未知项目"),
            ("role", "未知角色"),
            ("start_time", "未知时间"),
        ]:
            value = proj.get(key)
            if not value or (isinstance(value, str) and not value.strip()):
                result[key] = default_value
            else:
                result[key] = value.strip() if isinstance(value, str) else value

        # 保留其他字段
        for key in ["end_time", "team_size", "description"]:
            if key in proj:
                value = proj[key]
                if key in ["end_time", "team_size"] and not value:
                    result[key] = None
                elif key == "description" and not value:
                    result[key] = ""
                else:
                    result[key] = value

        # 处理tech_stack
        if "tech_stack" in proj:
            tech_stack = proj["tech_stack"]
            if isinstance(tech_stack, list):
                result["tech_stack"] = [t for t in tech_stack if t]
            elif isinstance(tech_stack, str):
                result["tech_stack"] = [tech_stack] if tech_stack.strip() else []
            else:
                result["tech_stack"] = []
        else:
            result["tech_stack"] = []

        # 处理achievements
        if "achievements" in proj:
            achievements = proj["achievements"]
            if isinstance(achievements, list):
                result["achievements"] = [a for a in achievements if a]
            else:
                result["achievements"] = []
        else:
            result["achievements"] = []

        # 处理complexity_indicators
        if "complexity_indicators" in proj:
            indicators = proj["complexity_indicators"]
            result["complexity_indicators"] = indicators if isinstance(indicators, dict) else {}
        else:
            result["complexity_indicators"] = {}

        return result

    @staticmethod
    def _handle_skill_dict(skill: Dict[str, Any]) -> Dict[str, Any]:
        """处理技能字典的缺失值"""
        if not skill or not skill.get("name"):
            return None

        result = {"name": skill["name"].strip()}

        # 处理category
        if "category" in skill and skill["category"]:
            result["category"] = skill["category"]
        else:
            result["category"] = "other"

        # 处理level
        if "level" in skill and skill["level"]:
            result["level"] = skill["level"]
        else:
            result["level"] = "了解"

        # 保留其他字段
        for key in ["verified"]:
            if key in skill:
                result[key] = skill[key]

        return result

    @staticmethod
    def fill_personal_info(info: PersonalInfo) -> PersonalInfo:
        """
        填充个人信息的缺失值

        Args:
            info: 原始个人信息

        Returns:
            PersonalInfo: 填充后的个人信息
        """
        if not info:
            return PersonalInfo(name=MissingValueHandler.DEFAULT_VALUES["name"])

        return PersonalInfo(
            name=info.name if info.name else MissingValueHandler.DEFAULT_VALUES["name"],
            phone=info.phone if info.phone else MissingValueHandler.DEFAULT_VALUES["phone"],
            email=info.email if info.email else MissingValueHandler.DEFAULT_VALUES["email"],
            location=info.location if info.location else MissingValueHandler.DEFAULT_VALUES["location"],
            birth_date=info.birth_date,
            gender=info.gender
        )

    @staticmethod
    def fill_education(edu: Education) -> Education:
        """
        填充教育经历的缺失值

        Args:
            edu: 原始教育经历

        Returns:
            Education: 填充后的教育经历
        """
        if not edu:
            return None

        return Education(
            school=edu.school if edu.school else MissingValueHandler.DEFAULT_VALUES["school"],
            major=edu.major if edu.major else MissingValueHandler.DEFAULT_VALUES["major"],
            degree=edu.degree if edu.degree else "未知",
            start_time=edu.start_time if edu.start_time else "未知时间",
            end_time=edu.end_time,
            gpa=edu.gpa,
            description=edu.description
        )

    @staticmethod
    def fill_work_experience(exp: WorkExperience) -> WorkExperience:
        """
        填充工作经历的缺失值

        Args:
            exp: 原始工作经历

        Returns:
            WorkExperience: 填充后的工作经历
        """
        if not exp:
            return None

        return WorkExperience(
            company=exp.company if exp.company else MissingValueHandler.DEFAULT_VALUES["company"],
            position=exp.position if exp.position else MissingValueHandler.DEFAULT_VALUES["position"],
            start_time=exp.start_time if exp.start_time else "未知时间",
            end_time=exp.end_time,
            industry=exp.industry,
            company_scale=exp.company_scale,
            description=exp.description,
            achievements=exp.achievements if exp.achievements else []
        )

    @staticmethod
    def fill_project(proj: Project) -> Project:
        """
        填充项目经验的缺失值

        Args:
            proj: 原始项目经验

        Returns:
            Project: 填充后的项目经验
        """
        if not proj:
            return None

        return Project(
            name=proj.name if proj.name else MissingValueHandler.DEFAULT_VALUES["project_name"],
            role=proj.role if proj.role else "未知角色",
            start_time=proj.start_time if proj.start_time else "未知时间",
            end_time=proj.end_time,
            team_size=proj.team_size,
            tech_stack=proj.tech_stack if proj.tech_stack else [],
            description=proj.description,
            achievements=proj.achievements if proj.achievements else [],
            complexity_indicators=proj.complexity_indicators if proj.complexity_indicators else {}
        )

    @staticmethod
    def fill_skill(skill: Skill) -> Skill:
        """
        填充技能的缺失值

        Args:
            skill: 原始技能

        Returns:
            Skill: 填充后的技能
        """
        if not skill:
            return None

        return Skill(
            name=skill.name if skill.name else MissingValueHandler.DEFAULT_VALUES["skill_name"],
            level=skill.level if skill.level else "了解",
            verified=skill.verified
        )

    @staticmethod
    def validate_personal_info(info: PersonalInfo) -> bool:
        """
        验证个人信息的必填字段

        Args:
            info: 个人信息

        Returns:
            bool: 是否有效
        """
        if not info:
            return False

        # 姓名是必填的
        if not info.name or info.name.strip() == "":
            return False

        return True

    @staticmethod
    def validate_education(edu: Education) -> bool:
        """
        验证教育经历的必填字段

        Args:
            edu: 教育经历

        Returns:
            bool: 是否有效
        """
        if not edu:
            return False

        # 学校、专业、学位是必填的
        if not edu.school or not edu.major or not edu.degree:
            return False

        return True

    @staticmethod
    def get_missing_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
        """
        获取缺失的字段列表

        Args:
            data: 数据字典
            required_fields: 必填字段列表

        Returns:
            List[str]: 缺失的字段名列表
        """
        missing = []

        for field in required_fields:
            if field not in data or not data[field]:
                missing.append(field)

        return missing

    @staticmethod
    def generate_cleaning_report(original: Any, cleaned: Any) -> Dict[str, Any]:
        """
        生成清洗报告

        Args:
            original: 原始数据
            cleaned: 清洗后数据

        Returns:
            Dict: 清洗报告
        """
        report = {
            "operations": [],
            "fixes": [],
            "warnings": [],
            "missing_fields": []
        }

        # 这里可以根据具体类型比较原始数据和清洗后数据
        # 记录哪些字段被填充、哪些字段被修改等

        return report
