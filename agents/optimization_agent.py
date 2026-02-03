# agents/optimization_agent.py
"""优化建议Agent"""
import json
from typing import Dict, Any, List
from agents.base import BaseAgent
from prompts import prompt_manager
from langchain_core.language_models import BaseChatModel


class OptimizationAgent(BaseAgent):
    """
    优化建议Agent - 基于分析结果提供简历优化建议
    """

    def __init__(
        self,
        llm: BaseChatModel,
        verbose: bool = False
    ):
        """
        初始化优化Agent

        Args:
            llm: 语言模型
            verbose: 是否输出详细信息
        """
        super().__init__(llm, verbose=verbose)

    def get_system_prompt(self) -> str:
        """获取系统Prompt"""
        return prompt_manager.get_system_prompt("optimization")

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行优化建议生成任务

        Args:
            input_data: 输入数据，包含：
                - analysis_results: 分析结果
                - resume_data: 简历数据
                - job_requirements: 岗位要求（可选）

        Returns:
            优化建议结果，包含：
                - success: 是否成功
                - optimization_suggestions: 优化建议列表
                - priority_suggestions: 优先级建议
                - error: 错误信息（如果失败）
        """
        if not self.validate_input(input_data):
            return {
                "success": False,
                "error": "Invalid input data"
            }

        try:
            analysis_results = input_data.get("analysis_results")
            resume_data = input_data.get("resume_data")
            job_requirements = input_data.get("job_requirements", "")

            if not analysis_results or not resume_data:
                return {
                    "success": False,
                    "error": "Missing analysis_results or resume_data"
                }

            # 生成详细优化建议
            detailed_suggestions = await self._generate_detailed_suggestions(
                analysis_results,
                resume_data,
                job_requirements
            )

            # 如果LLM返回空结果或失败，使用规则工具生成
            if not detailed_suggestions:
                if self.verbose:
                    print("[WARNING] LLM生成建议失败，使用规则工具生成")
                from tools.optimization import SuggestionGenerator
                detailed_suggestions = SuggestionGenerator.generate_suggestions(
                    analysis_results,
                    resume_data
                )

            # 生成优先级建议
            priority_suggestions = await self._generate_priority_suggestions(
                analysis_results
            )

            # 如果优先级建议为空，也使用规则工具
            if not priority_suggestions:
                from tools.optimization import SuggestionGenerator
                priority_suggestions = SuggestionGenerator.generate_priority_suggestions(
                    analysis_results
                )

            return {
                "success": True,
                "optimization_suggestions": detailed_suggestions,
                "priority_suggestions": priority_suggestions,
                "agent_name": "OptimizationAgent"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent_name": "OptimizationAgent"
            }

    async def _generate_detailed_suggestions(
        self,
        analysis_results: Dict[str, Any],
        resume_data: Dict[str, Any],
        job_requirements: str
    ) -> List[Dict[str, Any]]:
        """生成详细优化建议"""
        try:
            user_prompt = prompt_manager.get_user_prompt("optimization")
            formatted_prompt = user_prompt.format(
                analysis_results=json.dumps(analysis_results, ensure_ascii=False, indent=2),
                resume_data=json.dumps(resume_data, ensure_ascii=False, indent=2),
                job_requirements=job_requirements or "未提供特定岗位要求"
            )

            response = await self.llm.ainvoke([
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": formatted_prompt}
            ])

            # 获取原始响应文本
            response_text = response.content if hasattr(response, 'content') else str(response)

            # 使用改进的JSON解析器
            result = self.parse_json_response(response)

            if result:
                # 如果返回的是列表
                if isinstance(result, list):
                    return result
                # 如果返回的是包含suggestions字段的对象
                elif isinstance(result, dict):
                    return result.get("suggestions") or result.get("optimization_suggestions") or [result]

            # 解析失败，返回详细错误信息
            error_msg = f"JSON解析失败。LLM返回内容（前500字符）:\n{response_text[:500]}"
            if self.verbose:
                print(f"[ERROR] {error_msg}")
                print(f"[DEBUG] 完整响应:\n{response_text}")

            return [{"error": error_msg}]

        except Exception as e:
            import traceback
            error_details = {
                "error": str(e),
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc() if self.verbose else None
            }
            if self.verbose:
                print(f"[ERROR] 生成优化建议时出错: {error_details}")
            return [error_details]

    async def _generate_priority_suggestions(
        self,
        analysis_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """生成优先级优化建议"""
        try:
            user_prompt = prompt_manager.get_user_prompt("priority_optimization")
            formatted_prompt = user_prompt.format(
                analysis_results=json.dumps(analysis_results, ensure_ascii=False, indent=2)
            )

            system_prompt = prompt_manager.get_system_prompt("priority_optimization")

            response = await self.llm.ainvoke([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": formatted_prompt}
            ])

            response_text = response.content if hasattr(response, 'content') else str(response)

            # 解析优先级建议
            # 这里可以添加更复杂的解析逻辑
            # 暂时返回简单的结构
            return [
                {
                    "priority": "high",
                    "description": "基于分析结果的Top 5优先建议",
                    "details": response_text
                }
            ]

        except Exception as e:
            return [{"error": str(e)}]

    def categorize_suggestions(self, suggestions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        对建议进行分类

        Args:
            suggestions: 建议列表

        Returns:
            按类别分组的建议字典
        """
        categories = {
            "technical": [],
            "experience": [],
            "project": [],
            "soft_skill": [],
            "structure": [],
            "format": []
        }

        for suggestion in suggestions:
            category = suggestion.get("category", "other")
            if category in categories:
                categories[category].append(suggestion)
            else:
                categories.setdefault(category, []).append(suggestion)

        return categories

    def filter_by_priority(
        self,
        suggestions: List[Dict[str, Any]],
        priority: str = "high"
    ) -> List[Dict[str, Any]]:
        """
        按优先级过滤建议

        Args:
            suggestions: 建议列表
            priority: 优先级 (high/medium/low)

        Returns:
            过滤后的建议列表
        """
        return [
            s for s in suggestions
            if s.get("priority", "").lower() == priority.lower()
        ]


class PriorityOptimizationAgent(BaseAgent):
    """优先级优化Agent - 识别最需要改进的关键问题"""

    def __init__(
        self,
        llm: BaseChatModel,
        verbose: bool = False
    ):
        """
        初始化优先级优化Agent

        Args:
            llm: 语言模型
            verbose: 是否输出详细信息
        """
        super().__init__(llm, verbose=verbose)

    def get_system_prompt(self) -> str:
        """获取系统Prompt"""
        return prompt_manager.get_system_prompt("priority_optimization")

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行优先级优化任务

        Args:
            input_data: 输入数据，包含：
                - analysis_results: 分析结果

        Returns:
            优先级优化结果，包含：
                - success: 是否成功
                - top_priorities: Top 5优先改进项
                - error: 错误信息（如果失败）
        """
        if not self.validate_input(input_data):
            return {
                "success": False,
                "error": "Invalid input data"
            }

        try:
            analysis_results = input_data.get("analysis_results")

            if not analysis_results:
                return {
                    "success": False,
                    "error": "No analysis results provided"
                }

            # 使用OptimizationAgent的方法
            opt_agent = OptimizationAgent(self.llm, self.verbose)
            priorities = await opt_agent._generate_priority_suggestions(analysis_results)

            return {
                "success": True,
                "top_priorities": priorities,
                "agent_name": "PriorityOptimizationAgent"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent_name": "PriorityOptimizationAgent"
            }
