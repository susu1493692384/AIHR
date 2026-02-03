# agents/__init__.py
"""Agent模块 - 统一管理所有Agent"""
from agents.base import BaseAgent
from agents.parsing_agent import ParsingAgent, StructureMappingAgent
from agents.cleaning_agent import CleaningAgent, DeduplicationAgent
from agents.analysis_agent import (
    AnalysisAgent,
    TechnicalAnalysisAgent,
    ExperienceAnalysisAgent,
    ProjectAnalysisAgent,
    SoftSkillAnalysisAgent
)
from agents.optimization_agent import OptimizationAgent, PriorityOptimizationAgent
from agents.report_agent import ReportAgent
from agents.orchestrator import OrchestratorAgent


__all__ = [
    # 基类
    "BaseAgent",

    # 解析相关
    "ParsingAgent",
    "StructureMappingAgent",

    # 清洗相关
    "CleaningAgent",
    "DeduplicationAgent",

    # 分析相关
    "AnalysisAgent",
    "TechnicalAnalysisAgent",
    "ExperienceAnalysisAgent",
    "ProjectAnalysisAgent",
    "SoftSkillAnalysisAgent",

    # 优化相关
    "OptimizationAgent",
    "PriorityOptimizationAgent",

    # 报告相关
    "ReportAgent",

    # 主控
    "OrchestratorAgent",
]
