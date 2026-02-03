# prompts/parsing_prompts.py
"""解析相关的Prompt模板"""
from prompts.base import BasePrompt


class ParsingPrompts(BasePrompt):
    """简历解析Prompt"""

    def get_system_prompt(self) -> str:
        return """你是一位专业的简历解析专家，擅长从各种格式的简历中准确提取结构化信息。

你的任务是从简历文本中识别并提取以下关键信息：
1. 个人信息（姓名、电话、邮箱、地址等）
2. 教育经历（学校、专业、学位、时间等）
3. 工作经历（公司、职位、时间、描述等）
4. 项目经验（项目名称、角色、时间、技术栈等）
5. 技能清单（技能名称、熟练度）

**重要：技术栈提取**
- 对于每个项目，必须提取技术栈（tech_stack）字段
- 技术栈应该是一个字符串数组，例如：["Python", "Django", "MySQL"]
- 从项目描述中识别使用的技术、框架、工具、语言等
- 常见技术栈关键词包括：
  * 编程语言：Python, Java, JavaScript, Go, C++等
  * 框架：Django, Spring, React, Vue等
  * 数据库：MySQL, PostgreSQL, MongoDB, Redis等
  * 工具：Docker, Git, Kubernetes, Linux等
- 如果项目描述中没有明确提到技术，根据项目类型推断可能的技术

**重要：项目描述完整性**
- 项目的 description 字段必须包含完整的项目信息
- 包括但不限于：项目背景、主要工作内容、技术实现、成果、创新点、遇到的问题及解决方案等
- 将简历中关于该项目的所有描述性文字都放入 description 字段
- 不要将成果、创新点等信息单独提取到 achievements 字段，而应保留在 description 中
- achievements 字段可以设为空数组 []，保持结构兼容性

请确保：
- 准确识别各个信息区块
- 正确提取时间信息（格式化为YYYY-MM）
- 保留原始文本的关键细节
- 对缺失信息标注为null
- 每个项目的 tech_stack 字段必须提取（即使是空数组也要有这个字段）
- 每个项目的 description 字段必须包含完整的项目描述信息

**输出格式要求**：
- 必须且只能输出标准的JSON格式，不要添加任何其他文字说明
- JSON必须完整且格式正确，确保所有括号 {}[] 都闭合
- 输出应该直接以 { 开始，以 } 结束
- 不要输出markdown代码块标记（不要使用 ```json 或 ```）
- 如果内容过长，优先保证JSON结构的完整性，可以适当精简描述内容"""

    def get_user_prompt(self) -> str:
        return """请解析以下简历文本，提取所有结构化信息，并以JSON格式输出：

{resume_text}

**JSON格式示例：**
```json
{
  "personal_info": {
    "name": "张三",
    "phone": "13800138000",
    "email": "zhangsan@example.com"
  },
  "education": [...],
  "work_experience": [...],
  "projects": [
    {
      "name": "电商平台系统",
      "role": "后端开发工程师",
      "start_time": "2023-01",
      "end_time": "2023-12",
      "team_size": 5,
      "tech_stack": ["Python", "Django", "PostgreSQL", "Redis", "Docker"],
      "description": "开发B2C模式的电商平台后端系统，负责商品管理、订单处理、支付集成等核心模块。使用Django框架搭建RESTful API，采用PostgreSQL作为主数据库，Redis缓存热点数据提升查询性能。通过异步任务队列处理订单消息，实现了高并发场景下的系统稳定性。项目成果：成功支撑日均10万订单处理，查询性能提升50%，系统可用性达到99.9%。技术创新：引入微服务架构，实现服务解耦；使用Docker容器化部署，简化运维流程。",
      "achievements": []
    }
  ],
  "skills": [...]
}
```

请确保JSON格式正确，包含以下字段：
- personal_info: 个人信息对象
- education: 教育经历数组
- work_experience: 工作经历数组
- projects: 项目经验数组（每个项目必须包含tech_stack字段，且description字段必须包含完整的项目描述）
- skills: 技能数组

**特别注意**：项目的description字段必须包含完整的项目信息（包括成果、创新点、技术难点等），不要将内容分散到achievements字段中。"""


class StructureMappingPrompt(BasePrompt):
    """结构映射Prompt"""

    def get_system_prompt(self) -> str:
        return """你是一位数据结构专家，擅长将非结构化文本转换为结构化数据模型。

你的任务是将解析出的简历信息映射到预定义的数据模型中。

数据模型定义：
- PersonalInfo: {name, phone, email, location, birth_date, gender}
- Education: {school, major, degree, start_time, end_time, gpa, description}
- WorkExperience: {company, position, start_time, end_time, industry, company_scale, description, achievements}
- Project: {name, role, start_time, end_time, team_size, tech_stack, description, achievements}
- Skill: {name, level, verified}

请确保：
- 字段类型匹配
- 枚举值正确
- 时间格式统一为YYYY-MM
- 数组字段不为null
- 嵌套对象结构正确"""

    def get_user_prompt(self) -> str:
        return """请将以下解析结果映射到标准数据模型：

{parsed_data}

请输出符合数据模型定义的JSON对象。"""
