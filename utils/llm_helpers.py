# utils/llm_helpers.py
"""LLM辅助函数 - 通用的LLM查询功能"""
import os
from functools import lru_cache
from typing import List, Dict
from langchain_zhipu import ChatZhipuAI


@lru_cache(maxsize=1)
def get_llm():
    """
    获取LLM实例（缓存，支持环境变量配置）

    环境变量配置：
    - ZHIPU_API_KEY: API密钥（必需）
    - ZHIPU_MODEL: 模型名称（可选，默认 glm-4-flash）
    - ZHIPU_TEMPERATURE: 温度参数（可选，默认 0.3）

    Returns:
        ChatZhipuAI: LLM实例
    """
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        raise ValueError("未配置ZHIPU_API_KEY环境变量")

    # 从环境变量读取模型和温度参数
    model = os.getenv("ZHIPU_MODEL", "glm-4-flash")
    temperature = float(os.getenv("ZHIPU_TEMPERATURE", "0.3"))

    llm_instance = ChatZhipuAI(
        model=model,
        temperature=temperature,
        api_key=api_key
    )
    return llm_instance


def get_skill_description(skill_name: str, level: str = "了解") -> str:
    """
    获取技能描述（使用LLM生成）

    Args:
        skill_name: 技能名称
        level: 熟练度等级

    Returns:
        str: 技能描述
    """
    llm = get_llm()

    prompt = f"""请简单描述以下技能是什么？（1-2句话）

技能名称：{skill_name}
熟练度：{level}

要求：
1. 简洁明了，1-2句话
2. 说明这个技能是什么、用来做什么
3. 不要使用markdown格式
4. 不要包含示例代码

请直接返回描述内容："""

    try:
        response = llm.invoke(prompt)
        description = response.content.strip()

        # 清理可能的markdown格式
        description = description.replace("*", "").replace("#", "").strip()

        return description
    except Exception:
        # 如果LLM调用失败，返回默认描述
        return f"{skill_name}是{level}级别的技术能力。"


def get_school_description(school_name: str) -> str:
    """
    获取学校描述（使用LLM联网搜索生成）

    Args:
        school_name: 学校名称

    Returns:
        str: 学校描述
    """
    llm = get_llm()

    prompt = f"""请提供以下学校的基本信息（2-3句话）：

学校名称：{school_name}

要求：
1. 简洁明了说明该学校的水平，2-3句话
2. 说明学校的性质（如：985/211/双一流/普通本科/职业院校等）
3. 说明学校的主营特色或优势学科
4. 可以提及学校所在城市
5. 不要使用markdown格式

请利用你的联网搜索功能获取最新、准确的信息，然后直接返回描述内容："""

    try:
        response = llm.invoke(prompt)
        description = response.content.strip()

        # 清理可能的markdown格式
        description = description.replace("*", "").replace("#", "").strip()

        return description
    except Exception:
        # 如果LLM调用失败，返回默认描述
        return f"{school_name}是教育机构。"


def get_company_description(company_name: str) -> str:
    """
    获取公司描述（使用LLM联网搜索生成）

    Args:
        company_name: 公司名称

    Returns:
        str: 公司描述
    """
    llm = get_llm()

    prompt = f"""请提供以下公司的基本信息（2-3句话）：

公司名称：{company_name}

要求：
1. 简洁明了，2-3句话
2. 说明公司的主营业务
3. 说明公司的性质（如：上市公司/独角兽/创业公司/国企/外企等）
4. 可以提及公司所在行业或领域
5. 说明公司规模大小
6. 不要使用markdown格式

请利用你的联网搜索功能获取最新、准确的信息，然后直接返回描述内容："""

    try:
        response = llm.invoke(prompt)
        description = response.content.strip()

        # 清理可能的markdown格式
        description = description.replace("*", "").replace("#", "").strip()

        return description
    except Exception:
        # 如果LLM调用失败，返回默认描述
        return f"{company_name}是企业。"


