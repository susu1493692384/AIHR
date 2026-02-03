# -*- coding: utf-8 -*-
"""简化版演示程序 - 避免Windows控制台编码问题"""
import json
import sys
from io import StringIO

# 重定向输出以避免编码问题
old_stdout = sys.stdout
sys.stdout = StringIO()

try:
    from prompts import prompt_manager

    print("="*80)
    print("AI Resume Analysis System - Prompt Configuration Demo")
    print("="*80)

    # 1. 列出所有Prompt
    print("\n1. Available Prompts:")
    print("-"*80)
    prompts = prompt_manager.list_prompts()
    for i, name in enumerate(prompts, 1):
        print(f"   {i}. {name}")

    # 2. 展示技术分析Prompt
    print("\n2. Technical Analysis Prompt:")
    print("-"*80)

    system_prompt = prompt_manager.get_system_prompt("technical_analysis")
    user_prompt_template = prompt_manager.get_user_prompt("technical_analysis")

    print("\n[System Prompt (first 500 chars):]")
    print(system_prompt[:500] + "...")

    print("\n[User Prompt Template:]")
    print(user_prompt_template)

    # 3. 展示数据如何填充
    print("\n3. Data Transformation:")
    print("-"*80)

    # 模拟简历数据
    resume_data = {
        "personal_info": {
            "name": "Zhang San",
            "phone": "13800138000",
            "email": "zhangsan@example.com"
        },
        "skills": [
            {"name": "Python", "level": "Proficient"},
            {"name": "Java", "level": "Familiar"}
        ],
        "work_experience": [
            {
                "company": "ABC Company",
                "start_date": "2020-01",
                "end_date": "present"
            }
        ]
    }

    print("\n[Resume Data (Python Dict):]")
    print(json.dumps(resume_data, indent=2))

    # 转换为JSON字符串
    resume_json = json.dumps(resume_data, ensure_ascii=False, indent=2)

    print("\n[Resume Data (JSON String):]")
    print(resume_json[:300] + "...")

    # 填充到Prompt
    formatted_prompt = user_prompt_template.format(
        resume_data=resume_json,
        job_requirements="5+ years Python experience, Django/Flask"
    )

    print("\n[Formatted User Prompt (first 400 chars):]")
    print(formatted_prompt[:400] + "...")

    # 4. 展示发送给LLM的完整消息
    print("\n4. Message Sent to LLM:")
    print("-"*80)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": formatted_prompt}
    ]

    print(f"\nSystem message length: {len(system_prompt)} characters")
    print(f"User message length: {len(formatted_prompt)} characters")
    print(f"Total messages: 2")

    # 5. 模拟LLM响应
    print("\n5. Mock LLM Response:")
    print("-"*80)

    mock_response = {
        "score": 85,
        "detail_scores": {
            "Skill Breadth": 28,
            "Skill Depth": 27,
            "Relevance": 18,
            "Validation": 12
        },
        "insights": [
            "Comprehensive tech stack covering Python and Java",
            "4+ years of work experience",
            "Proficient in Django framework"
        ],
        "highlights": [
            "Expert in Python backend development",
            "Skilled in Django framework"
        ],
        "weaknesses": [
            "Limited frontend experience"
        ]
    }

    print(json.dumps(mock_response, indent=2, ensure_ascii=False))

    # 6. 展示调用链
    print("\n6. Call Chain:")
    print("-"*80)

    call_chain = """
Streamlit Frontend (app/streamlit_app.py)
    |
    | asyncio.run(orchestrator.run(input_data))
    v
OrchestratorAgent (agents/orchestrator.py)
    |
    | await analysis_agent.run(resume_data, job_requirements)
    v
AnalysisAgent (agents/analysis_agent.py)
    |
    | prompt_manager.get_user_prompt("technical_analysis")
    | user_prompt.format(resume_data=..., job_requirements=...)
    | await llm.ainvoke([system_msg, user_msg])
    v
LLM (ChatZhipuAI / ChatOpenAI / etc.)
    |
    | Returns JSON response
    v
Parse and Return Results
    """

    print(call_chain)

    print("\n" + "="*80)
    print("Demo Complete")
    print("="*80)

    # 获取输出
    output = sys.stdout.getvalue()

finally:
    # 恢复stdout
    sys.stdout = old_stdout

# 打印输出（使用utf-8编码）
print(output.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore'))
