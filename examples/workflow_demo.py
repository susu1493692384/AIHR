# -*- coding: utf-8 -*-
"""
示例：完整的简历分析流程演示
展示从输入到LLM调用的完整链路
"""
import asyncio
import json
from pathlib import Path

# 模拟导入（实际使用时取消注释）
# from langchain_zhipu import ChatZhipuAI
# from agents import OrchestratorAgent


async def demonstrate_complete_workflow():
    """演示完整的工作流程"""

    print("="*80)
    print("AI简历分析系统 - 完整流程演示")
    print("="*80)

    # ========================================
    # 步骤1: 初始化LLM
    # ========================================
    print("\n[步骤1] 初始化LLM")
    print("-" * 80)

    # 实际代码:
    # llm = ChatZhipuAI(
    #     model="glm-4",
    #     temperature=0.3,
    #     api_key="your-api-key"
    # )

    print("[OK] LLM: ChatZhipuAI(model='glm-4', temperature=0.3)")

    # ========================================
    # 步骤2: 创建OrchestratorAgent
    # ========================================
    print("\n[步骤2] 创建OrchestratorAgent")
    print("-" * 80)

    # 实际代码:
    # orchestrator = OrchestratorAgent(llm, verbose=True)

    print("✓ OrchestratorAgent已创建")
    print("  - ParsingAgent")
    print("  - StructureMappingAgent")
    print("  - CleaningAgent")
    print("  - DeduplicationAgent")
    print("  - AnalysisAgent")
    print("  - OptimizationAgent")
    print("  - ReportAgent")

    # ========================================
    # 步骤3: 准备输入数据
    # ========================================
    print("\n[步骤3] 准备输入数据")
    print("-" * 80)

    input_data = {
        "file_path": "resumes/zhang_san.pdf",
        "text": None,
        "job_requirements": "5年以上Python开发经验，熟悉Django/Flask框架",
        "report_types": ["full", "hr_summary"]
    }

    print(f"✓ 输入文件: {input_data['file_path']}")
    print(f"✓ 岗位要求: {input_data['job_requirements']}")
    print(f"✓ 报告类型: {', '.join(input_data['report_types'])}")

    # ========================================
    # 步骤4: 执行分析（模拟）
    # ========================================
    print("\n[步骤4] 执行分析流程")
    print("-" * 80)

    # 实际代码:
    # result = await orchestrator.run(input_data)

    # 模拟数据流转:
    print("\n[4.1] 解析简历 (ParsingAgent)")
    parsed_data = {
        "raw_text": "张三\n电话：138-0013-8000\n邮箱：zhangsan@example.com",
        "file_type": "pdf"
    }
    print(f"  提取文本: {parsed_data['raw_text'][:30]}...")

    print("\n[4.2] 结构映射 (StructureMappingAgent)")
    mapped_data = {
        "personal_info": {
            "name": "张三",
            "phone": "138-0013-8000",
            "email": "zhangsan@example.com"
        },
        "skills": ["Python", "Java", "Django"],
        "work_experience": [
            {
                "company": "ABC公司",
                "start_date": "2020.01",
                "end_date": "至今"
            }
        ]
    }
    print(f"  识别姓名: {mapped_data['personal_info']['name']}")
    print(f"  识别技能: {', '.join(mapped_data['skills'])}")

    print("\n[4.3] 数据清洗 (CleaningAgent)")
    cleaned_data = {
        "personal_info": {
            "name": "张三",
            "phone": "13800138000",  # 标准化
            "email": "zhangsan@example.com"
        },
        "work_experience": [
            {
                "company": "ABC公司",
                "start_date": "2020-01",  # 标准化
                "end_date": "至今"
            }
        ],
        "skills": [
            {"name": "Python", "level": "熟练"},  # 补全
            {"name": "Java", "level": "熟悉"},
            {"name": "Django", "level": "熟练"}
        ]
    }
    print(f"  电话标准化: {cleaned_data['personal_info']['phone']}")
    print(f"  日期标准化: {cleaned_data['work_experience'][0]['start_date']}")
    print(f"  技能补全: {cleaned_data['skills'][0]['name']} ({cleaned_data['skills'][0]['level']})")

    # ========================================
    # 步骤5: 关键！LLM调用详情
    # ========================================
    print("\n[步骤5] LLM调用详情 - 技术能力分析")
    print("=" * 80)

    # 获取Prompt
    from prompts import prompt_manager

    system_prompt = prompt_manager.get_system_prompt("technical_analysis")
    user_prompt_template = prompt_manager.get_user_prompt("technical_analysis")

    # 格式化用户Prompt
    formatted_user_prompt = user_prompt_template.format(
        resume_data=json.dumps(cleaned_data, ensure_ascii=False, indent=2),
        job_requirements=input_data['job_requirements']
    )

    print("\n📤 System Prompt (部分):")
    print("-" * 80)
    print(system_prompt[:300] + "...")

    print("\n📤 User Prompt (部分):")
    print("-" * 80)
    print(formatted_user_prompt[:400] + "...")

    # 构造消息
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": formatted_user_prompt}
    ]

    print(f"\n📨 发送消息给LLM:")
    print(f"  - System消息: {len(system_prompt)} 字符")
    print(f"  - User消息: {len(formatted_user_prompt)} 字符")
    print(f"  - 总消息数: 2")

    # 模拟LLM响应（实际代码: response = await llm.ainvoke(messages)）
    print("\n📥 LLM响应（模拟）:")
    print("-" * 80)

    mock_llm_response = {
        "score": 85,
        "detail_scores": {
            "技能广度": 28,
            "技能深度": 27,
            "技能相关性": 18,
            "技术验证度": 12
        },
        "insights": [
            "技术栈全面，涵盖Python、Java和Django",
            "有4年以上工作经验",
            "Django框架应用熟练"
        ],
        "highlights": [
            "精通Python后端开发",
            "熟练使用Django框架"
        ],
        "weaknesses": [
            "前端技术相对薄弱"
        ]
    }

    print(json.dumps(mock_llm_response, ensure_ascii=False, indent=2))

    # ========================================
    # 步骤6: 汇总所有维度分析
    # ========================================
    print("\n[步骤6] 汇总分析结果")
    print("-" * 80)

    analysis_results = {
        "technical_analysis": mock_llm_response,
        "experience_analysis": {"score": 75, "detail_scores": {}, "insights": [], "highlights": [], "weaknesses": []},
        "project_analysis": {"score": 90, "detail_scores": {}, "insights": [], "highlights": [], "weaknesses": []},
        "soft_skill_analysis": {"score": 70, "detail_scores": {}, "insights": [], "highlights": [], "weaknesses": []},
        "total_score": 82.5,  # 加权计算
        "score_breakdown": {
            "technical": {"score": 85, "weight": 0.25, "weighted_score": 21.25},
            "experience": {"score": 75, "weight": 0.20, "weighted_score": 15.0},
            "project": {"score": 90, "weight": 0.40, "weighted_score": 36.0},
            "soft_skill": {"score": 70, "weight": 0.15, "weighted_score": 10.5}
        }
    }

    print(f"  技术能力: {analysis_results['technical_analysis']['score']}分")
    print(f"  经验背景: {analysis_results['experience_analysis']['score']}分")
    print(f"  项目经验: {analysis_results['project_analysis']['score']}分")
    print(f"  软技能: {analysis_results['soft_skill_analysis']['score']}分")
    print(f"  ─────────────────────────────────")
    print(f"  综合评分: {analysis_results['total_score']}分")

    # ========================================
    # 步骤7: 最终输出
    # ========================================
    print("\n[步骤7] 最终输出")
    print("=" * 80)

    final_result = {
        "success": True,
        "state": {
            "steps_completed": [
                "parse", "structure_mapping", "clean",
                "deduplicate", "analyze", "optimize", "report"
            ],
            "total_score": 82.5,
            "report_types": ["full", "hr_summary"]
        },
        "reports": {
            "full": {
                "summary": "候选人技术能力优秀，项目经验丰富，建议面试",
                "detailed_analysis": analysis_results
            },
            "hr_summary": {
                "candidate_name": "张三",
                "total_score": 82.5,
                "recommendation": "建议面试"
            }
        }
    }

    print("\n✓ 分析完成！")
    print(f"  - 完成步骤: {len(final_result['state']['steps_completed'])} 个")
    print(f"  - 综合评分: {final_result['state']['total_score']} 分")
    print(f"  - 生成报告: {', '.join(final_result['state']['report_types'])}")

    print("\n" + "=" * 80)
    print("演示完成")
    print("=" * 80)

    return final_result


