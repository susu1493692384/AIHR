# 简历数据处理流程详解

## 文档信息

- **版本**: v1.0
- **更新日期**: 2026-01-30
- **作者**: AI Resume Analysis System

---

## 目录

1. [LLM解析详细说明](#1-llm解析详细说明)
2. [数据清洗和增强详细说明](#2-数据清洗和增强详细说明)
3. [完整数据处理流程](#3-完整数据处理流程)
4. [数据模型定义](#4-数据模型定义)

---

## 1. LLM解析详细说明

### 1.1 解析流程

```
原始简历文件 (PDF/Word/TXT)
    ↓
FileParserTool.extract_text()
    ↓
简历纯文本
    ↓
ParsingAgent (LLM解析)
    ├─ System Prompt: 解析专家角色定义
    ├─ User Prompt: 简历文本
    └─ LLM调用 → 结构化JSON
    ↓
StructureMapperTool (规则映射)
    ├─ 字段名标准化
    ├─ 数据类型规范化
    └─ 数据验证和修复
    ↓
ParsedResume (解析后的简历)
```

### 1.2 LLM解析的具体内容

#### LLM解析输入

**System Prompt** ([parsing_prompts.py:9-26](prompts/parsing_prompts.py#L9-L26))

```
你是一位专业的简历解析专家，擅长从各种格式的简历中准确提取结构化信息。

你的任务是从简历文本中识别并提取以下关键信息：
1. 个人信息（姓名、电话、邮箱、地址等）
2. 教育经历（学校、专业、学位、时间等）
3. 工作经历（公司、职位、时间、描述等）
4. 项目经验（项目名称、角色、时间、技术栈等）
5. 技能清单（技能名称、熟练度、类别等）

请确保：
- 准确识别各个信息区块
- 正确提取时间信息（格式化为YYYY-MM）
- 保留原始文本的关键细节
- 对缺失信息标注为null
- 对技能进行合理分类

输出必须是标准的JSON格式。
```

**User Prompt** ([parsing_prompts.py:28-38](prompts/parsing_prompts.py#L28-L38))

```
请解析以下简历文本，提取所有结构化信息，并以JSON格式输出：

{resume_text}

请确保JSON格式正确，包含以下字段：
- personal_info: 个人信息对象
- education: 教育经历数组
- work_experience: 工作经历数组
- projects: 项目经验数组
- skills: 技能数组
```

#### LLM解析输出（固定结构）

LLM解析返回的JSON数据**结构是固定的**，包含以下字段：

```json
{
  "personal_info": {
    "name": "张三",
    "phone": "13800138000",
    "email": "zhangsan@example.com",
    "location": "北京市",
    "birth_date": "1990-01",
    "gender": "男"
  },
  "education": [
    {
      "school": "清华大学",
      "major": "计算机科学与技术",
      "degree": "本科",
      "start_time": "2008-09",
      "end_time": "2012-06",
      "gpa": "3.8",
      "description": "主修课程：数据结构、算法、操作系统"
    }
  ],
  "work_experience": [
    {
      "company": "ABC科技公司",
      "position": "软件工程师",
      "start_time": "2012-07",
      "end_time": "2016-08",
      "industry": "互联网",
      "company_scale": "1000-9999",
      "description": "负责后端开发工作",
      "achievements": ["完成了XX系统开发", "性能提升30%"]
    }
  ],
  "projects": [
    {
      "name": "电商系统",
      "role": "后端开发",
      "start_time": "2014-01",
      "end_time": "2015-12",
      "team_size": 10,
      "tech_stack": ["Python", "Django", "MySQL"],
      "description": "开发电商平台后端系统",
      "achievements": ["实现了订单模块", "优化了数据库查询"],
      "complexity_indicators": {
        "has_high_concurrency": true,
        "large_team": false
      }
    }
  ],
  "skills": [
    {
      "name": "Python",
      "category": "编程语言",
      "level": "熟练"
    },
    {
      "name": "React",
      "category": "框架",
      "level": "熟悉"
    }
  ]
}
```

**固定字段说明**：

| 一级字段 | 类型 | 说明 | 是否必需 |
|---------|------|------|----------|
| `personal_info` | Object | 个人信息 | 是（可为空对象） |
| `education` | Array | 教育经历列表 | 是（可为空数组） |
| `work_experience` | Array | 工作经历列表 | 是（可为空数组） |
| `projects` | Array | 项目经验列表 | 是（可为空数组） |
| `skills` | Array | 技能列表 | 是（可为空数组） |

**注意**：
- ✅ **顶层字段结构固定**：必须包含这5个字段
- ✅ **字段名标准化**：LLM被要求使用英文字段名
- ⚠️ **字段名可能变体**：LLM可能使用中文或不规则字段名（通过规则映射修正）
- ⚠️ **数据质量**：取决于LLM理解能力和简历格式

### 1.3 规则提取（规则映射）

规则提取不提取新数据，而是**标准化LLM解析出的数据**。

#### 规则提取的规则

**文件**：[structure_mapper.py](tools/parsing/structure_mapper.py)

**规则1：字段名标准化映射**

LLM可能返回各种变体的字段名，规则映射表将其统一：

```python
FIELD_MAPPING = {
    # 个人信息相关
    "个人信息": "personal_info",
    "基本信息": "personal_info",
    "姓名": "name",
    "name": "name",
    "电话": "phone",
    "手机": "phone",
    "邮箱": "email",
    "email": "email",
    # ... 185个映射规则
}
```

**示例**：

```python
# LLM可能返回
{
  "个人信息": {"姓名": "张三", "手机": "138..."},
  "教育背景": [{"大学": "清华"}]
}

# 规则映射后
{
  "personal_info": {"name": "张三", "phone": "138..."},
  "education": [{"school": "清华"}]
}
```

**规则2：数据类型规范化**

- **日期标准化**：统一为 `YYYY-MM` 格式
  - `"2020年1月"` → `"2020-01"`
  - `"2020.01"` → `"2020-01"`
  - `"2020/01"` → `"2020-01"`

- **学位标准化**：统一为中文标准值
  ```python
  DEGREE_NORMALIZATION = {
      "phd": "博士",
      "master": "硕士",
      "bachelor": "本科",
      "大专": "大专",
      "专科": "大专"
  }
  ```

- **技能类别标准化**：
  ```python
  SKILL_CATEGORY_MAPPING = {
      "编程语言": "language",
      "框架": "framework",
      "数据库": "database",
      "工具": "tool",
      "其他": "other"
  }
  ```

- **技能等级标准化**：
  ```python
  SKILL_LEVEL_MAPPING = {
      "精通": "精通",
      "expert": "精通",
      "熟练": "熟练",
      "proficient": "熟练",
      "熟悉": "熟悉",
      "了解": "了解",
      "beginner": "了解"
  }
  ```

**规则3：数据验证和修复**

- 确保数组字段存在且为列表
- 过滤无效技能（name为空的技能）
- 确保必需字段有默认值

### 1.4 提取完成后的数据

**ParsedResume 数据模型** ([models.py:80-108](core/models.py#L80-L108))

```python
@dataclass
class ParsedResume:
    """解析后的简历数据模型"""
    resume_id: str = None              # 简历ID（自动生成UUID）
    file_name: str = ""                # 文件名
    file_type: str = ""                # 文件类型 (pdf/docx)
    parse_time: datetime = None        # 解析时间
    personal_info: PersonalInfo = None # 个人信息对象
    education: List[Education] = None  # 教育经历列表
    work_experience: List[WorkExperience] = None  # 工作经历列表
    projects: List[Project] = None     # 项目经验列表
    skills: List[Skill] = None         # 技能列表
    others: Dict[str, Any] = None      # 其他字段
```

**PersonalInfo 子模型** ([models.py:23-34](core/models.py#L23-L34))

```python
@dataclass
class PersonalInfo:
    """个人信息数据模型"""
    name: str = None           # 姓名
    phone: str = None          # 电话（已去除非数字字符）
    email: str = None          # 邮箱（已转小写）
    location: str = None       # 地址
    birth_date: str = None     # 出生日期（YYYY-MM格式）
    gender: str = None         # 性别（"男"/"女"）
```

**Education 子模型** ([models.py:37-49](core/models.py#L37-L49))

```python
@dataclass
class Education:
    """教育经历数据模型"""
    school: str = ""           # 学校名称
    major: str = ""            # 专业
    degree: str = ""           # 学位（标准化值）
    start_time: str = ""       # 开始时间（YYYY-MM）
    end_time: str = ""         # 结束时间（YYYY-MM）
    gpa: str = None            # GPA
    description: str = None    # 描述
```

**WorkExperience 子模型** ([models.py:52-63](core/models.py#L52-L63))

```python
@dataclass
class WorkExperience:
    """工作经历数据模型"""
    company: str = ""          # 公司名称
    position: str = ""         # 职位
    start_time: str = ""       # 开始时间（YYYY-MM）
    end_time: str = ""         # 结束时间（YYYY-MM）
    industry: str = None       # 行业
    company_scale: str = None  # 公司规模
    description: str = None    # 工作描述
    achievements: list = None  # 工作成就列表
```

**Project 子模型** ([models.py:66-78](core/models.py#L66-L78))

```python
@dataclass
class Project:
    """项目经验数据模型"""
    name: str = ""                      # 项目名称
    role: str = ""                      # 角色
    start_time: str = ""                # 开始时间（YYYY-MM）
    end_time: str = ""                  # 结束时间（YYYY-MM）
    team_size: int = None               # 团队规模
    tech_stack: list = None             # 技术栈列表
    description: str = None             # 项目描述
    achievements: list = None           # 项目成就列表
    complexity_indicators: dict = None  # 复杂度指标
```

**Skill 子模型** ([models.py:70-77](core/models.py#L70-L77))

```python
@dataclass
class Skill:
    """技能数据模型"""
    name: str = ""             # 技能名称
    category: str = "other"    # 技能类别（标准化值）
    level: str = "了解"        # 技能等级（标准化值）
    verified: bool = False     # 是否在项目中验证（后续填充）
```

---

## 2. 数据清洗和增强详细说明

### 2.1 清洗和增强流程

```
ParsedResume (解析后的简历)
    ↓
CleaningAgent.run()
    ├─ 步骤1: 日期标准化
    ├─ 步骤2: 文本清洗
    ├─ 步骤3: 缺失值处理
    └─ 步骤4: 数据去重
    ↓
CleanedResume (清洗后的简历)
```

### 2.2 清洗步骤详解

#### 步骤1：日期标准化

**工具**：[DateNormalizer](tools/cleaning/date_normalizer.py)

**处理字段**：
- `education[].start_time`
- `education[].end_time`
- `work_experience[].start_time`
- `work_experience[].end_time`
- `projects[].start_time`
- `projects[].end_time`

**标准化规则**：

```python
# 支持的输入格式
"2020-01"      → "2020-01"  # 已是标准格式
"2020年1月"    → "2020-01"
"2020.01"      → "2020-01"
"2020/01"      → "2020-01"
"2020"         → "2020-01"  # 缺少月份，默认01月
"至今"         → None       # 特殊值处理
"present"      → None
```

**代码实现**：[structure_mapper.py:534-564](tools/parsing/structure_mapper.py#L534-L564)

```python
@staticmethod
def _normalize_date(date_val: Any) -> Optional[str]:
    """规范化日期为 YYYY-MM 格式"""
    if not date_val:
        return None

    date_str = str(date_val).strip()

    # 已经是标准格式
    if re.match(r'^\d{4}-\d{2}$', date_str):
        return date_str

    # 提取年月信息
    year_match = re.search(r'(\d{4})', date_str)
    month_match = re.search(r'(\d{1,2})[月月.\-/]', date_str)

    if not year_match:
        return None

    year = year_match.group(1)
    month = month_match.group(1).zfill(2) if month_match else "01"

    return f"{year}-{month}"
```

#### 步骤2：文本清洗

**工具**：[TextNormalizer](tools/cleaning/text_normalizer.py)

**处理范围**：所有字符串字段

**清洗规则**：

```python
# 1. 去除多余空格
"  Python  Django  "  → "Python Django"

# 2. 统一引号
'Python'、"Django"  → "Python"、"Django"（全角统一）

# 3. 去除特殊字符
"Python\nDjango"     → "Python Django"
"Python\tDjango"     → "Python Django"

# 4. 去除HTML标签
"<p>Python</p>"      → "Python"

# 5. 去除控制字符
"Python\u200bDjango" → "Python Django"
```

**代码实现**：[cleaning_agent.py:151-173](agents/cleaning_agent.py#L151-L173)

```python
def _count_and_clean_text(self, resume_data: Dict[str, Any]) -> int:
    """清洗文本并返回处理数量"""
    from tools.cleaning.text_normalizer import TextNormalizer

    normalizer = TextNormalizer()
    count = 0

    def clean_dict(obj):
        nonlocal count
        if isinstance(obj, dict):
            return {k: clean_dict(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean_dict(item) for item in obj]
        elif isinstance(obj, str):
            original = obj
            cleaned = normalizer.normalize(obj)
            if original != cleaned:
                count += 1
            return cleaned
        return obj

    clean_dict(resume_data)
    return count
```

#### 步骤3：缺失值处理

**工具**：[MissingValueHandler](tools/cleaning/missing_value_handler.py)

**处理字段**：`personal_info` 的关键字段

**处理策略**：

| 字段 | 缺失处理 | 默认值 |
|------|---------|--------|
| `name` | 不填充（必需字段） | `None` |
| `phone` | 填充为空字符串 | `""` |
| `email` | 填充为空字符串 | `""` |
| `location` | 不填充 | `None` |
| `birth_date` | 不填充 | `None` |
| `gender` | 不填充 | `None` |

**代码实现**：[cleaning_agent.py:175-192](agents/cleaning_agent.py#L175-L192)

```python
def _handle_missing_values(self, resume_data: Dict[str, Any]) -> int:
    """处理缺失值并返回处理数量"""
    from tools.cleaning.missing_value_handler import MissingValueHandler

    handler = MissingValueHandler()

    # 统计缺失值
    missing_count = 0
    if "personal_info" in resume_data:
        for field in ["name", "email", "phone"]:
            if not resume_data["personal_info"].get(field):
                missing_count += 1

    # 填充缺失值
    if missing_count > 0:
        resume_data = handler.handle(resume_data)

    return missing_count
```

#### 步骤4：数据去重

**工具**：[DataDeduplicator](tools/cleaning/data_deduplicator.py)

**去重范围**：
- `skills`：技能去重
- `projects`：项目去重
- `work_experience`：工作经历去重
- `certificates`：证书去重

**去重规则**：

**1. 技能去重**（基于相似度）

```python
# 相似度阈值：85%
for skill in skills:
    for existing in unique_skills:
        similarity = SequenceMatcher(None,
            skill_name.lower(),
            existing_name.lower()
        ).ratio()   #ratio是什么？
        if similarity > 0.85:  # 重复
            removed_count += 1

# 示例：
["Python", "python", "Python编程"]
→ ["Python", "Python编程"]  # 第2个被去除（与第1个相似度100%）
```

**2. 项目去重**（基于项目名）

```python
# 相似度阈值：90%
["电商系统", "电商平台", "OA系统"]
→ ["电商系统", "OA系统"]  # 第2个被去除（与第1个相似度95%）
```

**3. 工作经历去重**（完全匹配）

```python
# 匹配条件：公司名 + 职位
[
  {"company": "ABC", "position": "工程师", "start_time": "2020-01"},
  {"company": "ABC", "position": "工程师", "start_time": "2020-01"}  # 重复
]
→ [
  {"company": "ABC", "position": "工程师", "start_time": "2020-01"}
]
```

**4. 证书去重**（完全匹配）

```python
["CPA", "CPA", "CFA"]
→ ["CPA", "CFA"]  # 第2个CPA被去除
```

**代码实现**：[cleaning_agent.py:367-398](agents/cleaning_agent.py#L367-L398)

```python
def _deduplicate_skills(self, resume_data: Dict[str, Any]) -> int:
    """去重技能（基于相似度）"""
    from difflib import SequenceMatcher

    skills = resume_data["skills"]
    unique_skills = []
    removed_count = 0

    for skill in skills:
        skill_name = skill.get("name", "")
        if not skill_name:
            continue

        # 检查是否与已有技能重复
        is_duplicate = False
        for existing in unique_skills:
            existing_name = existing.get("name", "")
            # 计算相似度
            similarity = SequenceMatcher(
                None,
                skill_name.lower(),
                existing_name.lower()
            ).ratio()
            if similarity > 0.85:  # 相似度阈值85%
                is_duplicate = True
                removed_count += 1
                break

        if not is_duplicate:
            unique_skills.append(skill)

    resume_data["skills"] = unique_skills
    return removed_count
```

### 2.3 数据增强

数据增强在清洗过程中自动完成，主要增强内容：

#### 增强内容1：技能自动分类

**实现**：[converter.py:270-326](tools/analysis/converter.py#L270-L326)

当技能的 `category` 为空或为 `other` 时，根据技能名称自动分类：

```python
def _classify_skill(skill_name: str, config: ScoreConfig) -> str:
    """根据技能名称自动分类"""
    # 1. 精确匹配
    for category, keywords in skill_categories.items():
        if skill_name.lower() in keywords:
            return category

    # 2. 模糊匹配
    for category, keywords in skill_categories.items():
        for keyword in keywords:
            if keyword.lower() in skill_name.lower():
                return category

    # 3. 默认归为 other
    return "other"

# 示例：
# "Python" → "language"
# "会计准则" → "accounting_standards"
# "Excel" → "financial_tools" (财务行业) 或 "tool" (IT行业)
```

#### 增强内容2：技能验证标志

**实现**：[converter.py:183-219](tools/analysis/converter.py#L183-L219)

自动检测技能是否在项目或工作经历中被使用：

```python
def _collect_verified_technologies(
    work_experience: List[WorkExperience],
    projects: List[Project]
) -> Set[str]:
    """从工作经历和项目中收集验证过的技术"""
    verified = set()

    # 从工作经历中提取
    for work in work_experience:
        if work.tech_stack:
            for tech in work.tech_stack:
                verified.add(tech.lower())

    # 从项目中提取
    for project in projects:
        if project.tech_stack:
            for tech in project.tech_stack:
                verified.add(tech.lower())

    return verified

# 示例：
# projects[0].tech_stack = ["Python", "Django"]
# verified = {"python", "django"}
#
# skills = [
#   Skill(name="Python", verified=True),   # 在tech_stack中
#   Skill(name="Java", verified=False)     # 不在tech_stack中
# ]
```

#### 增强内容3：技能智能提取

**实现**：[converter.py:222-267](tools/analysis/converter.py#L222-L267)

当简历中没有技能章节时，从项目技术栈中提取技能：

```python
def _extract_skills_from_projects(
    projects: List[Project],
    config: ScoreConfig
) -> List[Dict[str, Any]]:
    """从项目经验中提取技能信息"""
    extracted_skills = {}

    for project in projects:
        tech_stack = project.tech_stack or []
        for tech in tech_stack:
            if tech and isinstance(tech, str):
                category = _classify_skill(tech, config)
                extracted_skills[tech] = {
                    "name": tech,
                    "category": category,
                    "level": "熟练"  # 项目中使用默认"熟练"
                }

    return list(extracted_skills.values())

# 示例：
# skills = []  # 简历没有技能章节
# projects[0].tech_stack = ["Python", "Django", "MySQL"]
#
# 提取后：
# skills = [
#   Skill(name="Python", category="language", level="熟练"),
#   Skill(name="Django", category="framework", level="熟练"),
#   Skill(name="MySQL", category="database", level="熟练")
# ]
```

### 2.4 清洗后的数据结构

**CleanedResume 数据模型** ([models.py:110-145](core/models.py#L110-L145))

```python
@dataclass
class CleanedResume:
    """清洗后的简历数据模型"""
    original: ParsedResume = None        # 原始解析数据
    cleaned_data: ParsedResume = None    # 清洗后的数据

    # 清洗报告
    cleaning_report: dict = None
    # 示例：
    # {
    #     "normalized_dates": 8,           # 标准化的日期数量
    #     "cleaned_text_fields": 15,       # 清洗的文本字段数量
    #     "filled_missing_values": 2,      # 填充的缺失值数量
    #     "deduplicated_skills": 3,        # 去重的技能数量
    #     "deduplicated_projects": 1       # 去重的项目数量
    # }
```

**清洗后的数据特点**：

| 特性 | 说明 | 示例 |
|------|------|------|
| **日期统一** | 所有日期为 `YYYY-MM` 格式 | `"2020年1月"` → `"2020-01"` |
| **文本干净** | 无多余空格、特殊字符 | `"  Python  "` → `"Python"` |
| **字段标准** | 字段名、枚举值标准化 | `"编程语言"` → `"language"` |
| **无重复** | 技能、项目已去重 | `["Python", "python"]` → `["Python"]` |
| **技能增强** | 自动分类、验证标志 | `category` 自动填充 |
| **数据完整** | 必需字段有默认值 | 空数组 `[]` 而非 `null` |

---

## 3. 完整数据处理流程

### 3.1 端到端流程图

```
┌─────────────────────────────────────────────────────────────┐
│  1. 文件解析阶段                                            │
├─────────────────────────────────────────────────────────────┤
│  Input: 简历文件 (PDF/Word/TXT)                            │
│  Tool: FileParserTool                                      │
│  Output: 简历纯文本                                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  2. LLM解析阶段                                            │
├─────────────────────────────────────────────────────────────┤
│  Input: 简历文本                                            │
│  Agent: ParsingAgent                                       │
│  Process:                                                  │
│    - System Prompt: 解析专家角色                            │
│    - User Prompt: 简历文本                                 │
│    - LLM Call: 提取结构化信息                              │
│  Output: 原始JSON数据（可能不规范）                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  3. 规则映射阶段                                            │
├─────────────────────────────────────────────────────────────┤
│  Input: LLM解析的JSON数据                                   │
│  Tool: StructureMapperTool                                 │
│  Process:                                                  │
│    - 字段名标准化映射（185个规则）                          │
│    - 数据类型规范化                                         │
│    - 数据验证和修复                                         │
│  Output: ParsedResume 对象                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  4. 数据清洗阶段                                            │
├─────────────────────────────────────────────────────────────┤
│  Input: ParsedResume 对象                                   │
│  Agent: CleaningAgent                                      │
│  Process:                                                  │
│    - 日期标准化 (YYYY-MM)                                  │
│    - 文本清洗 (去空格、去特殊字符)                          │
│    - 缺失值处理                                             │
│    - 数据去重 (技能、项目、工作经历)                        │
│  Output: 清洗后的字典数据                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  5. 数据增强阶段                                            │
├─────────────────────────────────────────────────────────────┤
│  Input: 清洗后的数据                                        │
│  Tool: converter.py (dict_to_cleaned_resume)               │
│  Process:                                                  │
│    - 技能自动分类                                           │
│    - 技能验证标志                                           │
│    - 技能智能提取（如果缺失）                               │
│  Output: CleanedResume 对象                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  6. 评分分析阶段                                            │
├─────────────────────────────────────────────────────────────┤
│  Input: CleanedResume 对象                                 │
│  Agents: TechnicalAnalyzer, ExperienceAnalyzer, ...        │
│  Process:                                                  │
│    - 行业检测                                               │
│    - 技能分类和权重加载                                     │
│    - 评分计算                                               │
│    - LLM深度分析（可选）                                    │
│  Output: AnalysisResult 对象                               │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 数据流转示例

**输入简历**：

```
姓名：张三
电话：138-0013-8000
邮箱：ZHANGSAN@EXAMPLE.COM

教育经历：
- 清华大学 计算机本科 2008年9月 - 2012年6月

工作经历：
- ABC科技公司 软件工程师 2012.07 - 至今
  技术栈：Python、Django、MySQL

项目经验：
- 电商系统 后端开发 2014年 - 2015年
  技术栈：Python Django MySQL Redis

技能：
- Python（熟练）
- Django（熟悉）
- React（了解）
```

**阶段1：文件解析**

```python
resume_text = """
姓名：张三
电话：138-0013-8000
邮箱：ZHANGSAN@EXAMPLE.COM
...
"""
```

**阶段2：LLM解析**

```json
{
  "个人信息": {
    "姓名": "张三",
    "手机": "138-0013-8000",
    "电子邮件": "ZHANGSAN@EXAMPLE.COM"
  },
  "教育背景": [
    {
      "大学": "清华大学",
      "专业": "计算机",
      "学历学位": "本科",
      "入学时间": "2008年9月",
      "毕业时间": "2012年6月"
    }
  ],
  "工作": [
    {
      "公司": "ABC科技公司",
      "职位": "软件工程师",
      "开始日期": "2012.07",
      "结束日期": "至今",
      "技术栈": ["Python", "Django", "MySQL"]
    }
  ],
  "项目": [
    {
      "项目名": "电商系统",
      "职位": "后端开发",
      "项目开始日期": "2014年",
      "项目结束日期": "2015年",
      "技术": "Python Django MySQL Redis"
    }
  ],
  "技能": [
    {"技能名称": "Python", "掌握程度": "熟练"},
    {"技能名称": "Django", "掌握程度": "熟悉"},
    {"技能名称": "React", "掌握程度": "了解"}
  ]
}
```

**阶段3：规则映射**

```json
{
  "personal_info": {
    "name": "张三",
    "phone": "13800138000",      // 去除"-"
    "email": "zhangsan@example.com"  // 转小写
  },
  "education": [
    {
      "school": "清华大学",
      "major": "计算机",
      "degree": "本科",          // 标准化
      "start_time": "2008-09",   // 格式化为YYYY-MM
      "end_time": "2012-06"
    }
  ],
  "work_experience": [
    {
      "company": "ABC科技公司",
      "position": "软件工程师",
      "start_time": "2012-07",
      "end_time": null,          // "至今" → null
      "tech_stack": ["Python", "Django", "MySQL"]  // 字符串转列表
    }
  ],
  "projects": [
    {
      "name": "电商系统",
      "role": "后端开发",
      "start_time": "2014-01",   // 缺少月份默认01
      "end_time": "2015-01",
      "tech_stack": ["Python", "Django", "MySQL", "Redis"]  // 字符串拆分
    }
  ],
  "skills": [
    {"name": "Python", "category": "language", "level": "熟练"},  // 自动分类
    {"name": "Django", "category": "framework", "level": "熟悉"},
    {"name": "React", "category": "framework", "level": "了解"}
  ]
}
```

**阶段4：数据清洗**

```json
{
  "personal_info": {
    "name": "张三",             // 去除两端空格
    "phone": "13800138000",
    "email": "zhangsan@example.com"
  },
  // ... 其他字段类似清洗
  "skills": [
    {"name": "Python", "verified": true},   // 在tech_stack中验证
    {"name": "Django", "verified": true},
    {"name": "React", "verified": false}    // 不在tech_stack中
  ]
}
```

**阶段5：评分分析**

```json
{
  "technical_score": 47.50,
  "industry": "IT/互联网",
  "category_breakdown": {
    "language": {"avg_score": 40.0, "weight": 0.35},
    "framework": {"avg_score": 35.0, "weight": 0.25},
    "database": {"avg_score": 40.0, "weight": 0.20},
    "tool": {"avg_score": 0.0, "weight": 0.15}
  }
}
```

---

## 4. 数据模型定义

### 4.1 完整的字段清单

#### ParsedResume 字段

| 字段 | 类型 | 必需 | 说明 | 示例 |
|------|------|------|------|------|
| `resume_id` | str | 否 | 简历ID（自动生成UUID） | `"a1b2c3d4..."` |
| `file_name` | str | 是 | 文件名 | `"resume.pdf"` |
| `file_type` | str | 是 | 文件类型 | `"pdf"` / `"docx"` |
| `parse_time` | datetime | 否 | 解析时间 | `2026-01-30 10:00:00` |
| `personal_info` | PersonalInfo | 是 | 个人信息 | 见下方 |
| `education` | List[Education] | 是 | 教育经历列表 | 见下方 |
| `work_experience` | List[WorkExperience] | 是 | 工作经历列表 | 见下方 |
| `projects` | List[Project] | 是 | 项目经验列表 | 见下方 |
| `skills` | List[Skill] | 是 | 技能列表 | 见下方 |
| `others` | Dict | 否 | 其他字段 | `{}` |

#### PersonalInfo 字段

| 字段 | 类型 | 必需 | 说明 | 示例 |
|------|------|------|------|------|
| `name` | str | **是** | 姓名 | `"张三"` |
| `phone` | str | 否 | 电话（已标准化） | `"13800138000"` |
| `email` | str | 否 | 邮箱（已转小写） | `"zhangsan@example.com"` |
| `location` | str | 否 | 地址 | `"北京市"` |
| `birth_date` | str | 否 | 出生日期（YYYY-MM） | `"1990-01"` |
| `gender` | str | 否 | 性别 | `"男"` / `"女"` |

#### Education 字段

| 字段 | 类型 | 必需 | 说明 | 示例 |
|------|------|------|------|------|
| `school` | str | 是 | 学校名称 | `"清华大学"` |
| `major` | str | 是 | 专业 | `"计算机科学与技术"` |
| `degree` | str | 是 | 学位（标准化值） | `"本科"` / `"硕士"` / `"博士"` / `"大专"` |
| `start_time` | str | 否 | 开始时间（YYYY-MM） | `"2008-09"` |
| `end_time` | str | 否 | 结束时间（YYYY-MM） | `"2012-06"` |
| `gpa` | str | 否 | GPA | `"3.8"` |
| `description` | str | 否 | 描述 | `"主修课程：数据结构"` |

#### WorkExperience 字段

| 字段 | 类型 | 必需 | 说明 | 示例 |
|------|------|------|------|------|
| `company` | str | 是 | 公司名称 | `"ABC科技公司"` |
| `position` | str | 是 | 职位 | `"软件工程师"` |
| `start_time` | str | 否 | 开始时间（YYYY-MM） | `"2012-07"` |
| `end_time` | str | 否 | 结束时间（YYYY-MM或null） | `"2016-08"` / `null`（至今） |
| `industry` | str | 否 | 行业 | `"互联网"` |
| `company_scale` | str | 否 | 公司规模 | `"1000-9999"` |
| `description` | str | 否 | 工作描述 | `"负责后端开发"` |
| `achievements` | List[str] | 否 | 工作成就列表 | `["完成了XX系统"]` |

#### Project 字段

| 字段 | 类型 | 必需 | 说明 | 示例 |
|------|------|------|------|------|
| `name` | str | 是 | 项目名称 | `"电商系统"` |
| `role` | str | 是 | 角色 | `"后端开发"` |
| `start_time` | str | 否 | 开始时间（YYYY-MM） | `"2014-01"` |
| `end_time` | str | 否 | 结束时间（YYYY-MM） | `"2015-12"` |
| `team_size` | int | 否 | 团队规模 | `10` |
| `tech_stack` | List[str] | 否 | 技术栈列表 | `["Python", "Django"]` |
| `description` | str | 否 | 项目描述 | `"开发电商平台"` |
| `achievements` | List[str] | 否 | 项目成就列表 | `["实现了订单模块"]` |
| `complexity_indicators` | Dict | 否 | 复杂度指标 | `{"has_high_concurrency": true}` |

#### Skill 字段

| 字段 | 类型 | 必需 | 说明 | 示例 |
|------|------|------|------|------|
| `name` | str | **是** | 技能名称 | `"Python"` |
| `category` | str | 是 | 技能类别（标准化值） | `"language"` / `"framework"` / `"database"` / `"tool"` / `"other"` |
| `level` | str | 是 | 技能等级（标准化值） | `"精通"` / `"熟练"` / `"熟悉"` / `"了解"` |
| `verified` | bool | 是 | 是否在项目中验证 | `true` / `false` |

### 4.2 数据验证规则

#### 必需字段验证

```python
# ParsedResume
required_fields = {
    "file_name": str,
    "file_type": str,
    "personal_info": dict,  # 可为空对象，但字段必须存在
    "education": list,      # 可为空数组
    "work_experience": list,
    "projects": list,
    "skills": list
}

# PersonalInfo
required_fields = {
    "name": str  # 姓名是唯一必需字段
}

# Education, WorkExperience, Project, Skill
required_fields = {
    "school": str,         # Education
    "company": str,        # WorkExperience
    "name": str,           # Project, Skill
}
```

#### 数据格式验证

```python
# 日期格式
date_pattern = r"^\d{4}-\d{2}$"  # YYYY-MM

# 电话格式（去除非数字后）
phone_pattern = r"^\d{11,15}$"    # 11-15位数字

# 邮箱格式
email_pattern = r"^[^@]+@[^@]+\.[^@]+$"

# 学位枚举
degree_enum = ["博士", "硕士", "本科", "大专", "高中", "中专"]

# 技能等级枚举
skill_level_enum = ["精通", "熟练", "熟悉", "了解"]

# 技能类别枚举（IT行业）
skill_category_enum = ["language", "framework", "database", "tool", "other"]
```

---

## 附录

### A. 相关文件索引

| 文件 | 说明 | 关键内容 |
|------|------|----------|
| [tools/parsing/file_parser.py](tools/parsing/file_parser.py) | 文件解析工具 | PDF/DOCX转文本 |
| [tools/parsing/structure_mapper.py](tools/parsing/structure_mapper.py) | 结构映射工具 | 185个字段映射规则 |
| [agents/parsing_agent.py](agents/parsing_agent.py) | 解析Agent | LLM解析流程 |
| [agents/cleaning_agent.py](agents/cleaning_agent.py) | 清洗Agent | 数据清洗流程 |
| [tools/cleaning/date_normalizer.py](tools/cleaning/date_normalizer.py) | 日期标准化 | YYYY-MM格式 |
| [tools/cleaning/text_normalizer.py](tools/cleaning/text_normalizer.py) | 文本清洗 | 去空格、特殊字符 |
| [tools/cleaning/missing_value_handler.py](tools/cleaning/missing_value_handler.py) | 缺失值处理 | 填充默认值 |
| [tools/cleaning/data_deduplicator.py](tools/cleaning/data_deduplicator.py) | 数据去重 | 技能、项目去重 |
| [tools/analysis/converter.py](tools/analysis/converter.py) | 数据转换 | 技能分类、验证、提取 |
| [core/models.py](core/models.py) | 数据模型 | 所有数据类定义 |
| [prompts/parsing_prompts.py](prompts/parsing_prompts.py) | 解析Prompt | LLM提示词 |

### B. 配置文件

| 文件 | 说明 |
|------|------|
| [config/scoring.yaml](config/scoring.yaml) | 评分配置 |
| [prompts/base.py](prompts/base.py) | Prompt基类 |

### C. 测试文件

| 文件 | 说明 |
|------|------|
| [test_skill_classification.py](test_skill_classification.py) | 技能分类测试 |

---

**文档结束**