def generate_interview_questions(
    project_name: str,
    project_role: str,
    tech_stack: list,
    project_description: str,
    num_questions: int = 3
) -> list:
    """
    根据项目信息生成面试问题（由浅到深）

    Args:
        project_name: 项目名称
        project_role: 项目角色
        tech_stack: 技术栈列表
        project_description: 项目描述
        num_questions: 生成问题数量（默认3个）

    Returns:
        list: 面试问题列表，每个问题包含 question 和 answer 字段
    """
    llm = get_llm()

    if not project_description:
        return []

    # 格式化技术栈
    tech_str = ', '.join(tech_stack[:5]) if tech_stack else "未明确"

    # 构建提示词 - 改进版，避免占位符
    system_prompt = f"""你是一位资深的技术面试官，擅长根据候选人的项目经验设计面试问题。

你的任务是根据项目信息，生成{num_questions}面试问题和参考答案。

**问题要求**：
1. 基础问题：询问项目背景、职责、使用的技术
2. 中级问题：询问技术选型、遇到的问题及解决方案
3. 深度问题：询问架构设计、性能优化、技术难点

**输出格式示例（仅供参考，请根据实际项目生成具体问题）**：

Q1: 请简要介绍一下这个项目，以及你在其中主要负责什么工作？
A1: [根据项目实际情况生成答案]

Q2: 在开发过程中，你们遇到的最大技术挑战是什么？你是如何解决的？
A2: [根据项目实际情况生成答案]

Q3: 如果让你重新设计这个项目，你会如何改进架构或技术方案？
A3: [根据项目实际情况生成答案]

**重要提示**：
- 问题必须是完整句子，不要使用[基础问题]这样的占位符
- 每个问题都要具体、针对性强，结合项目的{tech_str}等技术栈
- 答案要展示技术深度，2-4句话，突出技术要点和量化成果
- 项目描述：{project_description[:200]}..."""

    user_prompt = f"""请根据以下项目信息，生成{num_questions}个面试问题和参考答案：

项目名称：{project_name}
项目角色：{project_role}
使用技术：{tech_str}

项目完整描述：
{project_description}

请严格按照以下格式输出（不要使用任何方括号占位符，直接写具体问题）：

Q1: [具体的面试问题1，询问项目背景和职责]
A1: [2-4句话的参考答案]

Q2: [具体的面试问题2，询问技术挑战或解决方案]
A2: [2-4句话的参考答案]

Q3: [具体的面试问题3，询问架构或优化]
A3: [2-4句话的参考答案]

注意：问题必须是完整句子，不要使用[基础问题]、[中级问题]、[深度问题]这样的占位符！"""

    try:
        from langchain_core.messages import HumanMessage, SystemMessage

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        response = llm.invoke(messages)
        response_text = response.content.strip() if hasattr(response, 'content') else str(response)

        # 调试：打印LLM原始响应
        print(f"[DEBUG] LLM原始响应:\n{response_text}")
        print(f"[DEBUG] 响应长度: {len(response_text)} 字符")

        # 解析响应
        questions = _parse_interview_questions(response_text)

        # 调试：打印解析结果
        print(f"[DEBUG] 解析得到 {len(questions)} 个问题")
        for i, q in enumerate(questions):
            print(f"[DEBUG] Q{i+1}: {q.get('question', '')[:50]}...")

        # 检查是否包含占位符，如果有则使用备用方案
        if questions and any('[基础问题]' in q.get('question', '') or '[中级问题]' in q.get('question', '') or '[深度问题]' in q.get('question', '') for q in questions):
            print(f"[WARNING] 检测到占位符，使用备用解析")
            questions = _parse_interview_questions_fallback(response_text)

        return questions[:num_questions]  # 限制返回数量

    except Exception as e:
        # 如果LLM调用失败，返回空列表
        print(f"[LLM错误] 生成面试问题失败: {e}")
        import traceback
        traceback.print_exc()
        return []


def _parse_interview_questions(response_text: str) -> list:
    """
    解析LLM返回的面试问题

    Args:
        response_text: LLM响应文本

    Returns:
        list: 面试问题列表
    """
    import re

    questions = []

    # 先清理文本，移除可能的markdown代码块标记
    text = response_text.strip()
    text = re.sub(r'```.*?\n?', '', text)

    # 使用正则表达式提取所有 Q&A 对
    # 匹配模式：Q1[：:] 问题内容 (可能包含"参考答案：") A1[：:] 答案内容
    # 或者：Q1[：:] 问题内容 A1[：:] 答案内容

    # 策略：先找到所有的 Q 和 A 标记
    lines = text.split('\n')

    current_q = None
    current_a = None
    waiting_for_answer = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 检查是否是问题行 (Q1:, Q1：, Q2:, Q2：, 等等)
        q_match = re.match(r'^Q(\d+)[：:]\s*(.+)', line, re.IGNORECASE)
        if q_match:
            # 保存上一个 Q&A 对
            if current_q:
                # 清理答案：移除可能的前缀
                clean_answer = current_a or "请参考项目描述进行回答"
                if "参考答案：" in clean_answer:
                    clean_answer = clean_answer.split("参考答案：", 1)[-1].strip()
                questions.append({
                    "question": current_q,
                    "answer": clean_answer
                })

            # 提取新问题
            current_q = q_match.group(2).strip()
            # 移除问题末尾可能的"?参考答案"等干扰
            current_q = re.sub(r'\?参考答案.*$', '', current_q).strip()
            current_a = None
            waiting_for_answer = True

        # 检查是否是答案行 (A1:, A1：, A2:, A2：, 等等)
        elif re.match(r'^A\d+[：:]', line, re.IGNORECASE):
            a_match = re.match(r'^A\d+[：:]\s*(.+)', line, re.IGNORECASE)
            if a_match:
                current_a = a_match.group(1).strip()
                waiting_for_answer = False
            else:
                # A标记后面没有内容，跳过
                waiting_for_answer = False

        # 检查是否是"参考答案："开头的行（有些LLM可能这样输出）
        elif line.startswith("参考答案：") and waiting_for_answer:
            current_a = line.split("参考答案：", 1)[-1].strip()
            waiting_for_answer = False

        # 如果已经在答案部分，继续累积答案内容
        elif current_a is not None and not waiting_for_answer and not re.match(r'^Q\d+[：:]', line, re.IGNORECASE):
            # 只有不以Q开头的内容才追加到答案
            current_a += ' ' + line

        # 如果有问题但没有答案，且行不是Q或A开头，可能是延续的问题内容
        elif current_q and current_a is None and waiting_for_answer:
            # 检查这行是否包含答案关键词
            if "参考答案" in line:
                current_a = line.split("参考答案", 1)[-1].strip()
                current_a = current_a.lstrip('：:').strip()
                waiting_for_answer = False
            elif not line.startswith('A') and len(line) > 5:
                # 可能是问题内容的延续
                current_q += ' ' + line

    # 保存最后一个 Q&A 对
    if current_q:
        clean_answer = current_a or "请参考项目描述进行回答"
        if "参考答案：" in clean_answer:
            clean_answer = clean_answer.split("参考答案：", 1)[-1].strip()
        questions.append({
            "question": current_q,
            "answer": clean_answer
        })

    # 如果正则方法没找到任何问题，尝试备用方法：按行分割并智能识别
    if not questions:
        # 备用方法：查找所有问号后面的内容作为答案
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if '？' in line or '?' in line:
                parts = re.split(r'[？?]', line, 1)
                if len(parts) == 2:
                    q = parts[0].strip()
                    a = parts[1].strip()
                    if q and not any(q.startswith(x) for x in ['Q1', 'Q2', 'Q3', 'q1', 'q2', 'q3']):
                        # 移除可能的序号前缀
                        q = re.sub(r'^\d+[.、]\s*', '', q)
                        questions.append({"question": q, "answer": a})

    return questions[:3]  # 最多返回3个问题