def show_prompt_template_examples():
    """展示Prompt模板示例"""
    print("\n" + "="*80)
    print("Prompt模板示例")
    print("="*80)

    from prompts import prompt_manager

    # 列出所有可用的Prompt
    print("\n📋 已注册的Prompt模板:")
    for prompt_name in prompt_manager.list_prompts():
        print(f"  - {prompt_name}")

    # 展示技术分析Prompt
    print("\n" + "="*80)
    print("技术分析Prompt详情")
    print("="*80)

    system_prompt = prompt_manager.get_system_prompt("technical_analysis")
    user_prompt = prompt_manager.get_user_prompt("technical_analysis")

    print("\nSystem Prompt:")
    print(system_prompt)

    print("\nUser Prompt Template:")
    print(user_prompt)


def show_data_transformation_examples():
    """展示数据转换示例"""
    print("\n" + "="*80)
    print("数据转换示例")
    print("="*80)

    # 原始文本
    raw_text = """张三
电话：138-0013-8000
邮箱： zhangsan@example.com
技能：Python, Java, Django
工作经历：
2020.01 - 至今：ABC公司，软件工程师
2018.06 - 2019.12：XYZ公司，初级工程师"""

    print("\n1️⃣ 原始文本:")
    print(raw_text)

    # 解析后
    parsed = {
        "raw_text": raw_text,
        "file_type": "pdf"
    }

    print("\n2️⃣ 解析后:")
    print(json.dumps(parsed, ensure_ascii=False, indent=2))

    # 结构化后
    structured = {
        "personal_info": {
            "name": "张三",
            "phone": "138-0013-8000",
            "email": " zhangsan@example.com "
        },
        "skills": ["Python", "Java", "Django"],
        "work_experience": [
            {"company": "ABC公司", "start_date": "2020.01", "end_date": "至今", "position": "软件工程师"},
            {"company": "XYZ公司", "start_date": "2018.06", "end_date": "2019.12", "position": "初级工程师"}
        ]
    }

    print("\n3️⃣ 结构化后:")
    print(json.dumps(structured, ensure_ascii=False, indent=2))

    # 清洗后
    cleaned = {
        "personal_info": {
            "name": "张三",
            "phone": "13800138000",  # 去除分隔符
            "email": "zhangsan@example.com"  # 去除空格
        },
        "skills": [
            {"name": "Python", "level": "熟练"},
            {"name": "Java", "level": "熟练"},
            {"name": "Django", "level": "熟练"}
        ],
        "work_experience": [
            {"company": "ABC公司", "start_date": "2020-01", "end_date": "至今", "position": "软件工程师"},
            {"company": "XYZ公司", "start_date": "2018-06", "end_date": "2019-12", "position": "初级工程师"}
        ]
    }

    print("\n4️⃣ 清洗后:")
    print(json.dumps(cleaned, ensure_ascii=False, indent=2))

    # 发送给LLM的JSON
    print("\n5️⃣ 发送给LLM的JSON:")
    print(json.dumps(cleaned, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    print("\n" + "="*80)
    print("AI简历分析系统 - 演示程序")
    print("="*80)

    # 1. 展示完整流程
    asyncio.run(demonstrate_complete_workflow())

    # 2. 展示Prompt模板
    show_prompt_template_examples()

    # 3. 展示数据转换
    show_data_transformation_examples()

    print("\n" + "="*80)
    print("✅ 演示完成")
    print("="*80)
    print("\n💡 提示: 运行实际分析时，请使用:")
    print("   streamlit run app/streamlit_app.py")
    print("="*80 + "\n")
