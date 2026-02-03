# agents/analysis_agent.py
"""简历分析Agent"""
import json
from typing import Dict, Any, Optional, List
from agents.base import BaseAgent
from prompts import prompt_manager
from langchain_core.language_models import BaseChatModel


class AnalysisAgent(BaseAgent):
    """
    简历分析Agent - 负责多维度分析简历
    包括：技术能力、经验背景、项目经验、软技能
    """

    def __init__(
        self,
        llm: BaseChatModel,
        verbose: bool = False
    ):
        """
        初始化分析Agent

        Args:
            llm: 语言模型
            verbose: 是否输出详细信息
        """
        super().__init__(llm, verbose=verbose)

    def get_system_prompt(self, analysis_type: str) -> str:
        """
        获取系统Prompt

        Args:
            analysis_type: 分析类型 (technical/experience/project/soft_skill)
        """
        return prompt_manager.get_system_prompt(f"{analysis_type}_analysis")

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行综合分析任务（使用新版规则打分，不调用LLM）

        Args:
            input_data: 输入数据，包含：
                - resume_data: 简历数据（Dict格式）
                - job_requirements: 岗位要求（可选）

        Returns:
            分析结果，包含：
                - success: 是否成功
                - analysis_results: 完整分析结果
                - error: 错误信息（如果失败）
        """
        if not self.validate_input(input_data):
            return {
                "success": False,
                "error": "Invalid input data"
            }

        try:
            resume_data = input_data.get("resume_data")
            job_requirements = input_data.get("job_requirements", "")

            if not resume_data:
                return {
                    "success": False,
                    "error": "No resume data provided"
                }

            # 导入新版分析器和转换工具
            from tools.analysis import (
                TechnicalAnalyzer,
                ExperienceAnalyzer,
                SoftSkillAnalyzer
            )
            from tools.analysis.project_analyzer_simple import SimpleProjectAnalyzer
            from tools.analysis.converter import dict_to_cleaned_resume, analysis_result_to_dict
            from core.config import ScoreConfig

            # 加载配置
            config = ScoreConfig.from_yaml("config/scoring.yaml")

            # 将Dict转换为CleanedResume（传入config以使用配置中的关键词表）
            cleaned_resume = dict_to_cleaned_resume(resume_data, config)

            # 使用新版分析器进行分析
            technical_analyzer = TechnicalAnalyzer(config)
            experience_analyzer = ExperienceAnalyzer(config)
            project_analyzer = SimpleProjectAnalyzer(llm=self.llm)  # 传入LLM用于生成面试问题
            soft_skill_analyzer = SoftSkillAnalyzer(config)

            # 执行四个维度的分析
            technical_result_obj = technical_analyzer.analyze(cleaned_resume)
            experience_result_obj = experience_analyzer.analyze(cleaned_resume)
            project_result_obj = project_analyzer.analyze(cleaned_resume)
            soft_skill_result_obj = soft_skill_analyzer.analyze(cleaned_resume)

            # 将AnalysisResult转换为Dict格式（保持向后兼容）
            technical_result = analysis_result_to_dict(technical_result_obj)
            experience_result = analysis_result_to_dict(experience_result_obj)
            project_result = analysis_result_to_dict(project_result_obj)
            soft_skill_result = analysis_result_to_dict(soft_skill_result_obj)

            # 计算总分
            total_score = (
                technical_result_obj.score * config.weights["technical"] +
                experience_result_obj.score * config.weights["experience"] +
                project_result_obj.score * config.weights["project"] +
                soft_skill_result_obj.score * config.weights["soft_skill"]
            )

            analysis_results = {
                "technical_analysis": technical_result,
                "experience_analysis": experience_result,
                "project_analysis": project_result,
                "soft_skill_analysis": soft_skill_result,
                "total_score": round(total_score, 2),
                "score_breakdown": {
                    "technical": {
                        "score": technical_result_obj.score,
                        "weight": config.weights["technical"],
                        "weighted_score": technical_result_obj.score * config.weights["technical"],
                        "detail_scores": technical_result_obj.detail_scores,
                        "raw_analysis": technical_result_obj.raw_analysis
                    },
                    "experience": {
                        "score": experience_result_obj.score,
                        "weight": config.weights["experience"],
                        "weighted_score": experience_result_obj.score * config.weights["experience"],
                        "detail_scores": experience_result_obj.detail_scores,
                        "raw_analysis": experience_result_obj.raw_analysis
                    },
                    "project": {
                        "score": project_result_obj.score,
                        "weight": config.weights["project"],
                        "weighted_score": project_result_obj.score * config.weights["project"],
                        "detail_scores": project_result_obj.detail_scores,
                        "raw_analysis": project_result_obj.raw_analysis
                    },
                    "soft_skill": {
                        "score": soft_skill_result_obj.score,
                        "weight": config.weights["soft_skill"],
                        "weighted_score": soft_skill_result_obj.score * config.weights["soft_skill"],
                        "detail_scores": soft_skill_result_obj.detail_scores,
                        "raw_analysis": soft_skill_result_obj.raw_analysis
                    }
                }
            }

            return {
                "success": True,
                "analysis_results": analysis_results,
                "agent_name": "AnalysisAgent"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent_name": "AnalysisAgent"
            }

    async def _run_parallel_analysis(self, tasks: List) -> tuple:
        """并行运行分析任务"""
        import asyncio
        return await asyncio.gather(*tasks)

    async def _analyze_technical(self, resume_data: Dict[str, Any], job_requirements: str) -> Dict[str, Any]:
        """分析技术能力"""
        try:
            user_prompt = prompt_manager.get_user_prompt("technical_analysis")
            formatted_prompt = user_prompt.format(
                resume_data=json.dumps(resume_data, ensure_ascii=False, indent=2),
                job_requirements=job_requirements or "未提供特定岗位要求"
            )

            response = await self.llm.ainvoke([
                {"role": "system", "content": self.get_system_prompt("technical")},
                {"role": "user", "content": formatted_prompt}
            ])

            # 使用改进的JSON解析器
            result = self.parse_json_response(response)
            if result:
                return result
            return {"score": 60, "note": "解析失败，返回默认分数"}

        except Exception as e:
            return {"score": 60, "error": str(e)}

    async def _analyze_experience(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析经验背景"""
        try:
            user_prompt = prompt_manager.get_user_prompt("experience_analysis")
            formatted_prompt = user_prompt.format(
                resume_data=json.dumps(resume_data, ensure_ascii=False, indent=2)
            )

            response = await self.llm.ainvoke([
                {"role": "system", "content": self.get_system_prompt("experience")},
                {"role": "user", "content": formatted_prompt}
            ])

            result = self.parse_json_response(response)
            if result:
                return result
            return {"score": 60, "note": "解析失败"}

        except Exception as e:
            return {"score": 60, "error": str(e)}

    async def _analyze_project(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析项目经验"""
        try:
            user_prompt = prompt_manager.get_user_prompt("project_analysis")
            formatted_prompt = user_prompt.format(
                resume_data=json.dumps(resume_data, ensure_ascii=False, indent=2)
            )

            response = await self.llm.ainvoke([
                {"role": "system", "content": self.get_system_prompt("project")},
                {"role": "user", "content": formatted_prompt}
            ])

            result = self.parse_json_response(response)
            if result:
                return result
            return {"score": 60, "note": "解析失败"}

        except Exception as e:
            return {"score": 60, "error": str(e)}

    async def _analyze_soft_skill(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析软技能"""
        try:
            user_prompt = prompt_manager.get_user_prompt("soft_skill_analysis")
            formatted_prompt = user_prompt.format(
                resume_data=json.dumps(resume_data, ensure_ascii=False, indent=2)
            )

            response = await self.llm.ainvoke([
                {"role": "system", "content": self.get_system_prompt("soft_skill")},
                {"role": "user", "content": formatted_prompt}
            ])

            result = self.parse_json_response(response)
            if result:
                return result
            return {"score": 60, "note": "解析失败"}

        except Exception as e:
            return {"score": 60, "error": str(e)}

    def _calculate_total_score(
        self,
        technical_score: float,
        experience_score: float,
        project_score: float,
        soft_skill_score: float
    ) -> float:
        """
        计算总分

        权重分配：
        - 技术能力：25%
        - 经验背景：20%
        - 项目经验：40%
        - 软技能：15%
        """
        total = (
            technical_score * 0.25 +
            experience_score * 0.20 +
            project_score * 0.40 +
            soft_skill_score * 0.15
        )
        return round(total, 2)


class TechnicalAnalysisAgent(BaseAgent):
    """技术能力分析Agent"""

    def __init__(self, llm: BaseChatModel, verbose: bool = False):
        super().__init__(llm, verbose=verbose)

    def get_system_prompt(self) -> str:
        return prompt_manager.get_system_prompt("technical_analysis")

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        agent = AnalysisAgent(self.llm, self.verbose)
        result = await agent._analyze_technical(
            input_data.get("resume_data", {}),
            input_data.get("job_requirements", "")
        )
        return {"success": True, "analysis_result": result}


class ExperienceAnalysisAgent(BaseAgent):
    """经验背景分析Agent"""

    def __init__(self, llm: BaseChatModel, verbose: bool = False):
        super().__init__(llm, verbose=verbose)

    def get_system_prompt(self) -> str:
        return prompt_manager.get_system_prompt("experience_analysis")

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        agent = AnalysisAgent(self.llm, self.verbose)
        result = await agent._analyze_experience(input_data.get("resume_data", {}))
        return {"success": True, "analysis_result": result}


class ProjectAnalysisAgent(BaseAgent):
    """项目经验分析Agent"""

    def __init__(self, llm: BaseChatModel, verbose: bool = False):
        super().__init__(llm, verbose=verbose)

    def get_system_prompt(self) -> str:
        return prompt_manager.get_system_prompt("project_analysis")

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        agent = AnalysisAgent(self.llm, self.verbose)
        result = await agent._analyze_project(input_data.get("resume_data", {}))
        return {"success": True, "analysis_result": result}


class SoftSkillAnalysisAgent(BaseAgent):
    """软技能分析Agent"""

    def __init__(self, llm: BaseChatModel, verbose: bool = False):
        super().__init__(llm, verbose=verbose)

    def get_system_prompt(self) -> str:
        return prompt_manager.get_system_prompt("soft_skill_analysis")

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        agent = AnalysisAgent(self.llm, self.verbose)
        result = await agent._analyze_soft_skill(input_data.get("resume_data", {}))
        return {"success": True, "analysis_result": result}
