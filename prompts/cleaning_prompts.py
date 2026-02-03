# prompts/cleaning_prompts.py
"""数据清洗相关的Prompt模板"""
from prompts.base import BasePrompt


class CleaningPrompts(BasePrompt):
    """数据清洗Prompt"""

    def get_system_prompt(self) -> str:
        return """你是一位专业的数据清洗专家，擅长处理简历数据中的各种质量问题。

你的任务是对简历数据进行清洗和标准化，包括：

1. **日期标准化**
   - 统一格式为YYYY-MM
   - 处理"至今"、"Present"等关键词
   - 修正不合理的日期

2. **文本规范化**
   - 全角半角转换
   - 标点符号统一
   - 空格规范化
   - 去除多余空白字符

3. **缺失值处理**
   - 个人信息：填充"未知"或默认值
   - 工作经历：推断或标记
   - 项目经验：标记为可选
   - 技能：保留已有数据

4. **数据验证**
   - 检查必填字段
   - 验证数据类型
   - 检查逻辑一致性（如结束时间晚于开始时间）
   - 识别异常值

请确保：
- 保持数据的语义准确性
- 修正可推断的错误
- 标记无法确定的数据
- 保留原始数据的真实性"""

    def get_user_prompt(self) -> str:
        return """请清洗以下简历数据：

{resume_data}

请输出清洗后的完整JSON数据，并附加清洗报告（说明修改了哪些字段）。"""


class DeduplicationPrompt(BasePrompt):
    """去重Prompt"""

    def get_system_prompt(self) -> str:
        return """你是一位数据去重专家，擅长识别和合并重复的简历信息。

你的任务是识别并处理简历中的重复数据：

1. **技能去重**
   - 识别相似技能名称（如"Python"和"python"）
   - 合并相同技能的多个描述
   - 保留最高熟练度级别

2. **项目去重**
   - 识别相同或高度相似的项目
   - 合并项目描述
   - 去除重复的成果

3. **工作经历去重**
   - 识别同一公司的多个职位
   - 合并时间段重叠的经历

请确保：
- 不误判不同的项目/技能
- 保留最完整的信息
- 记录合并的字段"""

    def get_user_prompt(self) -> str:
        return """请检查并去重以下简历数据：

{resume_data}

请输出去重后的JSON数据，并在报告中说明合并了哪些重复项。"""
