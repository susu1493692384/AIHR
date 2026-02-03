# tools/matching/llm_job_matcher.py
"""基于 LLM 的智能岗位匹配工具"""
import json
from typing import Dict, Any, Optional
from langchain_core.language_models import BaseChatModel


class LLMJobMatcher:
    """基于 LLM 的岗位匹配工具"""

    def __init__(self, llm: BaseChatModel):
        """
        初始化 LLM 岗位匹配器

        Args:
            llm: 语言模型实例
        """
        self.llm = llm

    def match_resume_to_job(
        self,
        resume_data: Dict[str, Any],
        job_requirements: str,
        analysis_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        使用 LLM 匹配简历与岗位

        Args:
            resume_data: 简历数据
            job_requirements: 岗位要求描述
            analysis_results: 简历分析结果（可选，用于提供更多上下文）

        Returns:
            岗位匹配分析结果
        """
        # 构建系统提示词
        system_prompt = self._get_system_prompt()

        # 构建用户提示词
        user_prompt = self._build_user_prompt(resume_data, job_requirements, analysis_results)

        try:
            # 调用 LLM
            response = self.llm.invoke([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ])

            # 解析响应
            result = self._parse_llm_response(response.content)

            return result

        except Exception as e:
            # LLM 调用失败，返回默认结果
            return {
                "success": False,
                "error": str(e),
                "match_score": 0,
                "match_level": "未知",
                "analysis": "LLM 分析失败",
                "strengths": [],
                "weaknesses": [],
                "recommendations": []
            }

    def _get_system_prompt(self) -> str:
        """构建系统提示词"""
        return """你是一位专业的HR分析师和招聘专家，擅长分析简历与岗位的匹配度。

你的任务是：
1. 分析候选人的技能、经验、教育背景是否满足岗位要求
2. 给出 0-100 分的匹配度评分
3. 识别候选人的优势和不足
4. 提供具体的改进建议

评分标准：
- 90-100分：完美匹配，候选人完全符合岗位要求
- 75-89分：高度匹配，候选人基本符合要求，有少量不足
- 60-74分：中度匹配，候选人部分符合要求，有一些差距
- 40-59分：低度匹配，候选人与要求有较大差距
- 0-39分：不匹配，候选人不适合该岗位

输出格式：
请严格按照以下 JSON 格式输出：
```json
{
  "match_score": 分数（0-100的整数）,
  "match_level": "完美匹配"|"高度匹配"|"中度匹配"|"低度匹配"|"不匹配",
  "summary": "简要总结（1-2句话）",
  "strengths": ["优势1", "优势2", "优势3"],
  "weaknesses": ["不足1", "不足2", "不足3"],
  "recommendations": ["建议1", "建议2", "建议3"],
  "skill_analysis": {
    "matched_skills": ["技能1", "技能2"],
    "missing_skills": ["技能1", "技能2"],
    "skill_coverage": 覆盖率（0-100的整数）
  },
  "experience_analysis": {
    "years_match": true/false,
    "relevant_experience": true/false,
    "analysis": "经验匹配分析"
  },
  "education_analysis": {
    "degree_match": true/false,
    "major_match": true/false,
    "analysis": "教育背景匹配分析"
  }
}
```

注意：
1. 保持客观中立，基于事实进行分析
2. 评分要公正合理，不要过高或过低
3. 优势和建议要具体明确，有针对性
4. 必须严格按照 JSON 格式输出，不要包含其他内容"""

    def _build_user_prompt(
        self,
        resume_data: Dict[str, Any],
        job_requirements: str,
        analysis_results: Optional[Dict[str, Any]] = None
    ) -> str:
        """构建用户提示词"""

        # 构建简历摘要
        resume_summary = self._build_resume_summary(resume_data, analysis_results)

        # 构建提示词
        prompt = f"""请分析以下候选人与岗位的匹配度：

【岗位要求】
{job_requirements}

【候选人信息】
{resume_summary}

请根据以上信息，按照指定的 JSON 格式输出匹配分析结果。"""

        return prompt

    def _build_resume_summary(
        self,
        resume_data: Dict[str, Any],
        analysis_results: Optional[Dict[str, Any]] = None
    ) -> str:
        """构建简历摘要"""

        parts = []

        # 基本信息
        personal_info = resume_data.get("personal_info", {})
        if personal_info.get("name"):
            parts.append(f"姓名：{personal_info['name']}")

        # 教育背景
        education = resume_data.get("education", [])
        if education:
            parts.append("\n【教育背景】")
            for edu in education[:3]:  # 最多显示3个
                parts.append(f"- {edu.get('school', '')} | {edu.get('degree', '')} | {edu.get('major', '')} | {edu.get('start_time', '')} - {edu.get('end_time', '至今')}")

        # 工作经历
        work_experience = resume_data.get("work_experience", [])
        if work_experience:
            parts.append("\n【工作经历】")
            for exp in work_experience[:3]:  # 最多显示3个
                parts.append(f"- {exp.get('company', '')} | {exp.get('position', '')} | {exp.get('start_time', '')} - {exp.get('end_time', '至今')}")
                if exp.get("description"):
                    parts.append(f"  职责：{exp['description'][:100]}...")  # 限制长度

        # 项目经验
        projects = resume_data.get("projects", [])
        if projects:
            parts.append("\n【项目经验】")
            for proj in projects[:3]:  # 最多显示3个
                parts.append(f"- {proj.get('name', '')} | {proj.get('role', '')} | {proj.get('start_time', '')} - {proj.get('end_time', '至今')}")
                if proj.get("description"):
                    parts.append(f"  描述：{proj['description'][:100]}...")  # 限制长度
                if proj.get("tech_stack"):
                    parts.append(f"  技术栈：{proj['tech_stack']}")

        # 技能
        skills = resume_data.get("skills", [])
        if skills:
            parts.append("\n【技能】")
            skill_list = []
            for skill in skills:
                level = skill.get("level", "")
                skill_list.append(f"{skill.get('name', '')}({level})" if level else skill.get("name", ""))
            parts.append(", ".join(skill_list))

        # 分析结果（如果提供）
        if analysis_results:
            parts.append("\n【能力评估】")
            technical = analysis_results.get("technical_analysis", {})
            experience = analysis_results.get("experience_analysis", {})
            project = analysis_results.get("project_analysis", {})

            if technical.get("score") is not None:
                parts.append(f"- 技术能力：{technical['score']:.1f}分")
                if technical.get("highlights"):
                    parts.append(f"  亮点：{', '.join(technical['highlights'][:2])}")

            if experience.get("score") is not None:
                parts.append(f"- 经验背景：{experience['score']:.1f}分")

            if project.get("score") is not None:
                parts.append(f"- 项目经验：{project['score']:.1f}分")
                if project.get("highlights"):
                    parts.append(f"  亮点：{', '.join(project['highlights'][:2])}")

        return "\n".join(parts)

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """解析 LLM 响应"""

        try:
            # 尝试直接解析 JSON
            result = json.loads(response)

            # 验证必要字段
            if "match_score" not in result:
                result["match_score"] = 50  # 默认分数

            if "match_level" not in result:
                result["match_level"] = self._get_match_level_from_score(result["match_score"])

            if "strengths" not in result:
                result["strengths"] = []

            if "weaknesses" not in result:
                result["weaknesses"] = []

            if "recommendations" not in result:
                result["recommendations"] = []

            # 添加成功标记
            result["success"] = True

            return result

        except json.JSONDecodeError:
            # JSON 解析失败，尝试提取 JSON
            result = self._extract_json_from_text(response)

            if result:
                result["success"] = True
                return result
            else:
                # 完全解析失败，返回默认结果
                return {
                    "success": False,
                    "error": "无法解析 LLM 响应",
                    "match_score": 50,
                    "match_level": "中度匹配",
                    "summary": "分析结果解析失败",
                    "strengths": [],
                    "weaknesses": [],
                    "recommendations": [],
                    "raw_response": response
                }

    def _extract_json_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """从文本中提取 JSON"""
        import re

        # 尝试匹配 JSON 代码块
        json_pattern = r'```json\s*(.*?)\s*```'
        match = re.search(json_pattern, text, re.DOTALL)

        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # 尝试匹配花括号内的 JSON
        brace_pattern = r'\{.*\}'
        match = re.search(brace_pattern, text, re.DOTALL)

        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        return None

    def _get_match_level_from_score(self, score: float) -> str:
        """根据分数确定匹配等级"""
        if score >= 90:
            return "完美匹配"
        elif score >= 75:
            return "高度匹配"
        elif score >= 60:
            return "中度匹配"
        elif score >= 40:
            return "低度匹配"
        else:
            return "不匹配"
