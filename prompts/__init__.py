# prompts/__init__.py
"""Prompt模块 - 统一管理所有Prompt模板"""
from typing import Dict, Type, Optional
from prompts.base import BasePrompt, PromptTemplate

# 导入所有Prompt类
from prompts.parsing_prompts import (
    ParsingPrompts,
    StructureMappingPrompt
)
from prompts.cleaning_prompts import (
    CleaningPrompts,
    DeduplicationPrompt
)
from prompts.analysis_prompts import (
    TechnicalAnalysisPrompt,
    ExperienceAnalysisPrompt,
    ProjectAnalysisPrompt,
    SoftSkillAnalysisPrompt
)
from prompts.optimization_prompts import (
    OptimizationPrompts,
    PriorityOptimizationPrompt
)
from prompts.report_prompts import (
    ReportGenerationPrompt,
    HRSummaryPrompt,
    CandidateSummaryPrompt,
    ScoreExplanationPrompt
)
from prompts.matching_prompts import JobMatchingPrompt


class PromptManager:
    """Prompt模板管理器"""

    def __init__(self):
        """初始化Prompt管理器"""
        self._prompts: Dict[str, BasePrompt] = {}
        self._register_default_prompts()

    def _register_default_prompts(self):
        """注册默认的Prompt模板"""
        # 解析相关
        self.register("parsing", ParsingPrompts())
        self.register("structure_mapping", StructureMappingPrompt())

        # 清洗相关
        self.register("cleaning", CleaningPrompts())
        self.register("deduplication", DeduplicationPrompt())

        # 分析相关
        self.register("technical_analysis", TechnicalAnalysisPrompt())
        self.register("experience_analysis", ExperienceAnalysisPrompt())
        self.register("project_analysis", ProjectAnalysisPrompt())
        self.register("soft_skill_analysis", SoftSkillAnalysisPrompt())

        # 优化相关
        self.register("optimization", OptimizationPrompts())
        self.register("priority_optimization", PriorityOptimizationPrompt())

        # 报告相关
        self.register("report_generation", ReportGenerationPrompt())
        self.register("hr_summary", HRSummaryPrompt())
        self.register("candidate_summary", CandidateSummaryPrompt())
        self.register("score_explanation", ScoreExplanationPrompt())

        # 匹配相关
        self.register("job_matching", JobMatchingPrompt())

    def register(self, name: str, prompt: BasePrompt):
        """
        注册Prompt模板

        Args:
            name: Prompt名称
            prompt: Prompt实例
        """
        self._prompts[name] = prompt

    def get(self, name: str) -> Optional[BasePrompt]:
        """
        获取Prompt模板

        Args:
            name: Prompt名称

        Returns:
            Prompt实例，如果不存在返回None
        """
        return self._prompts.get(name)

    def get_system_prompt(self, name: str) -> Optional[str]:
        """
        获取系统Prompt

        Args:
            name: Prompt名称

        Returns:
            系统Prompt字符串
        """
        prompt = self.get(name)
        return prompt.get_system_prompt() if prompt else None

    def get_user_prompt(self, name: str) -> Optional[str]:
        """
        获取用户Prompt

        Args:
            name: Prompt名称

        Returns:
            用户Prompt字符串
        """
        prompt = self.get(name)
        return prompt.get_user_prompt() if prompt else None

    def format_prompt(self, name: str, **kwargs) -> Optional[str]:
        """
        格式化Prompt

        Args:
            name: Prompt名称
            **kwargs: 格式化参数

        Returns:
            格式化后的Prompt字符串
        """
        prompt = self.get(name)
        return prompt.format(**kwargs) if prompt else None

    def list_prompts(self) -> list[str]:
        """
        列出所有已注册的Prompt名称

        Returns:
            Prompt名称列表
        """
        return list(self._prompts.keys())

    def create_few_shot(
        self,
        system_prompt: str,
        examples: list[Dict[str, str]],
        input_template: str = "Input: {input}\nOutput: {output}"
    ) -> str:
        """
        创建Few-Shot Prompt

        Args:
            system_prompt: 系统Prompt
            examples: 示例列表
            input_template: 输入模板

        Returns:
            Few-Shot Prompt字符串
        """
        return PromptTemplate.create_few_shot_prompt(
            system_prompt, examples, input_template
        )

    def create_cot(
        self,
        task_description: str,
        steps: list[str]
    ) -> str:
        """
        创建思维链Prompt

        Args:
            task_description: 任务描述
            steps: 思维步骤

        Returns:
            CoT Prompt字符串
        """
        return PromptTemplate.create_cot_prompt(task_description, steps)

    def create_structured(
        self,
        role: str,
        task: str,
        constraints: list[str] = None,
        output_format: str = None
    ) -> str:
        """
        创建结构化Prompt

        Args:
            role: 角色
            task: 任务
            constraints: 约束条件
            output_format: 输出格式

        Returns:
            结构化Prompt字符串
        """
        return PromptTemplate.create_structured_prompt(
            role, task, constraints, output_format
        )


# 全局Prompt管理器实例
prompt_manager = PromptManager()


__all__ = [
    # 基类
    "BasePrompt",
    "PromptTemplate",
    "PromptManager",

    # 解析相关
    "ParsingPrompts",
    "StructureMappingPrompt",

    # 清洗相关
    "CleaningPrompts",
    "DeduplicationPrompt",

    # 分析相关
    "TechnicalAnalysisPrompt",
    "ExperienceAnalysisPrompt",
    "ProjectAnalysisPrompt",
    "SoftSkillAnalysisPrompt",

    # 优化相关
    "OptimizationPrompts",
    "PriorityOptimizationPrompt",

    # 报告相关
    "ReportGenerationPrompt",
    "HRSummaryPrompt",
    "CandidateSummaryPrompt",
    "ScoreExplanationPrompt",

    # 匹配相关
    "JobMatchingPrompt",

    # 全局实例
    "prompt_manager",
]
