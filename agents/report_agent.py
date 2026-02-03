# agents/report_agent.py
"""报告生成Agent"""
import json
from typing import Dict, Any, Optional
from datetime import datetime
from agents.base import BaseAgent
from prompts import prompt_manager
from langchain_core.language_models import BaseChatModel


class ReportAgent(BaseAgent):
    """
    报告生成Agent - 整合所有分析结果生成最终报告
    """

    def __init__(
        self,
        llm: BaseChatModel,
        verbose: bool = False
    ):
        """
        初始化报告Agent

        Args:
            llm: 语言模型
            verbose: 是否输出详细信息
        """
        super().__init__(llm, verbose=verbose)

    def get_system_prompt(self) -> str:
        """获取系统Prompt"""
        return prompt_manager.get_system_prompt("report_generation")

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行报告生成任务（使用模板，不调用LLM）

        Args:
            input_data: 输入数据，包含：
                - analysis_results: 分析结果
                - resume_data: 简历数据
                - optimization_suggestions: 优化建议（可选）
                - job_requirements: 岗位要求（可选）
                - report_type: 报告类型 (full/hr_summary/candidate_summary)
                - processing_info: 处理信息（可选）- 包含步骤执行、去重报告等

        Returns:
            报告生成结果，包含：
                - success: 是否成功
                - report: 生成的报告
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
            optimization_suggestions = input_data.get("optimization_suggestions")
            job_requirements = input_data.get("job_requirements", "")
            report_type = input_data.get("report_type", "full")
            processing_info = input_data.get("processing_info")  # 新增：处理信息

            if not analysis_results or not resume_data:
                return {
                    "success": False,
                    "error": "Missing analysis_results or resume_data"
                }

            # 使用模板生成报告，不调用LLM
            if report_type == "hr_summary":
                report = self._generate_hr_summary_template(analysis_results, resume_data)
            elif report_type == "candidate_summary":
                report = self._generate_candidate_summary_template(analysis_results)
            else:
                report = await self._generate_full_report_template(
                    analysis_results,
                    resume_data,
                    optimization_suggestions,
                    job_requirements,
                    processing_info  # 新增：传递处理信息
                )

            return {
                "success": True,
                "report": report,
                "report_type": report_type,
                "generated_at": datetime.now().isoformat(),
                "agent_name": "ReportAgent"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent_name": "ReportAgent"
            }

    async def _generate_full_report_template(
        self,
        analysis_results: Dict[str, Any],
        resume_data: Dict[str, Any],
        optimization_suggestions: Optional[Any],
        job_requirements: str,
        processing_info: Optional[Dict[str, Any]] = None  # 新增：处理信息
    ) -> Dict[str, Any]:
        """使用模板生成完整报告（调用LLM进行岗位匹配分析）"""
        # 岗位匹配分析（使用LLM）
        job_match_analysis = None
        if job_requirements:
            job_match_analysis = await self._create_job_match_analysis(
                analysis_results, job_requirements, resume_data
            )

        # 获取总分和得分明细
        total_score = analysis_results.get("total_score", 0)
        score_breakdown = self._create_score_breakdown(analysis_results)

        report = {
            # 顶层关键字段
            "total_score": total_score,
            "score_level": self._get_score_level(total_score),
            "score_breakdown": score_breakdown,
            "recommendation": self._create_recommendation(analysis_results),

            # 报告主体
            "executive_summary": self._create_executive_summary(analysis_results, resume_data),
            "detailed_analysis": self._create_detailed_analysis(analysis_results),
            "key_findings": self._extract_key_findings(analysis_results),
            "cleaned_resume": self._create_cleaned_resume_section(resume_data, processing_info),
            "optimization_suggestions": optimization_suggestions if optimization_suggestions else [],
            "job_match_analysis": job_match_analysis,

            # 处理过程
            "processing_summary": self._create_processing_summary(processing_info) if processing_info else None,

            # 元数据（增强版）
            "metadata": self._create_enhanced_metadata(resume_data, job_requirements, processing_info)
        }

        return report

    def _generate_hr_summary_template(
        self,
        analysis_results: Dict[str, Any],
        resume_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """使用模板生成HR摘要（不调用LLM）"""
        return {
            "quick_assessment": self._create_quick_assessment(analysis_results, resume_data),
            "key_highlights": self._extract_key_highlights(analysis_results),
            "risk_factors": self._identify_risk_factors(analysis_results),
            "recommendation": self._create_recommendation(analysis_results),
            "contact_info": self._extract_contact_info(resume_data),
            "score_summary": self._create_quick_overview(analysis_results),
            "metadata": {
                "generated_at": datetime.now().isoformat()
            }
        }

    def _generate_candidate_summary_template(
        self,
        analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """使用模板生成求职者摘要（不调用LLM）"""
        return {
            "overall_evaluation": self._create_overall_evaluation(analysis_results),
            "strengths": self._extract_key_highlights(analysis_results),
            "improvement_areas": self._identify_risk_factors(analysis_results),
            "next_steps": self._suggest_next_steps(analysis_results),
            "score_summary": self._create_quick_overview(analysis_results),
            "metadata": {
                "generated_at": datetime.now().isoformat()
            }
        }

    def _extract_contact_info(self, resume_data: Dict[str, Any]) -> Dict[str, str]:
        """提取联系信息"""
        personal_info = resume_data.get("personal_info", {})
        return {
            "name": personal_info.get("name", ""),
            "phone": personal_info.get("phone", ""),
            "email": personal_info.get("email", "")
        }

    async def _generate_full_report(
        self,
        analysis_results: Dict[str, Any],
        resume_data: Dict[str, Any],
        optimization_suggestions: Optional[Any],
        job_requirements: str
    ) -> Dict[str, Any]:
        """生成完整报告"""
        try:
            user_prompt = prompt_manager.get_user_prompt("report_generation")
            formatted_prompt = user_prompt.format(
                analysis_results=json.dumps(analysis_results, ensure_ascii=False, indent=2),
                resume_data=json.dumps(resume_data, ensure_ascii=False, indent=2),
                job_requirements=job_requirements or "未提供特定岗位要求"
            )

            response = await self.llm.ainvoke([
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": formatted_prompt}
            ])

            response_text = response.content if hasattr(response, 'content') else str(response)

            # 构建结构化报告
            report = {
                "executive_summary": self._create_executive_summary(analysis_results, resume_data),
                "detailed_analysis": self._create_detailed_analysis(analysis_results),
                "key_findings": self._extract_key_findings(analysis_results),
                "optimization_suggestions": optimization_suggestions if optimization_suggestions else [],
                "job_match_analysis": self._create_job_match_analysis(analysis_results, job_requirements) if job_requirements else None,
                "llm_narrative": response_text  # 保留LLM生成的叙述性内容
            }

            return report

        except Exception as e:
            return {"error": str(e)}

    async def _generate_hr_summary(
        self,
        analysis_results: Dict[str, Any],
        resume_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成HR摘要"""
        try:
            user_prompt = prompt_manager.get_user_prompt("hr_summary")
            formatted_prompt = user_prompt.format(
                analysis_results=json.dumps(analysis_results, ensure_ascii=False, indent=2),
                resume_data=json.dumps(resume_data, ensure_ascii=False, indent=2)
            )

            system_prompt = prompt_manager.get_system_prompt("hr_summary")

            response = await self.llm.ainvoke([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": formatted_prompt}
            ])

            response_text = response.content if hasattr(response, 'content') else str(response)

            return {
                "summary_text": response_text,
                "quick_assessment": self._create_quick_assessment(analysis_results, resume_data),
                "key_highlights": self._extract_key_highlights(analysis_results),
                "risk_factors": self._identify_risk_factors(analysis_results),
                "recommendation": self._create_recommendation(analysis_results)
            }

        except Exception as e:
            return {"error": str(e)}

    async def _generate_candidate_summary(
        self,
        analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成求职者摘要"""
        try:
            user_prompt = prompt_manager.get_user_prompt("candidate_summary")
            formatted_prompt = user_prompt.format(
                analysis_results=json.dumps(analysis_results, ensure_ascii=False, indent=2)
            )

            system_prompt = prompt_manager.get_system_prompt("candidate_summary")

            response = await self.llm.ainvoke([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": formatted_prompt}
            ])

            response_text = response.content if hasattr(response, 'content') else str(response)

            return {
                "summary_text": response_text,
                "overall_evaluation": self._create_overall_evaluation(analysis_results),
                "strengths": self._extract_strengths(analysis_results),
                "improvement_areas": self._extract_improvement_areas(analysis_results),
                "next_steps": self._suggest_next_steps(analysis_results)
            }

        except Exception as e:
            return {"error": str(e)}

    def _create_executive_summary(
        self,
        analysis_results: Dict[str, Any],
        resume_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建执行摘要"""
        personal_info = resume_data.get("personal_info", {})
        total_score = analysis_results.get("total_score", 0)

        return {
            "candidate_name": personal_info.get("name", "未知"),
            "total_score": total_score,
            "score_level": self._get_score_level(total_score),
            "contact": {
                "phone": personal_info.get("phone", ""),
                "email": personal_info.get("email", "")
            },
            "quick_overview": self._create_quick_overview(analysis_results)
        }

    def _create_detailed_analysis(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """创建详细分析"""
        return {
            "technical": self._format_dimension_analysis(analysis_results.get("technical_analysis", {})),
            "experience": self._format_dimension_analysis(analysis_results.get("experience_analysis", {})),
            "project": self._format_dimension_analysis(analysis_results.get("project_analysis", {})),
            "soft_skill": self._format_dimension_analysis(analysis_results.get("soft_skill_analysis", {}))
        }

    def _format_dimension_analysis(self, dimension_data: Dict[str, Any]) -> Dict[str, Any]:
        """格式化维度分析数据"""
        return {
            "score": dimension_data.get("score", 0),
            "level": self._get_score_level(dimension_data.get("score", 0)),
            "key_findings": dimension_data.get("关键发现", dimension_data.get("key_findings", [])),
            "strengths": dimension_data.get("亮点", dimension_data.get("strengths", [])),
            "weaknesses": dimension_data.get("不足之处", dimension_data.get("weaknesses", [])),
            "raw_analysis": dimension_data.get("raw_analysis", dimension_data)  # 优先获取原始分析数据，否则使用整个对象
        }

    def _extract_key_findings(self, analysis_results: Dict[str, Any]) -> list:
        """提取关键发现"""
        findings = []

        for dim_key, dim_name in [
            ("technical_analysis", "技术能力"),
            ("experience_analysis", "经验背景"),
            ("project_analysis", "项目经验"),
            ("soft_skill_analysis", "软技能")
        ]:
            dim_data = analysis_results.get(dim_key, {})
            dim_findings = dim_data.get("关键发现", dim_data.get("key_findings", []))
            if dim_findings:
                findings.extend([f"[{dim_name}] {f}" for f in dim_findings])

        return findings[:10]  # 最多返回10条关键发现

    async def _create_job_match_analysis(
        self,
        analysis_results: Dict[str, Any],
        job_requirements: str,
        resume_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        创建岗位匹配分析（使用LLM，失败时使用规则工具）

        Args:
            analysis_results: 简历分析结果
            job_requirements: 岗位要求
            resume_data: 简历数据

        Returns:
            岗位匹配分析结果
        """
        try:
            # 使用LLM进行岗位匹配分析
            if self.verbose:
                print("[INFO] 使用LLM进行岗位匹配分析...")

            formatted_prompt = prompt_manager.format_prompt(
                "job_matching",
                job_requirements=job_requirements,
                resume_data=resume_data,
                analysis_results=analysis_results
            )

            system_prompt = prompt_manager.get_system_prompt("job_matching")

            response = await self.llm.ainvoke([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": formatted_prompt}
            ])

            response_text = response.content if hasattr(response, 'content') else str(response)

            # 解析LLM返回的JSON
            result = self._parse_job_match_response(response_text)

            if result and self._validate_job_match_result(result):
                if self.verbose:
                    print(f"[INFO] LLM岗位匹配分析成功: 匹配分数={result['match_score']}")

                # 添加原始岗位要求到结果中
                result["job_requirements"] = job_requirements
                result["analysis_method"] = "LLM"

                return result
            else:
                if self.verbose:
                    print("[WARNING] LLM返回的岗位匹配结果无效，使用规则工具")

        except Exception as e:
            if self.verbose:
                print(f"[WARNING] LLM岗位匹配分析失败: {e}，使用规则工具")

        # LLM失败或返回无效结果，使用规则工具
        return self._create_job_match_analysis_rules(
            resume_data, job_requirements, analysis_results
        )

    def _parse_job_match_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """解析LLM的岗位匹配响应"""
        import re

        # 尝试提取JSON
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # 尝试直接解析整个响应
            json_str = response_text.strip()

        try:
            result = json.loads(json_str)
            return result
        except json.JSONDecodeError:
            return None

    def _validate_job_match_result(self, result: Dict[str, Any]) -> bool:
        """验证岗位匹配结果的有效性"""
        required_fields = ["match_score", "match_level"]

        for field in required_fields:
            if field not in result:
                return False

        # 验证match_score是数字且在有效范围内
        match_score = result.get("match_score")
        if not isinstance(match_score, (int, float)) or not (0 <= match_score <= 100):
            return False

        # 验证match_level是有效值
        valid_levels = ["高度匹配", "较好匹配", "基本匹配", "部分匹配", "不匹配"]
        if result.get("match_level") not in valid_levels:
            return False

        return True

    def _create_job_match_analysis_rules(
        self,
        resume_data: Dict[str, Any],
        job_requirements: str,
        analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """使用 LLM 工具创建岗位匹配分析"""
        from tools.matching import LLMJobMatcher

        if self.verbose:
            print("[INFO] 使用 LLM 进行岗位匹配分析...")

        # 创建 LLM 匹配器
        matcher = LLMJobMatcher(self.llm)

        result = matcher.match_resume_to_job(
            resume_data=resume_data,
            job_requirements=job_requirements,
            analysis_results=analysis_results
        )

        # 添加原始岗位要求和分析方法
        result["job_requirements"] = job_requirements
        result["analysis_method"] = "LLM"

        return result

    def _create_quick_assessment(
        self,
        analysis_results: Dict[str, Any],
        resume_data: Dict[str, Any]
    ) -> str:
        """创建快速评估"""
        total_score = analysis_results.get("total_score", 0)
        level = self._get_score_level(total_score)
        name = resume_data.get("personal_info", {}).get("name", "候选人")

        return f"{name} - 总分{total_score}分，属于{level}水平"

    def _extract_key_highlights(self, analysis_results: Dict[str, Any]) -> list:
        """提取关键亮点"""
        highlights = []

        for dim_key in ["technical_analysis", "experience_analysis", "project_analysis", "soft_skill_analysis"]:
            dim_data = analysis_results.get(dim_key, {})
            dim_strengths = dim_data.get("亮点", dim_data.get("strengths", []))
            if dim_strengths:
                highlights.extend(dim_strengths)

        return highlights[:5]

    def _identify_risk_factors(self, analysis_results: Dict[str, Any]) -> list:
        """识别风险因素"""
        risks = []

        for dim_key in ["technical_analysis", "experience_analysis", "project_analysis", "soft_skill_analysis"]:
            dim_data = analysis_results.get(dim_key, {})
            dim_weaknesses = dim_data.get("不足之处", dim_data.get("weaknesses", []))
            if dim_weaknesses:
                risks.extend(dim_weaknesses)

        return risks[:5]

    def _create_recommendation(self, analysis_results: Dict[str, Any]) -> str:
        """创建推荐意见"""
        total_score = analysis_results.get("total_score", 0)

        if total_score >= 85:
            return "强烈推荐 - 候选人综合能力优秀"
        elif total_score >= 75:
            return "推荐 - 候选人综合能力良好"
        elif total_score >= 65:
            return "谨慎推荐 - 候选人基本符合要求"
        else:
            return "不推荐 - 候选人能力有待提升"

    def _create_overall_evaluation(self, analysis_results: Dict[str, Any]) -> str:
        """创建总体评价"""
        total_score = analysis_results.get("total_score", 0)
        return f"您的简历综合评分为{total_score}分，{self._get_score_level(total_score)}水平。"

    def _extract_strengths(self, analysis_results: Dict[str, Any]) -> list:
        """提取优势"""
        return self._extract_key_highlights(analysis_results)

    def _extract_improvement_areas(self, analysis_results: Dict[str, Any]) -> list:
        """提取改进领域"""
        return self._identify_risk_factors(analysis_results)

    def _suggest_next_steps(self, analysis_results: Dict[str, Any]) -> list:
        """建议下一步行动"""
        return [
            "根据优化建议逐步改进简历内容",
            "突出项目经验中的量化成果",
            "补充技能的具体应用场景",
            "优化简历的结构和表达方式"
        ]

    def _create_quick_overview(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """创建快速概览"""
        score_breakdown = analysis_results.get("score_breakdown", {})

        return {
            "technical": score_breakdown.get("technical", {}).get("score", 0),
            "experience": score_breakdown.get("experience", {}).get("score", 0),
            "project": score_breakdown.get("project", {}).get("score", 0),
            "soft_skill": score_breakdown.get("soft_skill", {}).get("score", 0)
        }

    def _create_score_breakdown(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建得分明细（包含权重和加权得分）

        Args:
            analysis_results: 分析结果

        Returns:
            得分明细
        """
        score_breakdown = analysis_results.get("score_breakdown", {})
        total_score = analysis_results.get("total_score", 0)

        # 维度配置
        dimensions = [
            ("technical", "技术能力", 0.25),
            ("experience", "经验背景", 0.20),
            ("project", "项目经验", 0.40),
            ("soft_skill", "软技能", 0.15)
        ]

        breakdown = {}
        weight_sum = 0

        for key, name, weight in dimensions:
            dim_data = score_breakdown.get(key, {})
            score = dim_data.get("score", 0)
            weighted_score = score * weight
            weight_sum += weighted_score

            breakdown[key] = {
                "name": name,
                "score": score,
                "weight": weight,
                "weighted_score": weighted_score,
                "contribution_percentage": (weighted_score / total_score * 100) if total_score > 0 else 0
            }

        return {
            "dimensions": breakdown,
            "weight_config": {
                "technical": 0.25,
                "experience": 0.20,
                "project": 0.40,
                "soft_skill": 0.15
            },
            "total_weighted_score": weight_sum,
            "normalization_factor": 1.0  # 归一化因子
        }

    def _create_enhanced_metadata(
        self,
        resume_data: Dict[str, Any],
        job_requirements: str,
        processing_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        创建增强的元数据

        Args:
            resume_data: 简历数据
            job_requirements: 岗位要求
            processing_info: 处理信息

        Returns:
            增强的元数据
        """
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "job_requirements": job_requirements or "未提供特定岗位要求",
            "report_version": "2.0",
            "generator": "AI_HR2 Resume Analysis System"
        }

        # 添加文件信息
        personal_info = resume_data.get("personal_info", {})
        if personal_info:
            metadata["candidate_name"] = personal_info.get("name", "未知")

        # 添加解析信息
        if processing_info:
            intermediate_results = processing_info.get("intermediate_results", {})
            parsed_info = intermediate_results.get("parsed", {})
            if parsed_info:
                metadata["parse_info"] = {
                    "parse_method": parsed_info.get("parse_method", "unknown"),
                    "fields_count": parsed_info.get("fields_count", 0)
                }

        return metadata

    def _get_score_level(self, score: float) -> str:
        """获取分数等级"""
        if score >= 90:
            return "优秀"
        elif score >= 80:
            return "良好"
        elif score >= 70:
            return "合格"
        elif score >= 60:
            return "及格"
        else:
            return "不及格"

    def _get_match_level(self, score: float) -> str:
        """获取匹配等级"""
        if score >= 90:
            return "高度匹配"
        elif score >= 80:
            return "较好匹配"
        elif score >= 70:
            return "基本匹配"
        elif score >= 60:
            return "部分匹配"
        else:
            return "不匹配"

    def _create_processing_summary(self, processing_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建处理过程摘要

        Args:
            processing_info: 处理信息，包含步骤执行、去重报告等

        Returns:
            处理过程摘要
        """
        summary = {
            "steps_completed": processing_info.get("steps_completed", []),
            "steps_failed": processing_info.get("steps_failed", []),
            "steps_summary": []
        }

        # 提取各步骤的摘要信息
        intermediate_results = processing_info.get("intermediate_results", {})

        for step_name in ["parsed", "structured", "cleaned", "deduplicated"]:
            step_info = intermediate_results.get(step_name, {})
            if step_info:
                step_summary = {
                    "step": step_name,
                    "status": "completed"
                }

                if step_name == "parsed":
                    step_summary["fields_count"] = step_info.get("fields_count", 0)
                    step_summary["parse_method"] = step_info.get("parse_method", "unknown")

                elif step_name == "structured":
                    step_summary["normalized"] = step_info.get("normalized", False)
                    step_summary["fields_count"] = step_info.get("fields_count", 0)

                elif step_name == "cleaned":
                    step_summary["fields_count"] = step_info.get("fields_count", 0)
                    step_summary["missing_values_handled"] = step_info.get("missing_values_handled", 0)

                elif step_name == "deduplicated":
                    step_summary["deduplication_performed"] = step_info.get("deduplication_performed", False)

                    # 添加去重详情
                    if step_info.get("deduplication_summary"):
                        dedup_sum = step_info["deduplication_summary"]
                        step_summary["deduplication_summary"] = {
                            "total_items_processed": dedup_sum.get("total_items_processed", 0),
                            "total_duplicates_removed": dedup_sum.get("total_duplicates_removed", 0),
                            "items_merged": dedup_sum.get("items_merged", 0)
                        }

                    # 添加具体去重信息
                    step_summary["skills_dedup"] = step_info.get("skills", {})
                    step_summary["projects_dedup"] = step_info.get("projects", {})
                    step_summary["work_experience_dedup"] = step_info.get("work_experience", {})

                    # 保留原始去重报告文本
                    if step_info.get("deduplication_report_text"):
                        step_summary["deduplication_report_text"] = step_info["deduplication_report_text"]

                summary["steps_summary"].append(step_summary)

        return summary

    def _create_cleaned_resume_section(
        self,
        resume_data: Dict[str, Any],
        processing_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        创建清洗后的简历信息部分

        Args:
            resume_data: 简历数据
            processing_info: 处理信息（可选）

        Returns:
            清洗后的简历信息
        """
        cleaned_section = {
            "personal_info": self._format_personal_info(resume_data.get("personal_info", {})),
            "skills": self._format_skills(resume_data.get("skills", [])),
            "work_experience": self._format_work_experience(resume_data.get("work_experience", [])),
            "projects": self._format_projects(resume_data.get("projects", [])),
            "education": self._format_education(resume_data.get("education", []))
        }

        # 添加清洗和去重的统计信息
        if processing_info:
            intermediate_results = processing_info.get("intermediate_results", {})

            # 清洗统计
            cleaned_info = intermediate_results.get("cleaned", {})
            if cleaned_info:
                cleaned_section["cleaning_stats"] = {
                    "fields_processed": cleaned_info.get("fields_count", 0),
                    "missing_values_handled": cleaned_info.get("missing_values_handled", 0)
                }

            # 去重统计
            dedup_info = intermediate_results.get("deduplicated", {})
            if dedup_info and dedup_info.get("deduplication_performed"):
                dedup_stats = {
                    "deduplication_performed": True,
                    "skills": {
                        "original_count": len(resume_data.get("skills", [])) + dedup_info.get("skills", {}).get("removed", 0),
                        "removed": dedup_info.get("skills", {}).get("removed", 0),
                        "merged": dedup_info.get("skills", {}).get("merged", 0),
                        "final_count": len(resume_data.get("skills", []))
                    },
                    "projects": {
                        "original_count": len(resume_data.get("projects", [])) + dedup_info.get("projects", {}).get("removed", 0),
                        "removed": dedup_info.get("projects", {}).get("removed", 0),
                        "final_count": len(resume_data.get("projects", []))
                    },
                    "work_experience": {
                        "original_count": len(resume_data.get("work_experience", [])) + dedup_info.get("work_experience", {}).get("removed", 0),
                        "removed": dedup_info.get("work_experience", {}).get("removed", 0),
                        "final_count": len(resume_data.get("work_experience", []))
                    }
                }

                # 添加去重摘要
                if dedup_info.get("deduplication_summary"):
                    dedup_sum = dedup_info["deduplication_summary"]
                    dedup_stats["summary"] = {
                        "total_items_processed": dedup_sum.get("total_items_processed", 0),
                        "total_duplicates_removed": dedup_sum.get("total_duplicates_removed", 0),
                        "items_merged": dedup_sum.get("items_merged", 0)
                    }

                cleaned_section["deduplication_stats"] = dedup_stats

        return cleaned_section

    def _format_personal_info(self, personal_info: Dict[str, Any]) -> Dict[str, Any]:
        """格式化个人信息"""
        return {
            "name": personal_info.get("name", ""),
            "phone": personal_info.get("phone", ""),
            "email": personal_info.get("email", ""),
            "location": personal_info.get("location", ""),
            "gender": personal_info.get("gender", ""),
            "birth_date": personal_info.get("birth_date", "")
        }

    def _format_skills(self, skills: list) -> list:
        """格式化技能列表"""
        formatted = []
        for skill in skills:
            formatted.append({
                "name": skill.get("name", ""),
                "level": skill.get("level", ""),
                "category": skill.get("category", "")
            })
        return formatted

    def _format_work_experience(self, work_exp: list) -> list:
        """格式化工作经历（包含完整字段）"""
        formatted = []
        for exp in work_exp:
            formatted.append({
                "company": exp.get("company", ""),
                "position": exp.get("position", ""),
                "start_time": exp.get("start_time", exp.get("start_date", "")),
                "end_time": exp.get("end_time", exp.get("end_date", "")),
                "description": exp.get("description", ""),
                "industry": exp.get("industry"),
                "company_scale": exp.get("company_scale"),
                "achievements": exp.get("achievements", [])
            })
        return formatted

    def _format_projects(self, projects: list) -> list:
        """格式化项目经验（包含完整字段）"""
        formatted = []
        for proj in projects:
            formatted.append({
                "name": proj.get("name", ""),
                "role": proj.get("role", ""),
                "start_time": proj.get("start_time", proj.get("start_date", "")),
                "end_time": proj.get("end_time", proj.get("end_date", "")),
                "tech_stack": proj.get("tech_stack", []),
                "description": proj.get("description", ""),
                "team_size": proj.get("team_size"),
                "achievements": proj.get("achievements", []),
                # 保留原始项目数据中的其他字段（如interview_questions、score_breakdown等）
                "interview_questions": proj.get("interview_questions", []),
                "score_breakdown": proj.get("score_breakdown"),
                "score": proj.get("score")
            })
        return formatted

    def _format_education(self, education: list) -> list:
        """格式化教育背景"""
        formatted = []
        for edu in education:
            formatted.append({
                "school": edu.get("school", ""),
                "degree": edu.get("degree", ""),
                "major": edu.get("major", ""),
                "start_time": edu.get("start_time", edu.get("start_date", "")),
                "end_time": edu.get("end_time", edu.get("end_date", ""))
            })
        return formatted

    def to_dict(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """将报告转换为字典格式"""
        return report

    def to_json(self, report: Dict[str, Any]) -> str:
        """将报告转换为JSON格式"""
        return json.dumps(report, ensure_ascii=False, indent=2)

    def to_markdown(self, report: Dict[str, Any]) -> str:
        """将报告转换为Markdown格式"""
        md_lines = ["# 简历分析报告\n"]

        # 执行摘要
        exec_summary = report.get("executive_summary", {})
        if exec_summary:
            md_lines.append("## 执行摘要\n")
            md_lines.append(f"- **候选人**: {exec_summary.get('candidate_name', '未知')}")
            md_lines.append(f"- **总分**: {exec_summary.get('total_score', 0)}")
            md_lines.append(f"- **等级**: {exec_summary.get('score_level', '未知')}\n")

        # 新增：数据处理过程
        processing = report.get("processing_summary", {})
        if processing and processing.get("steps_summary"):
            md_lines.append("## 数据处理过程\n")

            # 步骤执行情况
            steps_completed = processing.get("steps_completed", [])
            steps_failed = processing.get("steps_failed", [])

            if steps_completed:
                md_lines.append(f"**完成步骤**: {', '.join(steps_completed)}")

            if steps_failed:
                md_lines.append(f"**失败步骤**: {', '.join(steps_failed)}")

            md_lines.append("")

            # 各步骤详情
            md_lines.append("### 处理步骤详情\n")

            step_name_map = {
                "parsed": "简历解析",
                "structured": "结构映射",
                "cleaned": "数据清洗",
                "deduplicated": "数据去重"
            }

            for step in processing["steps_summary"]:
                step_name = step.get("step", "")
                display_name = step_name_map.get(step_name, step_name)
                md_lines.append(f"#### {display_name}")

                if step_name == "parsed":
                    md_lines.append(f"- 解析方法: {step.get('parse_method', 'unknown')}")
                    md_lines.append(f"- 识别字段数: {step.get('fields_count', 0)}")

                elif step_name == "structured":
                    md_lines.append(f"- 标准化完成: {'是' if step.get('normalized') else '否'}")
                    md_lines.append(f"- 映射字段数: {step.get('fields_count', 0)}")

                elif step_name == "cleaned":
                    md_lines.append(f"- 处理字段数: {step.get('fields_count', 0)}")
                    md_lines.append(f"- 缺失值处理: {step.get('missing_values_handled', 0)} 项")

                elif step_name == "deduplicated":
                    if step.get("deduplication_performed"):
                        dedup_sum = step.get("deduplication_summary", {})
                        md_lines.append(f"- 处理项数: {dedup_sum.get('total_items_processed', 0)}")
                        md_lines.append(f"- 删除重复: {dedup_sum.get('total_duplicates_removed', 0)} 项")
                        md_lines.append(f"- 合并项数: {dedup_sum.get('items_merged', 0)} 项")

                        # 具体去重信息
                        skills_dedup = step.get("skills_dedup", {})
                        if skills_dedup:
                            removed = skills_dedup.get("removed", 0)
                            merged = skills_dedup.get("merged", 0)
                            if removed > 0 or merged > 0:
                                md_lines.append(f"  - 技能去重: 删除{removed}项，合并{merged}项")

                        projects_dedup = step.get("projects_dedup", {})
                        if projects_dedup.get("removed", 0) > 0:
                            md_lines.append(f"  - 项目去重: 删除{projects_dedup['removed']}项")

                        work_dedup = step.get("work_experience_dedup", {})
                        if work_dedup.get("removed", 0) > 0:
                            md_lines.append(f"  - 工作经历去重: 删除{work_dedup['removed']}项")

                        # 原始去重报告
                        if step.get("deduplication_report_text"):
                            md_lines.append("\n**去重详情**:")
                            md_lines.append(f"```\n{step['deduplication_report_text']}\n```")
                    else:
                        md_lines.append("- 未执行去重（无需去重或去重失败）")

                md_lines.append("")

        # 清洗后的简历信息
        cleaned_resume = report.get("cleaned_resume", {})
        if cleaned_resume:
            md_lines.append("## 清洗后的简历信息\n")

            # 基本信息
            personal_info = cleaned_resume.get("personal_info", {})
            if personal_info and any(personal_info.values()):
                md_lines.append("### 基本信息")
                if personal_info.get("name"):
                    md_lines.append(f"- **姓名**: {personal_info['name']}")
                if personal_info.get("phone"):
                    md_lines.append(f"- **手机**: {personal_info['phone']}")
                if personal_info.get("email"):
                    md_lines.append(f"- **邮箱**: {personal_info['email']}")
                if personal_info.get("location"):
                    md_lines.append(f"- **所在地**: {personal_info['location']}")
                if personal_info.get("gender"):
                    md_lines.append(f"- **性别**: {personal_info['gender']}")
                if personal_info.get("birth_date"):
                    md_lines.append(f"- **出生日期**: {personal_info['birth_date']}")
                md_lines.append("")

            # 技能清单
            skills = cleaned_resume.get("skills", [])
            if skills:
                md_lines.append("### 技能清单")
                for skill in skills:
                    name = skill.get("name", "")
                    level = skill.get("level", "")
                    category = skill.get("category", "")
                    level_text = f" ({level})" if level else ""
                    category_text = f" [{category}]" if category else ""
                    md_lines.append(f"- {name}{level_text}{category_text}")
                md_lines.append("")

            # 工作经历
            work_exp = cleaned_resume.get("work_experience", [])
            if work_exp:
                md_lines.append("### 工作经历")
                for exp in work_exp:
                    company = exp.get("company", "")
                    position = exp.get("position", "")
                    start = exp.get("start_time", "")
                    end = exp.get("end_time", "")
                    desc = exp.get("description", "")

                    md_lines.append(f"#### {company} | {position}")
                    md_lines.append(f"- **时间**: {start} ~ {end}")
                    if desc:
                        md_lines.append(f"- **描述**: {desc}")
                    md_lines.append("")

            # 项目经验
            projects = cleaned_resume.get("projects", [])
            if projects:
                md_lines.append("### 项目经验")
                for proj in projects:
                    name = proj.get("name", "")
                    role = proj.get("role", "")
                    start = proj.get("start_time", "")
                    end = proj.get("end_time", "")
                    tech_stack = proj.get("tech_stack", [])
                    desc = proj.get("description", "")

                    md_lines.append(f"#### {name}")
                    if role:
                        md_lines.append(f"- **角色**: {role}")
                    if start or end:
                        md_lines.append(f"- **时间**: {start} ~ {end}")
                    if tech_stack:
                        md_lines.append(f"- **技术栈**: {', '.join(tech_stack)}")
                    if desc:
                        md_lines.append(f"- **描述**: {desc}")
                    md_lines.append("")

            # 教育背景
            education = cleaned_resume.get("education", [])
            if education:
                md_lines.append("### 教育背景")
                for edu in education:
                    school = edu.get("school", "")
                    degree = edu.get("degree", "")
                    major = edu.get("major", "")
                    start = edu.get("start_time", "")
                    end = edu.get("end_time", "")

                    md_lines.append(f"#### {school}")
                    md_lines.append(f"- **学历**: {degree}")
                    if major:
                        md_lines.append(f"- **专业**: {major}")
                    if start or end:
                        md_lines.append(f"- **时间**: {start} ~ {end}")
                    md_lines.append("")

            # 清洗和去重统计
            if cleaned_resume.get("cleaning_stats") or cleaned_resume.get("deduplication_stats"):
                md_lines.append("### 数据清洗统计")

                cleaning_stats = cleaned_resume.get("cleaning_stats", {})
                if cleaning_stats:
                    md_lines.append("**清洗统计**:")
                    md_lines.append(f"- 处理字段数: {cleaning_stats.get('fields_processed', 0)}")
                    md_lines.append(f"- 缺失值处理: {cleaning_stats.get('missing_values_handled', 0)} 项")
                    md_lines.append("")

                dedup_stats = cleaned_resume.get("deduplication_stats", {})
                if dedup_stats:
                    md_lines.append("**去重统计**:")

                    if dedup_stats.get("summary"):
                        summary = dedup_stats["summary"]
                        md_lines.append(f"- 总处理项数: {summary.get('total_items_processed', 0)}")
                        md_lines.append(f"- 删除重复项: {summary.get('total_duplicates_removed', 0)}")
                        md_lines.append(f"- 合并项数: {summary.get('items_merged', 0)}")
                        md_lines.append("")

                    # 各字段去重详情
                    for field in ["skills", "projects", "work_experience"]:
                        field_dedup = dedup_stats.get(field, {})
                        if field_dedup and field_dedup.get("removed", 0) > 0:
                            field_name_map = {
                                "skills": "技能",
                                "projects": "项目",
                                "work_experience": "工作经历"
                            }
                            field_name = field_name_map.get(field, field)
                            md_lines.append(f"- **{field_name}去重**:")
                            md_lines.append(f"  - 原始数量: {field_dedup.get('original_count', 0)}")
                            md_lines.append(f"  - 删除重复: {field_dedup.get('removed', 0)}")
                            if field_dedup.get("merged", 0) > 0:
                                md_lines.append(f"  - 合并重复: {field_dedup.get('merged', 0)}")
                            md_lines.append(f"  - 最终数量: {field_dedup.get('final_count', 0)}")

                    md_lines.append("")

        # 详细分析
        detailed = report.get("detailed_analysis", {})
        if detailed:
            md_lines.append("## 详细分析\n")
            for dim_name, dim_data in detailed.items():
                # 中文名称映射
                dim_name_map = {
                    "technical": "技术能力",
                    "experience": "经验背景",
                    "project": "项目经验",
                    "soft_skill": "软技能"
                }
                chinese_name = dim_name_map.get(dim_name, dim_name.upper())

                md_lines.append(f"### {chinese_name}")
                md_lines.append(f"- 得分: {dim_data.get('score', 0)}")
                md_lines.append(f"- 等级: {dim_data.get('level', '未知')}")

                # 关键发现
                key_findings = dim_data.get("key_findings", [])
                if key_findings:
                    md_lines.append("\n**关键发现**:")
                    for finding in key_findings:
                        md_lines.append(f"  - {finding}")

                # 亮点
                strengths = dim_data.get("strengths", [])
                if strengths:
                    md_lines.append("\n**亮点**:")
                    for strength in strengths:
                        md_lines.append(f"  - {strength}")

                # 不足
                weaknesses = dim_data.get("weaknesses", [])
                if weaknesses:
                    md_lines.append("\n**待改进**:")
                    for weakness in weaknesses:
                        md_lines.append(f"  - {weakness}")

                md_lines.append("")

        # 关键发现（整体）
        findings = report.get("key_findings", [])
        if findings:
            md_lines.append("## 关键发现\n")
            for finding in findings:
                md_lines.append(f"- {finding}")
            md_lines.append("")

        # 优化建议
        suggestions = report.get("optimization_suggestions", [])
        if suggestions:
            md_lines.append("## 优化建议\n")
            for i, suggestion in enumerate(suggestions, 1):
                priority = suggestion.get("priority", "中")
                category = suggestion.get("category", "建议")

                priority_emoji = {
                    "高": "🔴",
                    "中": "🟡",
                    "低": "🟢"
                }.get(priority, "")

                md_lines.append(f"### {i}. {priority_emoji} {category} [{priority}优先级]")
                md_lines.append(f"{suggestion.get('suggestion', '')}")

                if suggestion.get("example"):
                    md_lines.append(f"\n**示例**: {suggestion['example']}")

                md_lines.append("")

        # 元数据
        metadata = report.get("metadata", {})
        if metadata:
            md_lines.append("---\n")
            md_lines.append(f"**报告生成时间**: {metadata.get('generated_at', '未知')}")
            if metadata.get("job_requirements"):
                md_lines.append(f"**岗位要求**: {metadata['job_requirements']}")

        return "\n".join(md_lines)

    def to_html(self, report: Dict[str, Any]) -> str:
        """将报告转换为HTML格式"""
        html_parts = []

        # HTML头部和CSS样式
        html_parts.append("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>简历分析报告</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }

        h2 {
            color: #34495e;
            margin-top: 30px;
            margin-bottom: 15px;
            padding-left: 10px;
            border-left: 4px solid #3498db;
        }

        h3 {
            color: #555;
            margin-top: 20px;
            margin-bottom: 10px;
        }

        h4 {
            color: #666;
            margin-top: 15px;
            margin-bottom: 8px;
        }

        .score-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }

        .score-box .total-score {
            font-size: 48px;
            font-weight: bold;
        }

        .score-box .score-level {
            font-size: 24px;
            margin-top: 10px;
        }

        .score-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }

        .score-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #3498db;
        }

        .score-card .dimension-name {
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }

        .score-card .score-value {
            font-size: 24px;
            color: #3498db;
            font-weight: bold;
        }

        .info-section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            margin: 15px 0;
        }

        .info-list {
            list-style: none;
            padding: 0;
        }

        .info-list li {
            padding: 8px 0;
            border-bottom: 1px solid #e0e0e0;
        }

        .info-list li:last-child {
            border-bottom: none;
        }

        .info-list strong {
            color: #2c3e50;
            display: inline-block;
            min-width: 100px;
        }

        .skill-tag {
            display: inline-block;
            background: #3498db;
            color: white;
            padding: 5px 12px;
            margin: 5px;
            border-radius: 15px;
            font-size: 14px;
        }

        .skill-tag.level-精通 {
            background: #27ae60;
        }

        .skill-tag.level-熟练 {
            background: #3498db;
        }

        .skill-tag.level-了解 {
            background: #95a5a6;
        }

        .findings-list, .strengths-list, .weaknesses-list {
            list-style: none;
            padding: 0;
        }

        .findings-list li, .strengths-list li, .weaknesses-list li {
            padding: 10px;
            margin: 5px 0;
            border-radius: 4px;
        }

        .strengths-list li {
            background: #d4edda;
            border-left: 4px solid #28a745;
        }

        .weaknesses-list li {
            background: #f8d7da;
            border-left: 4px solid #dc3545;
        }

        .recommendation-card {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
        }

        .recommendation-card .priority-high {
            border-left-color: #dc3545;
        }

        .recommendation-card .priority-low {
            border-left-color: #28a745;
        }

        .action-steps {
            margin: 10px 0;
            padding-left: 20px;
        }

        .action-steps li {
            margin: 8px 0;
            line-height: 1.6;
        }

        .example-box {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-left: 3px solid #17a2b8;
            padding: 12px;
            margin: 10px 0;
            border-radius: 4px;
            font-size: 14px;
            line-height: 1.6;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }

        .stat-box {
            background: white;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
            border: 1px solid #e0e0e0;
        }

        .stat-box .stat-value {
            font-size: 28px;
            font-weight: bold;
            color: #3498db;
        }

        .stat-box .stat-label {
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        }

        .match-score {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 8px;
            margin: 15px 0;
        }

        .match-score .score {
            font-size: 48px;
            font-weight: bold;
        }

        .match-score .level {
            font-size: 24px;
            margin-top: 10px;
        }

        .tech-stack {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 10px 0;
        }

        .tech-stack span {
            background: #e3f2fd;
            color: #1976d2;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 13px;
        }

        .processing-step {
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-radius: 6px;
            border-left: 4px solid #3498db;
        }

        .metadata {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e0e0e0;
            color: #666;
            font-size: 14px;
        }

        .section-divider {
            border: none;
            border-top: 1px solid #e0e0e0;
            margin: 30px 0;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }

        table th, table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }

        table th {
            background: #f8f9fa;
            font-weight: bold;
            color: #2c3e50;
        }

        @media print {
            body {
                background: white;
                padding: 0;
            }

            .container {
                box-shadow: none;
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
""")

        # 标题
        html_parts.append("<h1>📋 简历分析报告</h1>")

        # 执行摘要
        exec_summary = report.get("executive_summary", {})
        if exec_summary:
            html_parts.append("<h2>📊 执行摘要</h2>")
            html_parts.append('<div class="score-box">')
            html_parts.append(f'<div class="total-score">总分: {exec_summary.get("total_score", 0)} 分</div>')
            html_parts.append(f'<div class="score-level">等级: {exec_summary.get("score_level", "未知")}</div>')
            html_parts.append('</div>')

            # 各维度得分
            quick_overview = exec_summary.get("quick_overview", {})
            if quick_overview:
                html_parts.append('<div class="score-grid">')
                for dim_name, dim_label in [
                    ("technical", "技术能力"),
                    ("experience", "经验背景"),
                    ("project", "项目经验"),
                    ("soft_skill", "软技能")
                ]:
                    score = quick_overview.get(dim_name, 0)
                    html_parts.append(f'''
                    <div class="score-card">
                        <div class="dimension-name">{dim_label}</div>
                        <div class="score-value">{score} 分</div>
                    </div>
                    ''')
                html_parts.append('</div>')


        # 清洗后的简历信息
        cleaned_resume = report.get("cleaned_resume", {})
        if cleaned_resume:
            html_parts.append("<h2>👤 清洗后的简历信息</h2>")

            # 基本信息
            personal_info = cleaned_resume.get("personal_info", {})
            if personal_info and any(personal_info.values()):
                html_parts.append("<h3>基本信息</h3>")
                html_parts.append('<div class="info-section">')
                html_parts.append('<ul class="info-list">')
                for key, label in [
                    ("name", "姓名"),
                    ("phone", "手机"),
                    ("email", "邮箱"),
                    ("location", "所在地"),
                    ("gender", "性别"),
                    ("birth_date", "出生日期")
                ]:
                    value = personal_info.get(key, "")
                    if value:
                        html_parts.append(f'<li><strong>{label}:</strong> {value}</li>')
                html_parts.append('</ul></div>')

            # 技能清单
            skills = cleaned_resume.get("skills", [])
            if skills:
                html_parts.append("<h3>技能清单</h3>")
                html_parts.append('<div class="skills-container">')
                for skill in skills:
                    name = skill.get("name", "")
                    level = skill.get("level", "")
                    level_class = f"level-{level}" if level in ["精通", "熟练", "了解"] else ""
                    level_text = f" ({level})" if level else ""
                    html_parts.append(f'<span class="skill-tag {level_class}">{name}{level_text}</span>')
                html_parts.append('</div>')

            # 工作经历
            work_exp = cleaned_resume.get("work_experience", [])
            if work_exp:
                html_parts.append("<h3>工作经历</h3>")
                for exp in work_exp:
                    html_parts.append('<div class="info-section">')
                    html_parts.append(f'<h4>{exp.get("company", "")} | {exp.get("position", "")}</h4>')
                    html_parts.append(f'<p><strong>时间:</strong> {exp.get("start_time", "")} ~ {exp.get("end_time", "")}</p>')
                    desc = exp.get("description", "")
                    if desc:
                        html_parts.append(f'<p><strong>描述:</strong> {desc}</p>')
                    html_parts.append('</div>')

            # 项目经验
            projects = cleaned_resume.get("projects", [])
            if projects:
                html_parts.append("<h3>项目经验</h3>")
                for proj in projects:
                    html_parts.append('<div class="info-section">')
                    html_parts.append(f'<h4>{proj.get("name", "")}</h4>')
                    role = proj.get("role", "")
                    if role:
                        html_parts.append(f'<p><strong>角色:</strong> {role}</p>')
                    tech_stack = proj.get("tech_stack", [])
                    if tech_stack:
                        html_parts.append('<p><strong>技术栈:</strong></p>')
                        html_parts.append('<div class="tech-stack">')
                        for tech in tech_stack:
                            html_parts.append(f'<span>{tech}</span>')
                        html_parts.append('</div>')
                    desc = proj.get("description", "")
                    if desc:
                        html_parts.append(f'<p><strong>描述:</strong> {desc}</p>')
                    html_parts.append('</div>')

            # 教育背景
            education = cleaned_resume.get("education", [])
            if education:
                html_parts.append("<h3>教育背景</h3>")
                for edu in education:
                    html_parts.append('<div class="info-section">')
                    html_parts.append(f'<h4>{edu.get("school", "")}</h4>')
                    html_parts.append(f'<p><strong>学历:</strong> {edu.get("degree", "")}</p>')
                    major = edu.get("major", "")
                    if major:
                        html_parts.append(f'<p><strong>专业:</strong> {major}</p>')
                    start = edu.get("start_time", "")
                    end = edu.get("end_time", "")
                    if start or end:
                        html_parts.append(f'<p><strong>时间:</strong> {start} ~ {end}</p>')
                    html_parts.append('</div>')


        # 详细分析（从cleaned_resume获取raw_analysis数据）
        cleaned_resume = report.get("cleaned_resume", {})
        detailed = report.get("detailed_analysis", {})

        if detailed:
            html_parts.append("<h2>📈 详细分析</h2>")

            # 技术能力详细分析
            if "technical" in detailed:
                tech_data = detailed["technical"]
                html_parts.append("<h3>🔧 技术能力</h3>")
                html_parts.append(f'<div class="score-card">')
                html_parts.append(f'<div class="dimension-name">技术能力总分</div>')
                html_parts.append(f'<div class="score-value">{tech_data.get("score", 0)} 分</div>')
                html_parts.append(f'<div>等级: {tech_data.get("level", "未知")}</div>')
                html_parts.append('</div>')

                # 关键发现
                key_findings = tech_data.get("key_findings", [])
                if key_findings:
                    html_parts.append('<h4>关键发现</h4>')
                    html_parts.append('<ul class="findings-list">')
                    for finding in key_findings:
                        html_parts.append(f'<li>{finding}</li>')
                    html_parts.append('</ul>')

                # 亮点
                strengths = tech_data.get("strengths", [])
                if strengths:
                    html_parts.append('<h4>亮点</h4>')
                    html_parts.append('<ul class="strengths-list">')
                    for strength in strengths:
                        html_parts.append(f'<li>{strength}</li>')
                    html_parts.append('</ul>')

                # 不足
                weaknesses = tech_data.get("weaknesses", [])
                if weaknesses:
                    html_parts.append('<h4>待改进</h4>')
                    html_parts.append('<ul class="weaknesses-list">')
                    for weakness in weaknesses:
                        html_parts.append(f'<li>{weakness}</li>')
                    html_parts.append('</ul>')

            # 经验背景详细分析
            if "experience" in detailed:
                exp_data = detailed["experience"]
                html_parts.append("<h3>💼 经验背景</h3>")
                html_parts.append(f'<div class="score-card">')
                html_parts.append(f'<div class="dimension-name">经验背景总分</div>')
                html_parts.append(f'<div class="score-value">{exp_data.get("score", 0)} 分</div>')
                html_parts.append(f'<div>等级: {exp_data.get("level", "未知")}</div>')
                html_parts.append('</div>')

                # 关键发现
                key_findings = exp_data.get("key_findings", [])
                if key_findings:
                    html_parts.append('<h4>关键发现</h4>')
                    html_parts.append('<ul class="findings-list">')
                    for finding in key_findings:
                        html_parts.append(f'<li>{finding}</li>')
                    html_parts.append('</ul>')

                # 亮点
                strengths = exp_data.get("strengths", [])
                if strengths:
                    html_parts.append('<h4>亮点</h4>')
                    html_parts.append('<ul class="strengths-list">')
                    for strength in strengths:
                        html_parts.append(f'<li>{strength}</li>')
                    html_parts.append('</ul>')

                # 不足
                weaknesses = exp_data.get("weaknesses", [])
                if weaknesses:
                    html_parts.append('<h4>待改进</h4>')
                    html_parts.append('<ul class="weaknesses-list">')
                    for weakness in weaknesses:
                        html_parts.append(f'<li>{weakness}</li>')
                    html_parts.append('</ul>')

            # 项目经验详细分析（包含项目详细评分）
            if "project" in detailed:
                proj_data = detailed["project"]
                html_parts.append("<h3>📁 项目经验</h3>")
                html_parts.append(f'<div class="score-card">')
                html_parts.append(f'<div class="dimension-name">项目经验总分</div>')
                html_parts.append(f'<div class="score-value">{proj_data.get("score", 0)} 分</div>')
                html_parts.append(f'<div>等级: {proj_data.get("level", "未知")}</div>')
                html_parts.append('</div>')

                # 项目详细评分（从raw_analysis获取）
                raw_analysis = proj_data.get("raw_analysis", {})
                project_scores = raw_analysis.get("project_scores", [])

                if project_scores:
                    html_parts.append('<h4>项目详细评分</h4>')
                    html_parts.append('<p><strong>评分标准：</strong>基础分(10) + 技术栈分(15) + 描述质量分(15) + 规模分(10) = 最高50分</p>')

                    for proj in project_scores:
                        score = proj.get("score", 0)
                        score_color = "#27ae60" if score >= 40 else "#f39c12" if score >= 30 else "#e74c3c"

                        html_parts.append(f'<div class="info-section" style="border-left-color: {score_color};">')
                        html_parts.append(f'<h4>📌 {proj.get("name", "未知项目")} - {score}/50分</h4>')

                        # 基本信息
                        html_parts.append('<table>')
                        html_parts.append(f'<tr><td><strong>角色:</strong></td><td>{proj.get("role", "未知")}</td></tr>')
                        html_parts.append(f'<tr><td><strong>时间:</strong></td><td>{proj.get("start_time", "")} ~ {proj.get("end_time", "进行中")}</td></tr>')

                        # 技术栈
                        tech_stack = proj.get("tech_stack", [])
                        if tech_stack:
                            html_parts.append(f'<tr><td><strong>技术栈:</strong></td><td><div class="tech-stack">')
                            for tech in tech_stack[:8]:
                                html_parts.append(f'<span>{tech}</span>')
                            if len(tech_stack) > 8:
                                html_parts.append(f'<span>... (+{len(tech_stack) - 8}项)</span>')
                            html_parts.append('</div></td></tr>')

                        # 项目描述
                        description = proj.get("description", "")
                        if description:
                            # 限制描述长度，避免HTML过长
                            short_desc = description[:300] + "..." if len(description) > 300 else description
                            html_parts.append(f'<tr><td><strong>描述:</strong></td><td>{short_desc}</td></tr>')

                        html_parts.append('</table>')

                        # 评分明细
                        score_breakdown = proj.get("score_breakdown", {})
                        if score_breakdown:
                            html_parts.append('<div class="stats-grid">')
                            html_parts.append(f'<div class="stat-box"><div class="stat-value">{score_breakdown.get("基础分", 0)}/10</div><div class="stat-label">基础分</div></div>')
                            html_parts.append(f'<div class="stat-box"><div class="stat-value">{score_breakdown.get("技术栈分", 0)}/15</div><div class="stat-label">技术栈分</div></div>')
                            html_parts.append(f'<div class="stat-box"><div class="stat-value">{score_breakdown.get("描述质量分", 0)}/15</div><div class="stat-label">描述质量分</div></div>')
                            html_parts.append(f'<div class="stat-box"><div class="stat-value">{score_breakdown.get("规模分", 0)}/10</div><div class="stat-label">规模分</div></div>')
                            html_parts.append('</div>')

                        # 面试问题
                        interview_questions = proj.get("interview_questions", [])
                        if interview_questions:
                            html_parts.append('<h5>💡 面试准备建议</h5>')
                            for i, qa in enumerate(interview_questions, 1):
                                difficulty = "初级" if i == 1 else "中级" if i == 2 else "高级"
                                html_parts.append(f'<div class="info-section">')
                                html_parts.append(f'<p><strong>Q{i}: {qa["question"]}</strong></p>')
                                html_parts.append(f'<p><strong>难度:</strong> {difficulty}</p>')
                                html_parts.append(f'<p><strong>参考答案:</strong> {qa["answer"]}</p>')
                                html_parts.append('</div>')

                        html_parts.append('</div>')

                # 关键发现
                key_findings = proj_data.get("key_findings", [])
                if key_findings:
                    html_parts.append('<h4>关键发现</h4>')
                    html_parts.append('<ul class="findings-list">')
                    for finding in key_findings:
                        html_parts.append(f'<li>{finding}</li>')
                    html_parts.append('</ul>')

                # 亮点
                strengths = proj_data.get("strengths", [])
                if strengths:
                    html_parts.append('<h4>亮点</h4>')
                    html_parts.append('<ul class="strengths-list">')
                    for strength in strengths:
                        html_parts.append(f'<li>{strength}</li>')
                    html_parts.append('</ul>')

                # 不足
                weaknesses = proj_data.get("weaknesses", [])
                if weaknesses:
                    html_parts.append('<h4>待改进</h4>')
                    html_parts.append('<ul class="weaknesses-list">')
                    for weakness in weaknesses:
                        html_parts.append(f'<li>{weakness}</li>')
                    html_parts.append('</ul>')

            # 软技能详细分析
            if "soft_skill" in detailed:
                soft_data = detailed["soft_skill"]
                html_parts.append("<h3>💡 软技能</h3>")
                html_parts.append(f'<div class="score-card">')
                html_parts.append(f'<div class="dimension-name">软技能总分</div>')
                html_parts.append(f'<div class="score-value">{soft_data.get("score", 0)} 分</div>')
                html_parts.append(f'<div>等级: {soft_data.get("level", "未知")}</div>')
                html_parts.append('</div>')

                # 关键发现
                key_findings = soft_data.get("key_findings", [])
                if key_findings:
                    html_parts.append('<h4>关键发现</h4>')
                    html_parts.append('<ul class="findings-list">')
                    for finding in key_findings:
                        html_parts.append(f'<li>{finding}</li>')
                    html_parts.append('</ul>')

                # 亮点
                strengths = soft_data.get("strengths", [])
                if strengths:
                    html_parts.append('<h4>亮点</h4>')
                    html_parts.append('<ul class="strengths-list">')
                    for strength in strengths:
                        html_parts.append(f'<li>{strength}</li>')
                    html_parts.append('</ul>')

                # 不足
                weaknesses = soft_data.get("weaknesses", [])
                if weaknesses:
                    html_parts.append('<h4>待改进</h4>')
                    html_parts.append('<ul class="weaknesses-list">')
                    for weakness in weaknesses:
                        html_parts.append(f'<li>{weakness}</li>')
                    html_parts.append('</ul>')

        # 关键发现（整体）
        findings = report.get("key_findings", [])
        if findings:
            html_parts.append("<h2>🔍 关键发现</h2>")
            html_parts.append('<ul class="findings-list">')
            for finding in findings:
                html_parts.append(f'<li>{finding}</li>')
            html_parts.append('</ul>')

        # 优化建议
        suggestions = report.get("optimization_suggestions", [])
        if suggestions:
            html_parts.append("<h2>💡 优化建议</h2>")
            for i, suggestion in enumerate(suggestions, 1):
                priority = suggestion.get("priority", "中")
                priority_class = f"priority-{priority.lower()}"
                category = suggestion.get("category", "建议")

                html_parts.append(f'<div class="recommendation-card {priority_class}">')
                html_parts.append(f'<h4>{i}. {category} [{priority}优先级]</h4>')

                # 问题分析
                problem_analysis = suggestion.get("problem_analysis", "")
                if problem_analysis:
                    html_parts.append(f'<p><strong>📌 问题分析：</strong>{problem_analysis}</p>')

                # 改进步骤
                action_steps = suggestion.get("action_steps", [])
                if action_steps and isinstance(action_steps, list):
                    html_parts.append('<p><strong>📋 改进步骤：</strong></p>')
                    html_parts.append('<ol class="action-steps">')
                    for step in action_steps:
                        html_parts.append(f'<li>{step}</li>')
                    html_parts.append('</ol>')

                # 改进示例（before_after）
                before_after = suggestion.get("before_after", "")
                if before_after:
                    # 将换行符转换为HTML换行
                    formatted_example = before_after.replace('\\n', '<br>').replace('\n', '<br>')
                    html_parts.append(f'<p><strong>💡 改进示例：</strong></p>')
                    html_parts.append(f'<div class="example-box">{formatted_example}</div>')

                # 预期效果
                expected_benefit = suggestion.get("expected_benefit", "")
                if expected_benefit:
                    html_parts.append(f'<p><strong>✨ 预期效果：</strong>{expected_benefit}</p>')

                html_parts.append('</div>')

        # 岗位匹配分析
        job_match = report.get("job_match_analysis")
        if job_match:
            html_parts.append("<h2>🎯 岗位匹配分析</h2>")

            html_parts.append('<div class="match-score">')
            html_parts.append(f'<div class="score">{job_match.get("match_score", 0)} 分</div>')
            html_parts.append(f'<div class="level">{job_match.get("match_level", "未知")}</div>')
            html_parts.append('</div>')

            # 技能分析
            skill_analysis = job_match.get("skill_analysis", {})
            if skill_analysis:
                html_parts.append("<h3>技能匹配分析</h3>")
                html_parts.append(f'<p>技能覆盖率: <strong>{skill_analysis.get("skill_coverage", 0)}%</strong></p>')

                matched_skills = skill_analysis.get("matched_skills", [])
                if matched_skills:
                    html_parts.append('<p><strong>匹配的技能:</strong></p>')
                    html_parts.append('<div class="skills-container">')
                    for skill in matched_skills:
                        html_parts.append(f'<span class="skill-tag level-熟练">{skill}</span>')
                    html_parts.append('</div>')

                missing_skills = skill_analysis.get("missing_skills", [])
                if missing_skills:
                    html_parts.append('<p><strong>缺失的技能:</strong></p>')
                    html_parts.append('<div class="skills-container">')
                    for skill in missing_skills:
                        html_parts.append(f'<span class="skill-tag level-了解">{skill}</span>')
                    html_parts.append('</div>')

            # 优势和不足
            strengths = job_match.get("strengths", [])
            if strengths:
                html_parts.append("<h3>优势</h3>")
                html_parts.append('<ul class="strengths-list">')
                for strength in strengths:
                    html_parts.append(f'<li>{strength}</li>')
                html_parts.append('</ul>')

            weaknesses = job_match.get("weaknesses", [])
            if weaknesses:
                html_parts.append("<h3>不足</h3>")
                html_parts.append('<ul class="weaknesses-list">')
                for weakness in weaknesses:
                    html_parts.append(f'<li>{weakness}</li>')
                html_parts.append('</ul>')

            # 改进建议
            recommendations = job_match.get("recommendations", [])
            if recommendations:
                html_parts.append("<h3>改进建议</h3>")
                html_parts.append('<ul class="findings-list">')
                for rec in recommendations:
                    html_parts.append(f'<li>{rec}</li>')
                html_parts.append('</ul>')

            # 总结
            summary = job_match.get("summary", "")
            if summary:
                html_parts.append(f'<p><strong>总结:</strong> {summary}</p>')

        # 元数据
        metadata = report.get("metadata", {})
        if metadata:
            html_parts.append('<div class="metadata">')
            html_parts.append(f'<p><strong>报告生成时间:</strong> {metadata.get("generated_at", "未知")}</p>')
            if metadata.get("job_requirements"):
                html_parts.append(f'<p><strong>岗位要求:</strong> {metadata["job_requirements"]}</p>')
            html_parts.append('</div>')

        # HTML尾部
        html_parts.append("""
    </div>
</body>
</html>""")

        return "\n".join(html_parts)