def _parse_interview_questions_fallback(response_text: str) -> list:
    """
    备用解析函数 - 当LLM返回占位符时使用更激进的解析策略

    Args:
        response_text: LLM响应文本

    Returns:
        list: 面试问题列表
    """
    import re

    questions = []
    lines = response_text.split('\n')

    # 策略1: 查找包含问号的行，将问号前作为问题，问号后作为答案
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # 查找问号
        if '？' in line or '?' in line:
            # 尝试按问号分割
            parts = re.split(r'[？?]', line, 1)
            if len(parts) == 2:
                q = parts[0].strip()
                a = parts[1].strip()

                # 清理问题前缀（如Q1:、1.等）
                q = re.sub(r'^(Q\d+[:：]|\d+[.、])\s*', '', q)
                q = re.sub(r'\[.*?\]', '', q)  # 移除所有方括号内容

                # 清理答案前缀
                a = re.sub(r'^(A\d+[:：]|参考答案[:：]?)\s*', '', a)
                a = re.sub(r'\[.*?\]', '', a)  # 移除所有方括号内容

                if q and len(q) > 5:  # 问题至少5个字符
                    questions.append({
                        "question": q,
                        "answer": a if a else "请参考项目描述进行回答"
                    })

                    if len(questions) >= 3:
                        break

    # 策略2: 如果策略1没找到足够问题，尝试按段落分割
    if len(questions) < 3:
        # 移除markdown标记
        text = re.sub(r'```.*?', '', response_text)
        paragraphs = re.split(r'\n\n+', text)

        for para in paragraphs:
            para = para.strip()
            if not para or len(para) < 20:
                continue

            # 查找问号位置
            q_end = -1
            for sep in ['？', '?']:
                idx = para.find(sep)
                if idx != -1 and (q_end == -1 or idx < q_end):
                    q_end = idx

            if q_end > 5:  # 找到问号且问题长度合理
                q = para[:q_end + 1].strip()
                a = para[q_end + 1:].strip()

                # 清理内容
                q = re.sub(r'^(Q\d+[:：]|\d+[.、])\s*', '', q)
                q = re.sub(r'\[.*?\]', '', q)
                a = re.sub(r'^(A\d+[:：]|参考答案[:：]?)\s*', '', a)
                a = re.sub(r'\[.*?\]', '', a)

                if q and len(q) > 5:
                    # 避免重复
                    is_duplicate = any(q == existing_q["question"] for existing_q in questions)
                    if not is_duplicate:
                        questions.append({
                            "question": q,
                            "answer": a if a else "请参考项目描述进行回答"
                        })

                        if len(questions) >= 3:
                            break

    # 策略3: 如果还是没找到，使用LLM重新生成
    if len(questions) < 3:
        print("[WARNING] 备用解析未找到足够问题，尝试使用LLM重新生成...")
        try:
            llm = get_llm()
            fallback_prompt = f"""请根据以下内容，生成3个具体的面试问题（不要使用占位符）：

{response_text[:500]}

请严格按照以下格式输出：

Q1: [具体问题1]
A1: [答案1]

Q2: [具体问题2]
A2: [答案2]

Q3: [具体问题3]
A3: [答案3]"""

            response = llm.invoke(fallback_prompt)
            if hasattr(response, 'content'):
                new_response = response.content
            else:
                new_response = str(response)

            # 递归调用标准解析
            questions = _parse_interview_questions(new_response)

        except Exception as e:
            print(f"[ERROR] LLM重新生成失败: {e}")

    return questions[:3]  # 最多返回3个问题
