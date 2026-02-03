# tools/analysis/project_analyzer_simple.py
"""极简项目评分分析器

采用极简评分规则：
- 基础分（10分）：有项目名称、角色、时间
- 技术栈分（0-15分）：根据技术栈数量
- 描述质量分（0-15分）：根据描述长度和是否有成果
- 规模分（0-10分）：根据团队规模和项目时长

每个项目最高50分，总分取平均并归一化到0-100
"""
from typing import Dict, List
from datetime import datetime
from core.models import CleanedResume, Project, AnalysisResult
from tools.analysis.base_analyzer import BaseAnalyzer


class SimpleProjectAnalyzer(BaseAnalyzer):
    """极简项目评分分析器"""

    dimension_name = "项目经验"
    weight = 0.40

    def __init__(self, llm=None):
        """
        初始化分析器

        Args:
            llm: 语言模型实例（可选，用于生成面试问题）
        """
        self.dimension_name = self.dimension_name
        self.weight = self.weight
        self.llm = llm

    def get_dimension_name(self) -> str:
        return self.dimension_name

    def get_weight(self) -> float:
        return self.weight

    def analyze(self, resume: CleanedResume) -> AnalysisResult:
        """分析项目经验"""
        projects = resume.cleaned_data.projects

        if not projects:
            return AnalysisResult(
                dimension=self.dimension_name,
                score=0.0,
                detail_scores={"项目数量": 0, "平均质量": 0},
                insights=["未发现项目经验"],
                highlights=[],
                weaknesses=["缺少项目经验"],
                raw_analysis={"project_count": 0, "project_scores": []}
            )

        # 计算每个项目的得分
        project_scores = []
        for proj in projects:
            score = self._calculate_single_project_score(proj)

            # 计算各项得分明细（传入description用于tech_stack备用提取）
            basic_score = 10 if (proj.name and proj.role and proj.start_time) else (5 if (proj.name or proj.role) else 0)
            tech_stack_score = self._calculate_tech_stack_score(proj.tech_stack, proj.description or "")
            desc_score = self._calculate_description_quality(proj)
            scale_score = self._calculate_project_scale(proj)

            # 生成面试问题（如果有LLM）
            interview_questions = []
            if self.llm:
                try:
                    from utils.llm_helpers import generate_interview_questions
                    interview_questions = generate_interview_questions(
                        project_name=proj.name,
                        project_role=proj.role,
                        tech_stack=proj.tech_stack or [],
                        project_description=proj.description or ""
                    )
                except Exception as e:
                    # 面试问题生成失败不影响主流程
                    print(f"[警告] 生成面试问题失败: {e}")

            project_scores.append({
                "name": proj.name,
                "score": score,
                "role": proj.role,
                "start_time": proj.start_time,
                "end_time": proj.end_time,
                "tech_stack": proj.tech_stack or [],
                "description": proj.description or "",  # 保持完整的项目描述
                "achievements": proj.achievements or [],  # 保持原始的成果字段
                "team_size": proj.team_size,
                "interview_questions": interview_questions,  # 面试问题
                # 评分明细
                "score_breakdown": {
                    "基础分": basic_score,
                    "技术栈分": tech_stack_score,
                    "描述质量分": desc_score,
                    "规模分": scale_score
                }
            })

        # 总分计算（取平均分并归一化到0-100）
        avg_score = sum(ps["score"] for ps in project_scores) / len(project_scores)
        total_score = min(avg_score * 2, 100)  # 每个项目最高50分，乘以2归一化

        return AnalysisResult(
            dimension=self.dimension_name,
            score=round(total_score, 2),
            detail_scores={
                "项目数量": len(projects),
                "平均质量": round(avg_score, 2)
            },
            insights=self._extract_insights(projects, project_scores),
            highlights=self._extract_highlights(project_scores),
            weaknesses=self._extract_weaknesses(project_scores),
            raw_analysis={
                "project_count": len(projects),
                "project_scores": project_scores
            }
        )

    def _calculate_single_project_score(self, proj: Project) -> int:
        """
        计算单个项目得分（最高50分）

        评分规则：
        - 基础分（10分）：有项目名称、角色、时间
        - 技术栈分（0-15分）：1-3项→5分，4-6项→10分，7+项→15分
        - 描述质量分（0-15分）：描述长度+是否有成果
        - 规模分（0-10分）：团队规模+项目时长
        """
        score = 0

        # 1. 基础分（10分）
        if proj.name and proj.role and proj.start_time:
            score += 10
        elif proj.name or proj.role:
            score += 5

        # 2. 技术栈分（0-15分）
        score += self._calculate_tech_stack_score(proj.tech_stack)

        # 3. 描述质量分（0-15分）
        score += self._calculate_description_quality(proj)

        # 4. 规模分（0-10分）
        score += self._calculate_project_scale(proj)

        return min(score, 50)

    def _calculate_tech_stack_score(self, tech_stack: List[str], description: str = "") -> int:
        """
        技术栈评分（0-15分）

        - 0项技术：0分
        - 1-3项技术：5分
        - 4-6项技术：10分
        - 7+项技术：15分

        如果tech_stack为空，尝试从描述中提取技术关键词
        """
        import re

        count = len(tech_stack or [])

        # 如果tech_stack为空，尝试从描述中提取技术
        if count == 0 and description:
            # 常见技术关键词列表（扩充版）
            tech_keywords = [
                # 编程语言
                'Python', 'Java', 'JavaScript', 'TypeScript', 'Go', 'Rust', 'C++', 'C#', 'C', 'PHP', 'Ruby', 'Swift', 'Kotlin', 'Scala', 'R', 'Matlab', 'Shell', 'Bash',

                # Web框架
                'Django', 'Flask', 'FastAPI', 'Spring', 'SpringBoot', 'SpringCloud', 'React', 'Vue', 'Angular', 'Nextjs', 'Nuxtjs', 'Express', 'Koa', 'Laravel', 'Rails', 'Gin', 'Echo',

                # 数据库
                'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Oracle', 'SQLServer', 'SQLite', 'Elasticsearch', 'Cassandra', 'Neo4j', 'Hive', 'HBase', 'InfluxDB',

                # 大数据/数据科学
                'Hadoop', 'Spark', 'Flink', 'Kafka', 'Hive', 'HBase', 'Presto', 'Druid', 'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn', 'Pandas', 'Numpy', 'Matplotlib',

                # 容器/云原生/运维
                'Docker', 'Kubernetes', 'K8s', 'Helm', 'Jenkins', 'Gitlab', 'CircleCI', 'TravisCI', 'Ansible', 'Terraform', 'Prometheus', 'Grafana', 'ELK',

                # 中间件/工具
                'Nginx', 'Apache', 'Gunicorn', 'uWSGI', 'Tomcat', 'Jetty', 'Netty', 'RabbitMQ', 'Kafka', 'RocketMQ', 'ActiveMQ', 'Zeromq', 'Zookeeper',

                # 版本控制/协作
                'Git', 'Svn', 'Github', 'Gitlab', 'Bitbucket',

                # 云平台
                'AWS', 'Azure', 'GCP', 'Aliyun', 'Qingcloud', 'Huaweicloud',

                # 前端技术
                'HTML', 'CSS', 'Less', 'Sass', 'Webpack', 'Vite', 'Babel', 'Redux', 'Mobx', 'Vuex', 'Pinia',

                # 移动端
                'Flutter', 'ReactNative', 'Android', 'IOS', 'SwiftUI', 'Jetpack',

                # 测试
                'JUnit', 'PyTest', 'Selenium', 'Jest', 'Mocha', 'Cypress',

                # 其他常见技术
                'RESTful', 'REST', 'GraphQL', 'gRPC', 'WebSocket', 'OAuth', 'OAuth2', 'JWT', 'SSO', 'RBAC', 'ACL',
                'SQL', 'NoSQL', 'ACID', 'CAP', 'BASE', 'MVVM', 'MVC', 'MVP', 'DDD', 'TDD', 'BDD',
                'Microservice', 'Microservices', 'Serverless', 'SPA', 'PWA', 'SSR', 'CSR',
                'CI/CD', 'DevOps', 'Agile', 'Scrum', 'Kanban',
                'Linux', 'Unix', 'Windows', 'MacOS', 'Ubuntu', 'CentOS', 'Debian',
                'Algorithm', 'DataStructure', 'DesignPattern', 'SOLID', 'DRY', 'KISS'
            ]

            # 从描述中查找技术关键词（大小写不敏感）
            found_techs = []
            desc_upper = description.upper()
            for tech in tech_keywords:
                if tech.upper() in desc_upper:
                    found_techs.append(tech)

            count = len(found_techs)

        if count == 0:
            return 0
        elif count <= 3:
            return 5
        elif count <= 6:
            return 10
        else:
            return 15

    def _calculate_description_quality(self, proj: Project) -> int:
        """
        描述质量评分（0-15分）

        评分依据：
        1. 描述长度评分（0-9分）：
           - 0字：0分
           - < 30字：3分
           - 30-60字：6分
           - 60-100字：9分
           - 100+字：12分
           - 150+字：15分
        2. 成果加分（额外+3分）：如果有 achievements 字段且不为空
        """
        score = 0

        # 1. 描述长度评分
        desc_len = len(proj.description or "")
        if desc_len >= 150:
            score = 15
        elif desc_len >= 100:
            score = 12
        elif desc_len >= 60:
            score = 9
        elif desc_len >= 30:
            score = 6
        elif desc_len > 0:
            score = 3
        else:
            score = 0

        # 2. 成果额外加分（如果有 achievements 字段且不为空）
        # 注意：描述长度最高12分，加上成果3分=15分
        if proj.achievements and len(proj.achievements) > 0 and score < 12:
            score = min(score + 3, 15)

        return score

    def _calculate_project_scale(self, proj: Project) -> int:
        """
        项目规模评分（0-10分）

        评分依据（适配实际数据结构）：
        1. 团队规模（0-7分）：如果有 team_size 字段则使用，否则默认3分
        2. 项目时长（0-3分）：超过3个月额外+3分

        团队规模评分：
        - 1人：0分
        - 2-5人：3分
        - 6-10人：5分
        - 10+人：7分
        - 未知：3分（默认中等规模）
        """
        score = 0

        # 团队规模评分
        if proj.team_size:
            if proj.team_size >= 10:
                score = 7
            elif proj.team_size >= 6:
                score = 5
            elif proj.team_size >= 2:
                score = 3
            # 1人项目保持0分
        else:
            # 没有团队规模信息，默认给中等分数（3分）
            score = 3

        # 项目时长加分
        if proj.start_time and proj.end_time:
            duration_months = self._calculate_duration_months(
                proj.start_time,
                proj.end_time
            )
            if duration_months >= 3:
                score = min(score + 3, 10)
        elif proj.start_time:
            # 只有开始时间，假设至少3个月
            score = min(score + 3, 10)

        return score

    def _calculate_duration_months(self, start_time: str, end_time: str) -> int:
        """计算项目时长（月）"""
        try:
            start = datetime.strptime(start_time, "%Y-%m")
            end = datetime.strptime(end_time, "%Y-%m")
            return (end.year - start.year) * 12 + (end.month - start.month)
        except Exception:
            return 0

    def _extract_insights(self, projects: List[Project], project_scores: List[Dict]) -> List[str]:
        """提取分析洞察"""
        insights = []

        if not projects:
            return insights

        # 项目数量洞察
        count = len(projects)
        if count >= 5:
            insights.append(f"候选人拥有丰富的项目经验，共参与{count}个项目")
        elif count >= 3:
            insights.append(f"候选人参与过{count}个项目，经验较为丰富")
        else:
            insights.append(f"候选人参与过{count}个项目")

        # 项目质量洞察
        avg_score = sum(ps["score"] for ps in project_scores) / len(project_scores)
        if avg_score >= 40:
            insights.append("项目整体质量很高，技术栈丰富，团队规模较大")
        elif avg_score >= 30:
            insights.append("项目整体质量良好，有一定的技术深度")
        elif avg_score >= 20:
            insights.append("项目经验相对基础，仍有提升空间")
        else:
            insights.append("项目描述较为简单，缺乏详细说明")

        # 角色洞察
        roles = [p.role for p in projects]
        lead_count = sum(1 for r in roles if r in ["负责人", "主导"])
        if lead_count > 0:
            insights.append(f"在{lead_count}个项目中担任负责人或主导角色，具备领导能力")

        # 技术栈洞察
        all_techs = []
        for p in projects:
            all_techs.extend(p.tech_stack or [])
        unique_techs = len(set(all_techs))
        if unique_techs >= 10:
            insights.append(f"技术栈非常丰富，掌握{unique_techs}项技术")
        elif unique_techs >= 5:
            insights.append(f"技术栈较为丰富，掌握{unique_techs}项技术")

        return insights

    def _extract_highlights(self, project_scores: List[Dict]) -> List[str]:
        """提取亮点"""
        highlights = []

        # 找出得分最高的项目
        if project_scores:
            best_projects = sorted(project_scores, key=lambda x: x["score"], reverse=True)[:3]
            for proj in best_projects:
                if proj["score"] >= 40:
                    highlights.append(f"《{proj['name']}》：{proj['role']}，评分{proj['score']}/50")
                elif proj["score"] >= 30:
                    highlights.append(f"《{proj['name']}》：评分{proj['score']}/50")

        return highlights

    def _extract_weaknesses(self, project_scores: List[Dict]) -> List[str]:
        """提取不足"""
        weaknesses = []

        if not project_scores:
            return ["缺少项目经验"]

        avg_score = sum(ps["score"] for ps in project_scores) / len(project_scores)

        # 整体质量不足
        if avg_score < 25:
            weaknesses.append("项目整体质量较低，建议补充项目描述和技术栈")
        elif avg_score < 35:
            weaknesses.append("项目描述较为简单，建议增加技术细节和成果说明")

        # 找出得分较低的项目
        weak_projects = [p for p in project_scores if p["score"] < 25]
        if weak_projects:
            weaknesses.append(f"{len(weak_projects)}个项目得分较低，建议补充详细信息")

        return weaknesses
