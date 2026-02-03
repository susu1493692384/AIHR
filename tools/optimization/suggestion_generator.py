# tools/optimization/suggestion_generator.py
"""优化建议生成工具 - 基于规则的智能建议生成"""
from typing import Dict, Any, List


class SuggestionGenerator:
    """优化建议生成工具类"""

    # 优化建议模板（匹配当前评分维度）
    SUGGESTION_TEMPLATES = {
        "technical": {
            "low_count": {
                "category": "技术能力",
                "problem_analysis": "您的技能数量较少，技术栈覆盖面不够广，这会限制您在项目中的适应能力和竞争力。",
                "action_steps": [
                    "选择与当前技能相关的技术方向，如前端、后端、数据库或运维",
                    "通过在线课程（慕课网、极客时间等）系统学习新技术基础",
                    "完成至少2个实战项目，将新技术应用到实际开发中",
                    "在简历中更新技能清单，明确标注掌握程度（了解/熟悉/熟练/精通）"
                ],
                "before_after": "改进前：技能：Python(了解)\\n改进后：技能：Python(熟练)-熟练使用Django/Flask框架；JavaScript(熟悉)-掌握Vue3前端开发；MySQL(了解)-了解基本SQL查询和索引优化",
                "expected_benefit": "技术能力得分提升10-15分，增加求职选择范围。",
                "priority": "中"
            },
            "low_proficiency": {
                "category": "技术能力",
                "problem_analysis": "您的技能熟练度普遍较低，缺乏深入理解和实战经验，难以胜任核心技术岗位。",
                "action_steps": [
                    "选择1-2项核心技能进行深度学习，避免贪多嚼不烂",
                    "阅读框架/库的源码，理解底层原理和设计思想",
                    "参与复杂项目开发，在实际场景中磨练技能",
                    "考取相关技术认证（如Oracle Java认证、AWS云架构师）"
                ],
                "before_after": "改进前：Python(了解)、Django(了解)\\n改进后：Python(熟练)-深入理解GIL、内存管理、异步编程；Django(熟练)-精通ORM、中间件、DRF，有3个完整项目经验",
                "expected_benefit": "技术能力得分提升15-20分，获得更多技术面试机会。",
                "priority": "高"
            },
            "low_verified": {
                "category": "技术能力",
                "problem_analysis": "您的技能缺乏项目实战验证，雇主无法判断您的真实技术水平，影响简历可信度。",
                "action_steps": [
                    "在GitHub上发布个人开源项目，展示代码能力和项目质量",
                    "撰写技术博客，记录学习心得和项目经验",
                    "在简历中为每个技能标注实际应用的项目名称",
                    "获得技术社区认可，如Stack Overflow高赞回答、开源项目贡献"
                ],
                "before_after": "改进前：技能：Python、MySQL（无项目说明）\\n改进后：技能：Python-用于电商平台后端开发（10万+订单）；MySQL-负责数据库设计和查询优化，性能提升50%",
                "expected_benefit": "技术能力得分提升10-15分，显著提升简历说服力。",
                "priority": "中"
            }
        },
        "experience": {
            "low_education": {
                "category": "经验背景",
                "problem_analysis": "您的学历层次相对较低，可能在简历初筛阶段处于劣势，影响面试机会。",
                "action_steps": [
                    "考虑攻读在职研究生或MBA，提升学历背景",
                    "考取权威技术认证（如PMP、AWS、Oracle认证）",
                    "通过实际项目成果和工作能力来弥补学历不足",
                    "突出在知名企业或重要项目的工作经验"
                ],
                "before_after": "改进前：学历：本科\\n改进后：学历：本科 + PMP项目管理认证 + AWS解决方案架构师认证；3年大厂核心项目经验",
                "expected_benefit": "经验背景得分提升8-12分，增加简历通过率。",
                "priority": "中"
            },
            "low_work_years": {
                "category": "经验背景",
                "problem_analysis": "您的工作年限相对较短，缺乏足够的行业经验和项目积累。",
                "action_steps": [
                    "积极寻找实习机会，提前进入职场积累经验",
                    "参与开源项目或接外包项目，丰富实战经验",
                    "在简历中突出项目成果和能力成长，而非仅关注工作年限",
                    "参加技术社区活动，建立行业人脉"
                ],
                "before_after": "改进前：工作经验：1年（仅列出了时间）\\n改进后：工作经验：1年，完成3个完整项目，独立负责核心模块开发，代码质量被团队评为优秀",
                "expected_benefit": "经验背景得分提升5-10分，展示快速成长能力。",
                "priority": "低"
            },
            "low_school": {
                "category": "经验背景",
                "problem_analysis": "您的学校背景相对普通，可能在简历筛选时处于劣势。",
                "action_steps": [
                    "通过实际能力证明自己，如竞赛获奖、论文发表、专利申请",
                    "在知名大厂实习或工作，借助平台光环提升简历含金量",
                    "考取高含金量的技术认证，证明专业能力",
                    "在GitHub上维护高star项目或参与知名开源项目"
                ],
                "before_after": "改进前：教育：XX学院（本科）\\n改进后：教育：XX学院（本科）+ ACM竞赛省银奖 + GitHub 1000+ star项目作者 + 字节跳动实习经验",
                "expected_benefit": "经验背景得分提升8-12分，显著提升竞争力。",
                "priority": "中"
            },
            "low_internship": {
                "category": "经验背景",
                "problem_analysis": "您的实习经验较少，缺乏实际工作环境和项目协作经验。",
                "action_steps": [
                    "积极投递大厂暑期实习项目，提前规划实习时间",
                    "参加校企合作的实训项目，积累项目经验",
                    "在简历中详细描述实习期间的具体工作和成果",
                    "争取实习转正机会或获得推荐信"
                ],
                "before_after": "改进前：实习：暂无\\n改进后：实习：XX公司（暑期实习生）-参与电商平台开发，独立完成用户模块，获得优秀实习生评价",
                "expected_benefit": "经验背景得分提升5-8分，增加全职就业机会。",
                "priority": "低"
            }
        },
        "project": {
            "low_quantity": {
                "category": "项目经验",
                "problem_analysis": "您的项目数量较少，无法充分展示您的技术广度和实战能力。",
                "action_steps": [
                    "根据兴趣和职业方向，规划3-5个有代表性的项目",
                    "选择不同技术栈的项目，展示技术多样性",
                    "确保每个项目都有完整的开发流程和可展示的成果",
                    "在GitHub上发布项目代码和演示地址"
                ],
                "before_after": "改进前：项目：1个（课程作业）\\n改进后：项目：个人博客系统（Vue+Django）、电商平台（Spring Cloud微服务）、数据可视化工具（Python+Pyecharts）等5个项目",
                "expected_benefit": "项目经验得分提升15-25分，全面展示技术能力。",
                "priority": "高"
            },
            "low_quality": {
                "category": "项目经验",
                "problem_analysis": "您的项目质量有待提升，缺乏技术深度和详细的成果展示。",
                "action_steps": [
                    "在每个项目中使用3-5种技术，展示技术栈广度",
                    "详细描述项目背景、技术选型、遇到的问题及解决方案",
                    "量化项目成果，如性能提升、用户增长、业务指标等",
                    "突出个人在项目中的角色和贡献，避免用'参与'等模糊词汇"
                ],
                "before_after": "改进前：项目：电商系统-负责后端开发\\n改进后：项目：B2C电商平台（技术负责人）- 采用微服务架构，支撑10万+日活；使用Redis缓存，查询性能提升60%；独立设计订单系统，处理大促峰值5000 QPS",
                "expected_benefit": "项目经验得分提升15-20分，展现技术深度和成果。",
                "priority": "高"
            }
        },
        "soft_skill": {
            "low_coverage": {
                "category": "软技能",
                "problem_analysis": "您的软技能描述较少，无法全面展示您的综合能力和团队价值。",
                "action_steps": [
                    "在简历中增加软技能相关经历，如团队协作、技术分享、培训新人等",
                    "使用STAR法则（情境-任务-行动-结果）描述软技能应用场景",
                    "在项目描述中加入沟通、协调、领导等方面的具体事例",
                    "补充外语能力、学习能力、抗压能力等软技能信息"
                ],
                "before_after": "改进前：（无软技能描述）\\n改进后：软技能：团队协作-作为技术负责人协调5人团队，完成跨部门合作项目；沟通能力-定期进行技术分享，培训3名新人快速上手",
                "expected_benefit": "软技能得分提升10-15分，展示综合素质。",
                "priority": "中"
            },
            "low_teamwork": {
                "category": "软技能",
                "problem_analysis": "您的团队协作经验展示不足，难以体现您的团队合作能力。",
                "action_steps": [
                    "在项目描述中明确团队规模和协作情况",
                    "突出参与代码评审、技术讨论、跨部门协作的经历",
                    "描述解决团队冲突或带领团队达成目标的经验",
                    "补充团队合作相关成果，如团队效率提升、知识分享等"
                ],
                "before_after": "改进前：项目：XX系统开发\\n改进后：项目：XX系统开发（5人团队）- 与前端团队协作设计API接口，参与代码评审提出20+条改进建议，组织技术分享会提升团队整体能力",
                "expected_benefit": "软技能得分提升8-12分，突出团队协作能力。",
                "priority": "低"
            },
            "low_leadership": {
                "category": "软技能",
                "problem_analysis": "您的领导力经验较少，缺乏带领团队或推动项目的能力展示。",
                "action_steps": [
                    "主动承担项目负责人或Tech Lead角色",
                    "描述带领团队完成项目的经历，包括团队管理、技术决策等",
                    "突出指导新人、技术培训、知识传承等领导行为",
                    "补充项目管理经验，如使用敏捷开发、任务分配、进度管理等"
                ],
                "before_after": "改进前：（无领导力相关描述）\\n改进后：项目负责人：带领6人团队完成企业SaaS平台开发，制定技术方案和开发计划，指导2名新人快速成长，项目按时交付并获得客户好评",
                "expected_benefit": "软技能得分提升5-10分，展现领导潜质。",
                "priority": "低"
            }
        }
    }

    @staticmethod
    def generate_suggestions(
        analysis_results: Dict[str, Any],
        resume_data: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        基于分析结果生成优化建议（每个维度最多1条）

        Args:
            analysis_results: 分析结果
            resume_data: 简历数据（暂未使用，保留兼容性）

        Returns:
            优化建议列表（每个维度最多1条）
        """
        suggestions = []

        # 获取各维度得分
        score_breakdown = analysis_results.get("score_breakdown", {})
        technical = score_breakdown.get("technical", {})
        experience = score_breakdown.get("experience", {})
        project = score_breakdown.get("project", {})
        soft_skill = score_breakdown.get("soft_skill", {})

        # 技术能力建议（最多1条 - 优先返回最高优先级的）
        tech_detail = technical.get("detail_scores", {})
        tech_score = technical.get("score", 0)

        if tech_score < 60:
            # 低分情况：优先检查熟练度
            if tech_detail.get("精通", 0) == 0 and tech_detail.get("熟练", 0) <= 1:
                suggestions.append(SuggestionGenerator.SUGGESTION_TEMPLATES["technical"]["low_proficiency"])
            # 技能数量少
            elif tech_detail.get("技能总数", 0) < 5:
                suggestions.append(SuggestionGenerator.SUGGESTION_TEMPLATES["technical"]["low_count"])
            # 验证技能少
            elif tech_detail.get("验证比例", "0%") == "0%":
                suggestions.append(SuggestionGenerator.SUGGESTION_TEMPLATES["technical"]["low_verified"])

        # 经验背景建议（最多1条）
        exp_detail = experience.get("detail_scores", {})
        exp_score = experience.get("score", 0)

        if exp_score < 60:
            # 低分情况：优先检查工作年限
            work_years = exp_detail.get("工作经验_年限", 0)
            if work_years < 30:  # 少于3年
                suggestions.append(SuggestionGenerator.SUGGESTION_TEMPLATES["experience"]["low_work_years"])
            # 学历层次低
            elif exp_detail.get("教育背景_学历层次", 0) < 10:
                suggestions.append(SuggestionGenerator.SUGGESTION_TEMPLATES["experience"]["low_education"])
            # 学校层次低
            elif exp_detail.get("教育背景_学校层次", 0) < 7:
                suggestions.append(SuggestionGenerator.SUGGESTION_TEMPLATES["experience"]["low_school"])
            # 实习时长短
            elif exp_detail.get("实习经验_时长", 0) < 5:
                suggestions.append(SuggestionGenerator.SUGGESTION_TEMPLATES["experience"]["low_internship"])

        # 项目经验建议（最多1条）
        proj_detail = project.get("detail_scores", {})
        proj_score = project.get("score", 0)

        if proj_score < 60:
            # 低分情况：优先检查项目数量
            if proj_detail.get("项目数量", 0) < 2:
                suggestions.append(SuggestionGenerator.SUGGESTION_TEMPLATES["project"]["low_quantity"])
            # 项目质量低
            elif proj_detail.get("平均质量", 0) < 25:
                suggestions.append(SuggestionGenerator.SUGGESTION_TEMPLATES["project"]["low_quality"])

        # 软技能建议（最多1条）
        soft_detail = soft_skill.get("detail_scores", {})
        soft_score = soft_skill.get("score", 0)

        if soft_score < 60:
            # 低分情况：优先检查覆盖面
            if soft_detail.get("覆盖面", 0) < 15:
                suggestions.append(SuggestionGenerator.SUGGESTION_TEMPLATES["soft_skill"]["low_coverage"])
            # 团队协作少
            elif soft_detail.get("团队协作", 0) < 10:
                suggestions.append(SuggestionGenerator.SUGGESTION_TEMPLATES["soft_skill"]["low_teamwork"])
            # 领导力少
            elif soft_detail.get("领导力", 0) < 5:
                suggestions.append(SuggestionGenerator.SUGGESTION_TEMPLATES["soft_skill"]["low_leadership"])

        # 如果没有任何建议（说明各方面都不错），给出一些通用的提升建议
        if not suggestions:
            suggestions = [
                {
                    "category": "持续提升",
                    "problem_analysis": "您的简历整体表现优秀，但技术发展日新月异，需要持续学习保持竞争力。",
                    "action_steps": [
                        "订阅优质技术博客和公众号，每天至少阅读1篇技术文章",
                        "每年参加1-2次技术会议或技术沙龙，了解行业最新趋势",
                        "每季度学习1个新技术或框架，保持技术敏感度",
                        "定期复盘总结，将所学知识整理成技术博客或分享材料"
                    ],
                    "before_after": "改进前：技能栈：Python、Django（2年未更新）\\n改进后：技能栈：Python、Django、FastAPI（新增）；持续关注AI、云原生等新兴技术领域；年度学习总结：掌握Rust、K8s等5项新技术",
                    "expected_benefit": "保持技术竞争力，为职业发展打开更多可能性。",
                    "priority": "低"
                },
                {
                    "category": "个人品牌",
                    "problem_analysis": "您的技术能力扎实，但缺乏个人品牌建设，行业影响力和知名度有限。",
                    "action_steps": [
                        "在CSDN、掘金、Medium等平台开设技术博客，每月至少发布2篇原创文章",
                        "在GitHub上维护高质量开源项目，贡献代码或文档",
                        "参与技术社区讨论，在Stack Overflow、知乎等平台回答问题",
                        "参加线下技术沙龙或会议，进行技术分享和演讲"
                    ],
                    "before_after": "改进前：（无个人品牌相关内容）\\n改进后：技术博客：CSDN博客专家，发表原创文章50+篇，累计阅读10万+；GitHub：维护3个开源项目，总计500+ star；技术分享：在5场技术会议担任演讲嘉宾",
                    "expected_benefit": "建立行业影响力，获得更多职业发展机会。",
                    "priority": "中"
                }
            ]

        return suggestions

    @staticmethod
    def generate_priority_suggestions(
        analysis_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        生成优先级改进建议（Top 5）

        Args:
            analysis_results: 分析结果

        Returns:
            优先级建议列表
        """
        all_suggestions = SuggestionGenerator.generate_suggestions(
            analysis_results,
            analysis_results.get("resume_data", {})
        )

        # 按优先级排序
        priority_order = {"高": 0, "中": 1, "低": 2}
        sorted_suggestions = sorted(
            all_suggestions,
            key=lambda x: priority_order.get(x.get("priority", "中"), 1)
        )

        # 取前5个
        return sorted_suggestions[:5]
