# prompts/matching_prompts.py
"""岗位匹配相关Prompt模板"""
from typing import List
from prompts.base import BasePrompt


class JobMatchingPrompt(BasePrompt):
    """岗位匹配分析Prompt"""

    def get_system_prompt(self) -> str:
        """获取系统Prompt"""
        return """你是专业的HR招聘助手，擅长分析简历与岗位要求的匹配度。

你的任务是对比候选人的简历与具体的岗位要求，提供专业的匹配分析。

分析时需要考虑：
1. 技能匹配度 - 候选人的技能是否满足岗位需求
2. 经验匹配度 - 工作年限、项目经验是否符合要求
3. 学历匹配度 - 学历层次是否达标
4. 综合潜力 - 候选人的成长潜力
5. 差距分析 - 缺失的关键技能和经验
6. 改进建议 - 如何提高匹配度

请保持客观、专业的语气，给出有建设性的意见。"""

    def get_user_prompt(self) -> str:
        """获取用户Prompt"""
        return """请分析以下简历与岗位要求的匹配度：

## 岗位要求
{job_requirements}

## 候选人简历信息

### 基本信息
{basic_info}

### 技能清单
{skills_info}

### 工作经历
{work_experience_info}

### 项目经验
{projects_info}

### 教育背景
{education_info}

## 简历分析结果
- 综合评分：{total_score}分
- 技术能力：{technical_score}分
- 经验背景：{experience_score}分
- 项目经验：{project_score}分

请提供以下JSON格式的匹配分析：

```json
{{
    "match_score": <匹配分数0-100>,
    "match_level": "<高度匹配|较好匹配|基本匹配|部分匹配|不匹配>",
    "skill_analysis": {{
        "matched_skills": ["<匹配的技能列表>"],
        "missing_skills": ["<缺失的关键技能列表>"],
        "additional_skills": ["<候选人的额外技能>"],
        "skill_coverage": <技能覆盖率0-100>
    }},
    "experience_analysis": {{
        "years_match": <年限匹配情况true/false>,
        "project_relevance": <项目相关性0-100>,
        "gap_analysis": "<经验差距描述>"
    }},
    "education_analysis": {{
        "degree_match": <学历匹配情况true/false>,
        "major_relevance": <专业相关性0-100>
    }},
    "strengths": ["<候选人的优势1>", "<优势2>", ...],
    "weaknesses": ["<候选人的不足1>", "<不足2>", ...],
    "recommendations": ["<改进建议1>", "<建议2>", ...],
    "summary": "<整体评估总结（1-2句话）>"
}}
```

注意：
1. 匹配分数综合考虑技能、经验、学历等因素
2. 如果岗位要求中没有明确某方面要求，该方面不计入扣分
3. 给出具体、可操作的改进建议
4. 保持客观中立，既不过分夸奖也不刻意贬低"""

    def format(self, **kwargs) -> str:
        """格式化Prompt"""
        job_requirements = kwargs.get("job_requirements", "")
        resume_data = kwargs.get("resume_data", {})
        analysis_results = kwargs.get("analysis_results", {})

        # 提取基本信息
        personal_info = resume_data.get("personal_info", {})
        basic_info = f"""
- 姓名：{personal_info.get("name", "未知")}
- 手机：{personal_info.get("phone", "未知")}
- 邮箱：{personal_info.get("email", "未知")}"""

        # 提取技能信息
        skills = resume_data.get("skills", [])
        if skills:
            skills_list = "\n".join([f"- {s.get('name', '')}: {s.get('level', '')}" for s in skills])
            skills_info = f"共{len(skills)}项技能：\n{skills_list}"
        else:
            skills_info = "无技能信息"

        # 提取工作经历
        work_exp = resume_data.get("work_experience", [])
        if work_exp:
            work_list = []
            for exp in work_exp[:3]:  # 最多显示3段
                company = exp.get("company", "")
                position = exp.get("position", "")
                start = exp.get("start_time", exp.get("start_date", ""))
                end = exp.get("end_time", exp.get("end_date", ""))
                work_list.append(f"- {company} | {position} | {start} ~ {end}")
            work_experience_info = "\n".join(work_list)
        else:
            work_experience_info = "无工作经历"

        # 提取项目经验
        projects = resume_data.get("projects", [])
        if projects:
            project_list = []
            for proj in projects[:3]:  # 最多显示3个
                name = proj.get("name", "")
                role = proj.get("role", "")
                project_list.append(f"- {name} | {role}")
            projects_info = "\n".join(project_list)
        else:
            projects_info = "无项目经验"

        # 提取教育背景
        education = resume_data.get("education", [])
        if education:
            edu_list = []
            for edu in education:
                school = edu.get("school", "")
                degree = edu.get("degree", "")
                major = edu.get("major", "")
                edu_list.append(f"- {school} | {degree} | {major}")
            education_info = "\n".join(edu_list)
        else:
            education_info = "无教育信息"

        # 提取分数
        score_breakdown = analysis_results.get("score_breakdown", {})
        total_score = analysis_results.get("total_score", 0)
        technical_score = score_breakdown.get("technical", {}).get("score", 0)
        experience_score = score_breakdown.get("experience", {}).get("score", 0)
        project_score = score_breakdown.get("project", {}).get("score", 0)

        return self.get_user_prompt().format(
            job_requirements=job_requirements,
            basic_info=basic_info.strip(),
            skills_info=skills_info.strip(),
            work_experience_info=work_experience_info.strip(),
            projects_info=projects_info.strip(),
            education_info=education_info.strip(),
            total_score=total_score,
            technical_score=technical_score,
            experience_score=experience_score,
            project_score=project_score
        )
