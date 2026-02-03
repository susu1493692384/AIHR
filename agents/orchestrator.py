# agents/orchestrator.py
"""主控Agent - 协调所有Agent的执行"""
import json
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from langchain_core.language_models import BaseChatModel
from agents.parsing_agent import ParsingAgent, StructureMappingAgent
from agents.cleaning_agent import CleaningAgent, DeduplicationAgent
from agents.analysis_agent import AnalysisAgent
from agents.optimization_agent import OptimizationAgent
from agents.report_agent import ReportAgent


class OrchestratorAgent:
    """
    主控Agent - 协调简历分析的完整流程
    使用状态图管理整个分析流程
    """

    def __init__(
        self,
        llm: BaseChatModel,
        verbose: bool = False,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ):
        """
        初始化主控Agent

        Args:
            llm: 语言模型
            verbose: 是否输出详细信息
            progress_callback: 进度回调函数，参数为 (current_step, total_steps, step_name)
        """
        self.llm = llm
        self.verbose = verbose
        self.progress_callback = progress_callback

        # 初始化所有子Agent
        self.parsing_agent = ParsingAgent(llm, verbose)
        self.structure_mapping_agent = StructureMappingAgent(llm, verbose)
        self.cleaning_agent = CleaningAgent(llm, verbose)
        self.deduplication_agent = DeduplicationAgent(llm, verbose)
        self.analysis_agent = AnalysisAgent(llm, verbose)
        self.optimization_agent = OptimizationAgent(llm, verbose)
        self.report_agent = ReportAgent(llm, verbose)

        # 初始化状态
        self.state: Dict[str, Any] = {}

    def _update_progress(self, current_step: int, total_steps: int, step_name: str):
        """更新进度"""
        if self.progress_callback:
            self.progress_callback(current_step, total_steps, step_name)
            # 添加延迟，让Streamlit有时间更新UI
            # 只有在使用进度回调时才延迟（用于前端显示）
            import asyncio
            asyncio.sleep(0.3)

    async def run(
        self,
        input_data: Dict[str, Any],
        steps: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        执行完整的简历分析流程

        Args:
            input_data: 输入数据，包含：
                - file_path: 文件路径（可选）
                - text: 简历文本（可选）
                - job_requirements: 岗位要求（可选）
                - report_types: 报告类型列表（可选）
            steps: 要执行的步骤列表（可选，如果为None则执行全部步骤）

        Returns:
            最终分析结果，包含：
                - success: 是否成功
                - state: 完整状态
                - reports: 生成的报告
                - error: 错误信息（如果失败）
        """
        # 定义默认执行步骤
        default_steps = [
            "parse",
            "structure_mapping",
            "clean",
            "deduplicate",
            "analyze",
            "optimize",
            "report"
        ]

        execution_steps = steps or default_steps

        try:
            # 初始化状态
            self.state = {
                "input": input_data,
                "current_step": None,
                "steps_completed": [],
                "steps_failed": [],
                "intermediate_results": {},
                "final_result": None
            }

            # 1. 解析简历
            if "parse" in execution_steps:
                await self._step_parse()

            # 2. 结构映射
            if "structure_mapping" in execution_steps:
                await self._step_structure_mapping()

            # 3. 数据清洗
            if "clean" in execution_steps:
                await self._step_clean()

            # 4. 数据去重
            if "deduplicate" in execution_steps:
                await self._step_deduplicate()

            # 5. 分析
            if "analyze" in execution_steps:
                await self._step_analyze()

            # 6. 优化建议
            if "optimize" in execution_steps:
                await self._step_optimize()

            # 7. 生成报告
            if "report" in execution_steps:
                await self._step_report(input_data.get("report_types", ["full"]))

            # 记录完成时间
            self.state["completed_at"] = datetime.now().isoformat()

            return {
                "success": True,
                "state": self._summarize_state(),
                "reports": self.state.get("final_result", {}).get("reports", {}),
                "agent_name": "OrchestratorAgent"
            }

        except Exception as e:
            self.state["error"] = str(e)
            self.state["failed_at"] = datetime.now().isoformat()

            return {
                "success": False,
                "error": str(e),
                "state": self._summarize_state(),
                "agent_name": "OrchestratorAgent"
            }

    async def _step_parse(self):
        """步骤1: 解析简历"""
        self.state["current_step"] = "parse"
        self._update_progress(1, 7, "📄 解析简历")

        if self.verbose:
            print("[FILE] 步骤1: 解析简历...")
            print(f"  输入: file_path={self.state['input'].get('file_path', 'N/A')}")
            print(f"  处理: 使用ParsingAgent提取PDF/DOCX文本并解析为结构化数据")

        result = await self.parsing_agent.run({
            "file_path": self.state["input"].get("file_path"),
            "text": self.state["input"].get("text")
        })

        if result.get("success"):
            self.state["intermediate_results"]["parsed"] = result
            self.state["steps_completed"].append("parse")
            self.state["resume_data"] = result.get("parsed_data")

            if self.verbose:
                raw_text_len = len(result.get("raw_text", ""))
                parsed_data = result.get("parsed_data", {})
                print(f"  输出: 提取文本 {raw_text_len} 字符")
                print(f"  输出: 解析出 {len(parsed_data)} 个顶级字段")
                if parsed_data:
                    print(f"  字段: {', '.join(parsed_data.keys())}")
                print("[OK] 简历解析完成")
        else:
            self.state["steps_failed"].append("parse")
            raise Exception(f"解析失败: {result.get('error')}")

    async def _step_structure_mapping(self):
        """步骤2: 结构映射"""
        self.state["current_step"] = "structure_mapping"
        self._update_progress(2, 7, "🔧 结构映射")

        input_data = self.state.get("resume_data", {})

        if self.verbose:
            print("[TOOL] 步骤2: 结构映射...")
            print(f"  输入: {len(input_data)} 个字段")
            print(f"  处理: 使用规则映射将字段名标准化（中文→英文）")

        result = await self.structure_mapping_agent.run({
            "parsed_data": input_data
        })

        if result.get("success"):
            self.state["intermediate_results"]["structure_mapped"] = result
            self.state["steps_completed"].append("structure_mapping")
            self.state["resume_data"] = result.get("mapped_data")

            if self.verbose:
                mapped_data = result.get("mapped_data", {})
                print(f"  输出: 映射后 {len(mapped_data)} 个字段")
                if mapped_data:
                    print(f"  字段: {', '.join(mapped_data.keys())}")
                print("[OK] 结构映射完成")
        else:
            self.state["steps_failed"].append("structure_mapping")
            if self.verbose:
                print(f"[WARNING] 结构映射失败: {result.get('error')}")
                print(f"  说明: 继续使用原始数据")
            # 继续使用原始数据

    async def _step_clean(self):
        """步骤3: 数据清洗"""
        self.state["current_step"] = "clean"
        self._update_progress(3, 7, "🧹 数据清洗")

        input_data = self.state.get("resume_data", {})

        if self.verbose:
            print("[CLEAN] 步骤3: 数据清洗...")
            print(f"  输入: {len(input_data)} 个字段")
            print(f"  处理: 标准化日期格式、清理文本、处理缺失值")

        result = await self.cleaning_agent.run({
            "resume_data": input_data
        })

        if result.get("success"):
            self.state["intermediate_results"]["cleaned"] = result
            self.state["steps_completed"].append("clean")
            self.state["resume_data"] = result.get("cleaned_data")

            if self.verbose:
                cleaned_data = result.get("cleaned_data", {})
                report = result.get("cleaning_report", {})
                print(f"  输出: 清洗后 {len(cleaned_data)} 个字段")
                if report:
                    print(f"  清洗报告: {report}")
                print("[OK] 数据清洗完成")
        else:
            self.state["steps_failed"].append("clean")
            if self.verbose:
                print(f"[WARNING] 数据清洗失败: {result.get('error')}")
                print(f"  说明: 继续使用未清洗的数据")
            # 继续使用未清洗的数据

    async def _step_deduplicate(self):
        """步骤4: 数据去重"""
        self.state["current_step"] = "deduplicate"
        self._update_progress(4, 7, "🔄 数据去重")

        input_data = self.state.get("resume_data", {})

        if self.verbose:
            print("[ROTATE] 步骤4: 数据去重...")
            print(f"  输入: {len(input_data)} 个字段")
            print(f"  处理: 识别并合并重复的技能、项目、工作经历")

        result = await self.deduplication_agent.run({
            "resume_data": input_data
        })

        if result.get("success"):
            self.state["intermediate_results"]["deduplicated"] = result
            self.state["steps_completed"].append("deduplicate")
            self.state["resume_data"] = result.get("deduplicated_data")

            if self.verbose:
                deduplicated_data = result.get("deduplicated_data", {})
                report = result.get("deduplication_report", {})
                report_text = result.get("deduplication_report_text", "")

                print(f"  输出: 去重后 {len(deduplicated_data)} 个字段")

                # 显示详细的去重报告
                if report_text:
                    print("\n" + report_text)
                elif report:
                    summary = report.get("summary", {})
                    print(f"  去重统计:")
                    print(f"    - 处理项数: {summary.get('total_items_processed', 0)}")
                    print(f"    - 删除重复: {summary.get('total_duplicates_removed', 0)}")
                    print(f"    - 合并项数: {summary.get('items_merged', 0)}")

                print("[OK] 数据去重完成")
        else:
            self.state["steps_failed"].append("deduplicate")
            if self.verbose:
                print(f"[WARNING] 数据去重失败: {result.get('error')}")
                print(f"  说明: 继续使用未去重的数据")
            # 继续使用未去重的数据

    async def _step_analyze(self):
        """步骤5: 分析"""
        self.state["current_step"] = "analyze"
        self._update_progress(5, 7, "📊 多维度分析")

        input_data = self.state.get("resume_data", {})
        job_req = self.state["input"].get("job_requirements", "")

        if self.verbose:
            print("[CHART] 步骤5: 多维度分析...")
            print(f"  输入: {len(input_data)} 个字段")
            print(f"  岗位要求: {job_req[:50] if job_req else 'N/A'}...")
            print(f"  处理: 从4个维度分析（技术、经验、项目、软技能）")

        result = await self.analysis_agent.run({
            "resume_data": input_data,
            "job_requirements": job_req
        })

        if result.get("success"):
            self.state["intermediate_results"]["analyzed"] = result
            self.state["steps_completed"].append("analyze")
            self.state["analysis_results"] = result.get("analysis_results")

            if self.verbose:
                analysis_results = result.get("analysis_results", {})
                total_score = analysis_results.get("total_score", 0)
                score_breakdown = analysis_results.get("score_breakdown", {})
                print(f"  输出: 总分 {total_score:.1f}")
                print(f"  分项得分:")
                for dim, data in score_breakdown.items():
                    score = data.get("score", 0)
                    weight = data.get("weight", 0)
                    print(f"    - {dim}: {score:.1f}分 (权重{weight*100:.0%})")
                print("[OK] 分析完成")
        else:
            self.state["steps_failed"].append("analyze")
            raise Exception(f"分析失败: {result.get('error')}")

    async def _step_optimize(self):
        """步骤6: 优化建议"""
        self.state["current_step"] = "optimize"
        self._update_progress(6, 7, "💡 优化建议")

        analysis_results = self.state.get("analysis_results", {})
        resume_data = self.state.get("resume_data", {})
        job_req = self.state["input"].get("job_requirements", "")

        if self.verbose:
            print("[LIGHT] 步骤6: 生成优化建议...")
            print(f"  输入: 分析结果总分={analysis_results.get('total_score', 0):.1f}")
            print(f"  处理: 基于分析结果生成简历改进建议")

        result = await self.optimization_agent.run({
            "analysis_results": analysis_results,
            "resume_data": resume_data,
            "job_requirements": job_req
        })

        if result.get("success"):
            self.state["intermediate_results"]["optimized"] = result
            self.state["steps_completed"].append("optimize")
            self.state["optimization_suggestions"] = result.get("optimization_suggestions")

            if self.verbose:
                suggestions = result.get("optimization_suggestions", [])
                priority_suggestions = result.get("priority_suggestions", [])
                print(f"  输出: {len(suggestions)} 条建议")
                print(f"  优先建议: {len(priority_suggestions)} 条")
                if suggestions:
                    print(f"  建议类别:")
                    for sug in suggestions[:5]:
                        category = sug.get("category", "未分类")
                        priority = sug.get("priority", "中")
                        print(f"    - {category}: {priority}优先级")
                print("[OK] 优化建议生成完成")
        else:
            self.state["steps_failed"].append("optimize")
            if self.verbose:
                print(f"[WARNING] 优化建议生成失败: {result.get('error')}")
                print(f"  说明: 将使用空建议列表")
            self.state["optimization_suggestions"] = []

    async def _step_report(self, report_types: List[str]):
        """步骤7: 生成报告"""
        self.state["current_step"] = "report"
        self._update_progress(7, 7, "📝 生成报告")

        analysis_results = self.state.get("analysis_results", {})
        resume_data = self.state.get("resume_data", {})
        suggestions = self.state.get("optimization_suggestions")
        job_req = self.state["input"].get("job_requirements", "")

        # 收集处理信息（用于增强报告透明度）
        processing_info = {
            "steps_completed": self.state.get("steps_completed", []),
            "steps_failed": self.state.get("steps_failed", []),
            "started_at": self.state.get("started_at"),
            "intermediate_results": {}
        }

        # 添加各步骤的中间结果摘要
        for step_name in ["parsed", "structured", "cleaned", "deduplicated"]:
            step_result = self.state.get("intermediate_results", {}).get(step_name, {})
            if step_result:
                processing_info["intermediate_results"][step_name] = self._extract_step_summary(step_name, step_result)

        if self.verbose:
            print("[NOTE] 步骤7: 生成报告...")
            print(f"  输入: 分析结果、优化建议、简历数据、处理信息")
            print(f"  报告类型: {', '.join(report_types)}")
            print(f"  处理: 整合所有分析结果和处理过程，生成最终报告")

        reports = {}

        for report_type in report_types:
            if self.verbose:
                print(f"  生成 {report_type} 报告...")

            result = await self.report_agent.run({
                "analysis_results": analysis_results,
                "resume_data": resume_data,
                "optimization_suggestions": suggestions,
                "job_requirements": job_req,
                "report_type": report_type,
                "processing_info": processing_info  # 新增：处理信息
            })

            if result.get("success"):
                reports[report_type] = result.get("report")

                if self.verbose:
                    report = result.get("report", {})
                    print(f"    ✓ {report_type} 报告生成成功 (包含 {len(report)} 个字段)")
            else:
                if self.verbose:
                    print(f"    ✗ {report_type} 报告生成失败: {result.get('error')}")

        self.state["intermediate_results"]["report"] = {"reports": reports}
        self.state["steps_completed"].append("report")

        # 保存最终结果
        self.state["final_result"] = {
            "reports": reports,
            "analysis_results": analysis_results,
            "optimization_suggestions": suggestions
        }

        if self.verbose:
            print(f"  输出: {len(reports)} 个报告")
            print(f"  报告类型: {', '.join(reports.keys())}")
            print("[OK] 报告生成完成")

    def _extract_step_summary(self, step_name: str, step_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        提取步骤结果的摘要信息

        Args:
            step_name: 步骤名称
            step_result: 步骤执行结果

        Returns:
            步骤摘要
        """
        summary = {"step": step_name}

        if step_name == "parsed":
            # 解析步骤摘要
            parsed_data = step_result.get("parsed_data", {})
            summary["fields_count"] = len(parsed_data) if parsed_data else 0
            summary["parse_method"] = step_result.get("parse_method", "unknown")

        elif step_name == "structured":
            # 结构映射步骤摘要
            summary["normalized"] = step_result.get("success", False)
            mapped_data = step_result.get("mapped_data", {})
            summary["fields_count"] = len(mapped_data) if mapped_data else 0

        elif step_name == "cleaned":
            # 清洗步骤摘要
            cleaned_data = step_result.get("cleaned_data", {})
            summary["fields_count"] = len(cleaned_data) if cleaned_data else 0
            summary["missing_values_handled"] = step_result.get("missing_values_handled", 0)

        elif step_name == "deduplicated":
            # 去重步骤摘要（最重要）
            summary["deduplication_performed"] = step_result.get("success", False)

            # 提取去重报告
            dedup_report = step_result.get("deduplication_report", {})
            if dedup_report:
                summary["deduplication_summary"] = dedup_report.get("summary", {})

                # 提取具体的去重信息
                summary["skills"] = {
                    "removed": len(dedup_report.get("skills", {}).get("removed", [])),
                    "merged": len(dedup_report.get("skills", {}).get("merged", []))
                }
                summary["projects"] = {
                    "removed": len(dedup_report.get("projects", {}).get("removed", []))
                }
                summary["work_experience"] = {
                    "removed": len(dedup_report.get("work_experience", {}).get("removed", []))
                }

                # 保留原始去重报告文本
                summary["deduplication_report_text"] = step_result.get("deduplication_report_text", "")

        return summary

    def _summarize_state(self) -> Dict[str, Any]:
        """总结状态信息"""
        final_result = self.state.get("final_result") or {}
        analysis_results = self.state.get("analysis_results", {})

        return {
            "steps_completed": self.state.get("steps_completed", []),
            "steps_failed": self.state.get("steps_failed", []),
            "total_score": analysis_results.get("total_score", 0),
            "score_breakdown": analysis_results.get("score_breakdown", {}),
            "optimization_suggestions": self.state.get("optimization_suggestions", []),
            "report_types": list(final_result.get("reports", {}).keys()) if final_result else [],
            "started_at": self.state.get("started_at"),
            "completed_at": self.state.get("completed_at"),
            # 添加简历数据，供前端使用
            "resume_data": self.state.get("resume_data", {})
        }

    def get_state(self) -> Dict[str, Any]:
        """获取当前完整状态"""
        return self.state.copy()

    def get_intermediate_result(self, step: str) -> Optional[Dict[str, Any]]:
        """
        获取指定步骤的中间结果

        Args:
            step: 步骤名称 (parse/structure_mapping/clean/deduplicate/analyze/optimize/report)

        Returns:
            该步骤的结果，如果不存在返回None
        """
        return self.state.get("intermediate_results", {}).get(step)

    def reset_state(self):
        """重置状态"""
        self.state = {}

    async def run_partial(
        self,
        input_data: Dict[str, Any],
        from_step: str,
        to_step: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        运行部分流程（用于调试或重试）

        Args:
            input_data: 输入数据
            from_step: 起始步骤
            to_step: 结束步骤（可选，如果为None则运行到末尾）

        Returns:
            执行结果
        """
        all_steps = [
            "parse",
            "structure_mapping",
            "clean",
            "deduplicate",
            "analyze",
            "optimize",
            "report"
        ]

        try:
            start_idx = all_steps.index(from_step)
            end_idx = all_steps.index(to_step) if to_step else len(all_steps)

            steps_to_run = all_steps[start_idx:end_idx + 1]

            return await self.run(input_data, steps=steps_to_run)

        except ValueError:
            return {
                "success": False,
                "error": f"Invalid step name: {from_step} or {to_step}"
            }

    def export_state(self, filepath: str):
        """
        导出状态到文件

        Args:
            filepath: 文件路径
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def import_state(self, filepath: str):
        """
        从文件导入状态

        Args:
            filepath: 文件路径
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            self.state = json.load(f)
