# agents/cleaning_agent.py
"""数据清洗Agent"""
import json
from typing import Dict, Any, Optional
from agents.base import BaseAgent
from prompts import prompt_manager
from langchain_core.language_models import BaseChatModel


class CleaningAgent(BaseAgent):
    """数据清洗Agent - 负责清洗和标准化简历数据"""

    def __init__(
        self,
        llm: BaseChatModel,
        verbose: bool = False
    ):
        """
        初始化清洗Agent

        Args:
            llm: 语言模型
            verbose: 是否输出详细信息
        """
        super().__init__(llm, verbose=verbose)

    def get_system_prompt(self) -> str:
        """获取系统Prompt"""
        return prompt_manager.get_system_prompt("cleaning")

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行数据清洗任务（使用工具，不调用LLM）

        Args:
            input_data: 输入数据，包含：
                - resume_data: 简历数据
                - cleaning_steps: 清洗步骤列表（可选）

        Returns:
            清洗结果，包含：
                - success: 是否成功
                - cleaned_data: 清洗后的数据
                - cleaning_report: 清洗报告
                - error: 错误信息（如果失败）
        """
        if not self.validate_input(input_data):
            return {
                "success": False,
                "error": "Invalid input data"
            }

        try:
            resume_data = input_data.get("resume_data")

            if not resume_data:
                return {
                    "success": False,
                    "error": "No resume data provided"
                }

            # 使用工具直接清洗，不调用LLM
            cleaning_report = {}

            # 1. 日期标准化
            normalized_count = self._count_and_normalize_dates(resume_data)
            if normalized_count > 0:
                cleaning_report["normalized_dates"] = normalized_count

            # 2. 文本清洗
            cleaned_fields = self._count_and_clean_text(resume_data)
            if cleaned_fields > 0:
                cleaning_report["cleaned_text_fields"] = cleaned_fields

            # 3. 缺失值处理
            filled_count = self._handle_missing_values(resume_data)
            if filled_count > 0:
                cleaning_report["filled_missing_values"] = filled_count

            return {
                "success": True,
                "cleaned_data": resume_data,
                "cleaning_report": cleaning_report,
                "agent_name": "CleaningAgent"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent_name": "CleaningAgent"
            }

    def _count_and_normalize_dates(self, resume_data: Dict[str, Any]) -> int:
        """标准化日期并返回处理数量"""
        from tools.cleaning.date_normalizer import DateNormalizer

        normalizer = DateNormalizer()
        count = 0

        # 清洗教育经历日期
        if "education" in resume_data and isinstance(resume_data["education"], list):
            for edu in resume_data["education"]:
                if "start_time" in edu and edu["start_time"]:
                    original = edu["start_time"]
                    normalized = normalizer.normalize(original)
                    if original != normalized:
                        edu["start_time"] = normalized
                        count += 1
                if "end_time" in edu and edu["end_time"]:
                    original = edu["end_time"]
                    normalized = normalizer.normalize(original)
                    if original != normalized:
                        edu["end_time"] = normalized
                        count += 1

        # 清洗工作经历日期
        if "work_experience" in resume_data and isinstance(resume_data["work_experience"], list):
            for work in resume_data["work_experience"]:
                if "start_time" in work and work["start_time"]:
                    original = work["start_time"]
                    normalized = normalizer.normalize(original)
                    if original != normalized:
                        work["start_time"] = normalized
                        count += 1
                if "end_time" in work and work["end_time"]:
                    original = work["end_time"]
                    normalized = normalizer.normalize(original)
                    if original != normalized:
                        work["end_time"] = normalized
                        count += 1

        # 清洗项目日期
        if "projects" in resume_data and isinstance(resume_data["projects"], list):
            for project in resume_data["projects"]:
                if "start_time" in project and project["start_time"]:
                    original = project["start_time"]
                    normalized = normalizer.normalize(original)
                    if original != normalized:
                        project["start_time"] = normalized
                        count += 1
                if "end_time" in project and project["end_time"]:
                    original = project["end_time"]
                    normalized = normalizer.normalize(original)
                    if original != normalized:
                        project["end_time"] = normalized
                        count += 1

        return count

    def _count_and_clean_text(self, resume_data: Dict[str, Any]) -> int:
        """清洗文本并返回处理数量"""
        from tools.cleaning.text_normalizer import TextNormalizer

        normalizer = TextNormalizer()
        count = 0

        def clean_dict(obj):
            nonlocal count
            if isinstance(obj, dict):
                return {k: clean_dict(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_dict(item) for item in obj]
            elif isinstance(obj, str):
                original = obj
                cleaned = normalizer.normalize(obj)
                if original != cleaned:
                    count += 1
                return cleaned
            return obj

        clean_dict(resume_data)
        return count

    def _handle_missing_values(self, resume_data: Dict[str, Any]) -> int:
        """处理缺失值并返回处理数量"""
        from tools.cleaning.missing_value_handler import MissingValueHandler

        handler = MissingValueHandler()

        # 统计缺失值
        missing_count = 0
        if "personal_info" in resume_data and isinstance(resume_data["personal_info"], dict):
            for field in ["name", "email", "phone"]:
                if not resume_data["personal_info"].get(field):
                    missing_count += 1

        # 填充缺失值
        if missing_count > 0:
            resume_data = handler.handle(resume_data)

        return missing_count

    def clean_dates(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        清洗日期数据

        Args:
            resume_data: 简历数据

        Returns:
            清洗后的数据
        """
        from tools.cleaning.date_normalizer import DateNormalizer

        normalizer = DateNormalizer()
        cleaned = resume_data.copy()

        # 清洗教育经历日期
        if "education" in cleaned:
            for edu in cleaned["education"]:
                if "start_time" in edu:
                    edu["start_time"] = normalizer.normalize(edu["start_time"])
                if "end_time" in edu:
                    edu["end_time"] = normalizer.normalize(edu["end_time"])

        # 清洗工作经历日期
        if "work_experience" in cleaned:
            for work in cleaned["work_experience"]:
                if "start_time" in work:
                    work["start_time"] = normalizer.normalize(work["start_time"])
                if "end_time" in work:
                    work["end_time"] = normalizer.normalize(work["end_time"])

        # 清洗项目日期
        if "projects" in cleaned:
            for project in cleaned["projects"]:
                if "start_time" in project:
                    project["start_time"] = normalizer.normalize(project["start_time"])
                if "end_time" in project:
                    project["end_time"] = normalizer.normalize(project["end_time"])

        return cleaned

    def normalize_text(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        规范化文本数据

        Args:
            resume_data: 简历数据

        Returns:
            规范化后的数据
        """
        from tools.cleaning.text_normalizer import TextNormalizer

        normalizer = TextNormalizer()
        cleaned = resume_data.copy()

        # 规范化所有字符串字段
        def normalize_dict(obj):
            if isinstance(obj, dict):
                return {k: normalize_dict(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [normalize_dict(item) for item in obj]
            elif isinstance(obj, str):
                return normalizer.normalize(obj)
            return obj

        return normalize_dict(cleaned)

    def handle_missing_values(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理缺失值

        Args:
            resume_data: 简历数据

        Returns:
            处理后的数据
        """
        from tools.cleaning.missing_value_handler import MissingValueHandler

        handler = MissingValueHandler()
        return handler.handle(resume_data)

    def deduplicate(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        去重数据

        Args:
            resume_data: 简历数据

        Returns:
            去重后的数据
        """
        # 这里可以调用去重工具
        # 暂时返回原数据
        return resume_data


class DeduplicationAgent(BaseAgent):
    """去重Agent - 负责识别和合并重复数据"""

    def __init__(
        self,
        llm: BaseChatModel,
        verbose: bool = False
    ):
        """
        初始化去重Agent

        Args:
            llm: 语言模型
            verbose: 是否输出详细信息
        """
        super().__init__(llm, verbose=verbose)

    def get_system_prompt(self) -> str:
        """获取系统Prompt"""
        return prompt_manager.get_system_prompt("deduplication")

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行去重任务（使用算法，不调用LLM）

        Args:
            input_data: 输入数据，包含：
                - resume_data: 简历数据

        Returns:
            去重结果，包含：
                - success: 是否成功
                - deduplicated_data: 去重后的数据
                - deduplication_report: 去重报告
                - error: 错误信息（如果失败）
        """
        if not self.validate_input(input_data):
            return {
                "success": False,
                "error": "Invalid input data"
            }

        try:
            resume_data = input_data.get("resume_data")

            if not resume_data:
                return {
                    "success": False,
                    "error": "No resume data provided"
                }

            # 使用智能去重工具，不调用LLM
            from tools.cleaning import DataDeduplicator

            # 执行去重
            deduplicated_data, deduplication_report = DataDeduplicator.deduplicate_resume(resume_data)

            # 生成可读的报告文本
            report_text = DataDeduplicator.format_report_for_display(deduplication_report)

            return {
                "success": True,
                "deduplicated_data": deduplicated_data,
                "deduplication_report": deduplication_report,
                "deduplication_report_text": report_text,
                "agent_name": "DeduplicationAgent"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent_name": "DeduplicationAgent"
            }

    def _deduplicate_skills(self, resume_data: Dict[str, Any]) -> int:
        """去重技能（基于相似度）"""
        from difflib import SequenceMatcher

        if "skills" not in resume_data or not isinstance(resume_data["skills"], list):
            return 0

        skills = resume_data["skills"]
        unique_skills = []
        removed_count = 0

        for skill in skills:
            skill_name = skill.get("name", "") if isinstance(skill, dict) else str(skill)
            if not skill_name:
                continue

            # 检查是否与已有技能重复
            is_duplicate = False
            for existing in unique_skills:
                existing_name = existing.get("name", "") if isinstance(existing, dict) else str(existing)
                # 计算相似度
                similarity = SequenceMatcher(None, skill_name.lower(), existing_name.lower()).ratio()
                if similarity > 0.85:  # 相似度阈值85%
                    is_duplicate = True
                    removed_count += 1
                    break

            if not is_duplicate:
                unique_skills.append(skill)

        resume_data["skills"] = unique_skills
        return removed_count

    def _deduplicate_projects(self, resume_data: Dict[str, Any]) -> int:
        """去重项目（基于项目名和描述）"""
        from difflib import SequenceMatcher

        if "projects" not in resume_data or not isinstance(resume_data["projects"], list):
            return 0

        projects = resume_data["projects"]
        unique_projects = []
        removed_count = 0

        for project in projects:
            project_name = project.get("name", "")
            if not project_name:
                continue

            # 检查是否与已有项目重复
            is_duplicate = False
            for existing in unique_projects:
                existing_name = existing.get("name", "")
                # 计算项目名相似度
                similarity = SequenceMatcher(None, project_name.lower(), existing_name.lower()).ratio()
                if similarity > 0.9:  # 项目名相似度阈值90%
                    is_duplicate = True
                    removed_count += 1
                    break

            if not is_duplicate:
                unique_projects.append(project)

        resume_data["projects"] = unique_projects
        return removed_count

    def _deduplicate_work_experience(self, resume_data: Dict[str, Any]) -> int:
        """去重工作经历（基于公司+职位+时间段）"""
        if "work_experience" not in resume_data or not isinstance(resume_data["work_experience"], list):
            return 0

        work_list = resume_data["work_experience"]
        unique_work = []
        removed_count = 0

        for work in work_list:
            company = work.get("company", "")
            position = work.get("position", "")

            # 检查是否完全重复
            is_duplicate = False
            for existing in unique_work:
                if (company and company == existing.get("company", "") and
                    position and position == existing.get("position", "")):
                    is_duplicate = True
                    removed_count += 1
                    break

            if not is_duplicate:
                unique_work.append(work)

        resume_data["work_experience"] = unique_work
        return removed_count

    def _deduplicate_certificates(self, resume_data: Dict[str, Any]) -> int:
        """去重证书"""
        if "certificates" not in resume_data or not isinstance(resume_data["certificates"], list):
            return 0

        certificates = resume_data["certificates"]
        unique_certs = []
        removed_count = 0

        seen_certs = set()
        for cert in certificates:
            cert_name = cert.get("name", "") if isinstance(cert, dict) else str(cert)
            if not cert_name:
                continue

            cert_key = cert_name.lower().strip()
            if cert_key in seen_certs:
                removed_count += 1
            else:
                seen_certs.add(cert_key)
                unique_certs.append(cert)

        resume_data["certificates"] = unique_certs
        return removed_count
