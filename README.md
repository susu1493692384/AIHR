# AI简历分析系统

基于大语言模型的多Agent协作简历分析系统，支持智能解析、多维度评分和优化建议生成。

## ✨ 功能特性

- 📄 **多格式支持**: 支持 PDF 和 Word (.docx) 格式简历
- 🤖 **智能解析**: 使用LLM自动提取简历结构化信息
- 🧹 **数据清洗**: 自动去重、格式统一、缺失值处理
- 📊 **多维度评分**: 技术、经验、项目、软技能四个维度
- 📈 **科学评分**: 技术25% + 经验20% + 项目40% + 软技能15%
- 💡 **优化建议**: 基于分析结果生成针对性改进建议
- 📋 **多格式报告**: JSON/Markdown/HTML三种格式的完整报告
- 🎯 **岗位匹配**: LLM智能匹配 + 规则引擎兜底
- 👤 **简历展示**: 清洗去重后的完整简历信息展示
- 🎨 **精美HTML**: 现代化UI设计，响应式布局，支持打印
- 🔄 **处理过程透明**: 完整展示数据处理每一步的统计信息

## 🏗️ 系统架构

```
用户上传简历
    ↓
解析Agent → 提取结构化信息
    ↓
清洗Agent → 数据标准化
    ↓
分析Agent → 四维度并行分析
    ├─ 技术能力分析
    ├─ 经验背景分析
    ├─ 项目经验分析
    └─ 软技能分析
    ↓
优化Agent → 生成改进建议
    ↓
报告Agent → 生成结构化报告
    ↓
前端展示 → 用户查看结果
```
---
## 🚀 快速开始

### 方式1: 使用Streamlit前端（推荐）

#### 1. 克隆项目

```bash
git clone https://github.com/susu1493692384/AIHR.git
cd AI_HR
```

#### 2. 创建Python虚拟环境

```bash
# Python 3.9+ 必需
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

**依赖说明**：
- `langchain>=0.1.0` - LangChain核心库
- `langchain-core>=0.1.0` - LangChain核心
- `langchain-zhipu>=0.1.0` - 智谱AI集成
- `PyPDF2>=3.0.0` - PDF解析
- `python-docx>=1.0.0` - Word文档解析
- `streamlit>=1.28.0` - Web前端
- `pyyaml>=6.0` - YAML配置解析

#### 4. 配置API Key

创建 `.env` 文件：

```bash
cp .env.example .env
```

编辑 `.env`，填入智谱AI API Key：

```bash
ZHIPU_API_KEY=your_api_key_here
```

**获取API Key**：访问 [智谱AI开放平台](https://open.bigmodel.cn/) 注册并获取

#### 5. 运行应用

```bash
streamlit run app/streamlit_app.py
```

访问 `http://localhost:8501` 开始使用。

---

### 方式2: API调用

```python
import asyncio
from langchain_zhipu import ChatZhipuAI
from agents import OrchestratorAgent

async def analyze_resume():
    # 初始化LLM
    llm = ChatZhipuAI(
        model="glm-4",
        temperature=0.3,
        api_key="your_api_key"
    )

    # 创建OrchestratorAgent
    orchestrator = OrchestratorAgent(llm, verbose=True)

    # 准备输入数据
    input_data = {
        "file_path": "path/to/resume.pdf",
        "job_requirements": "5年以上Python开发经验",
        "report_types": ["full", "hr_summary"]
    }

    # 执行分析
    result = await orchestrator.run(input_data)

    if result["success"]:
        print(f"总分: {result['state']['total_score']}")
        print(f"技术能力: {result['state']['score_breakdown']['technical']}")
    else:
        print(f"分析失败: {result['error']}")

# 运行
asyncio.run(analyze_resume())
```

---

## ⚙️ 配置说明

### 评分配置 (config/scoring.yaml)

修改各维度权重：

```yaml
weights:
  technical: 0.25   # 技术能力 25%
  experience: 0.20  # 经验背景 20%
  project: 0.40     # 项目经验 40%
  soft_skill: 0.15  # 软技能 15%
```

修改技能热度：

```yaml
skill_demand:
  Python: A         # A类-热门
  Java: B           # B类-主流
  PHP: C            # C类-常规
  Struts: D         # D类-传统
```

修改学校分级：

```yaml
school_tier:
  985:
    - 清华大学
    - 北京大学
    - 复旦大学
  211:
    - 北京理工大学
    - 同济大学
```
## 🔄 详细数据流过程

### Step 1: 简历解析 (ParsingAgent)

**输入数据**:
```python
{
    "file_path": "path/to/resume.pdf",  # PDF或Word文件路径
    "parse_method": "ai"                 # 解析方法：ai/rules
}
```

**处理过程**:
1. 读取文件内容
2. 提取文本信息
3. 调用LLM进行结构化解析
4. 映射到标准数据结构

**输出结果**:
```python
{
    "success": True,
    "parsed_data": {
        "personal_info": {
            "name": "张三",
            "phone": "13800138000",
            "email": "zhangsan@example.com",
            "location": "北京",
            "gender": "男",
            "birth_date": "1990-01-01"
        },
        "skills": [
            {"name": "Java", "level": "精通", "category": "编程语言"},
            {"name": "Python", "level": "熟练", "category": "编程语言"}
        ],
        "work_experience": [
            {
                "company": "科技公司A",
                "position": "后端工程师",
                "start_time": "2020-01",
                "end_time": "至今",
                "description": "负责后端开发"
            }
        ],
        "projects": [
            {
                "name": "电商平台",
                "role": "后端开发",
                "start_time": "2020-03",
                "end_time": "2020-12",
                "tech_stack": ["Java", "Spring Boot", "MySQL"],
                "description": "开发交易系统"
            }
        ],
        "education": [
            {
                "school": "某某大学",
                "degree": "本科",
                "major": "计算机科学与技术",
                "start_time": "2014-09",
                "end_time": "2018-06"
            }
        ]
    },
    "parse_method": "ai",           # 实际使用的解析方法
    "fields_count": 20               # 识别的字段数量
}
```

**数据传递**: `parsed_data` → 清洗Agent

---

### Step 2: 结构映射 (StructureMapper)

**输入数据**: 上一步的 `parsed_data`

**处理过程**:
1. 检查字段完整性
2. 标准化字段名称
3. 统一数据格式
4. 填充默认值

**输出结果**:
```python
{
    "success": True,
    "structured_data": {
        # 标准化后的简历数据，确保所有必需字段存在
        "personal_info": {...},
        "skills": [...],
        "work_experience": [...],
        "projects": [...],
        "education": [...]
    },
    "normalized": True,              # 是否执行了标准化
    "fields_count": 20               # 映射后的字段数量
}
```

**数据传递**: `structured_data` → 清洗Agent

---

### Step 3: 数据清洗 (CleaningAgent)

**输入数据**: 上一步的 `structured_data`

**处理过程**:
1. **日期标准化**: 统一日期格式 (YYYY-MM)
2. **文本清洗**: 去除多余空格、特殊字符
3. **缺失值处理**: 填充默认值或标记为缺失

**输出结果**:
```python
{
    "success": True,
    "cleaned_data": {
        # 清洗后的简历数据
        "personal_info": {...},
        "skills": [...],
        "work_experience": [
            {
                "company": "科技公司A",
                "position": "后端工程师",
                "start_time": "2020-01",     # 已标准化
                "end_time": "2024-01",       # 至今转为当前日期
                "description": "负责后端开发"  # 已去除多余空格
            }
        ],
        "projects": [...],
        "education": [...]
    },
    "cleaning_summary": {
        "fields_count": 20,               # 处理的字段数
        "missing_values_handled": 3       # 处理的缺失值数量
    }
}
```

**数据传递**: `cleaned_data` → 去重Agent

---

### Step 4: 数据去重 (DeduplicationAgent)

**输入数据**: 上一步的 `cleaned_data`

**处理过程**:
1. **技能去重**: 合并相同技能，保留最高熟练度
2. **项目去重**: 删除重复项目（名称+角色相同）
3. **工作经历去重**: 删除重复的工作经历（公司+时间相同）

**输出结果**:
```python
{
    "success": True,
    "deduplicated_data": {
        # 去重后的简历数据
        "personal_info": {...},
        "skills": [
            {"name": "Java", "level": "精通"},     # 保留最高熟练度
            {"name": "Python", "level": "熟练"}
        ],
        "work_experience": [...],    # 已删除重复项
        "projects": [...],           # 已删除重复项
        "education": [...]
    },
    "deduplication_summary": {
        "total_items_processed": 25,  # 总处理项数
        "total_duplicates_removed": 3,# 删除的重复项数
        "items_merged": 2             # 合并的项数
    },
    "deduplication_performed": True,
    "details": {
        "skills": {
            "original_count": 5,
            "removed": 1,
            "merged": 1,
            "final_count": 3
        },
        "projects": {
            "original_count": 3,
            "removed": 1,
            "final_count": 2
        },
        "work_experience": {
            "original_count": 3,
            "removed": 1,
            "final_count": 2
        }
    }
}
```

**数据传递**: `deduplicated_data` → 分析Agent，同时保存到 `processing_info`

---

### Step 5: 四维度分析 (AnalysisAgent)

**输入数据**:
```python
{
    "resume_data": {...},              # 去重后的简历数据
    "analysis_dimensions": [           # 要分析的维度
        "technical",
        "experience",
        "project",
        "soft_skill"
    ]
}
```

**处理过程**: 并行分析四个维度

**输出结果**:
```python
{
    "success": True,
    "analysis_results": {
        "total_score": 82.5,           # 加权总分
        "score_breakdown": {
            "technical": {
                "score": 85,
                "weight": 0.25,
                "contribution": 21.25   # 85 * 0.25
            },
            "experience": {
                "score": 75,
                "weight": 0.20,
                "contribution": 15.0
            },
            "project": {
                "score": 90,
                "weight": 0.40,
                "contribution": 36.0
            },
            "soft_skill": {
                "score": 70,
                "weight": 0.15,
                "contribution": 10.5
            }
        },
        "technical_analysis": {
            "score": 85,
            "level": "良好",
            "关键发现": [
                "技术栈较为完整，涵盖后端主流技术",
                "掌握多种编程语言"
            ],
            "亮点": [
                "Java基础扎实",
                "熟悉Spring生态",
                "有分布式系统经验"
            ],
            "不足之处": [
                "前端技术栈相对薄弱"
            ]
        },
        "experience_analysis": {
            "score": 75,
            "level": "良好",
            "关键发现": [...],
            "亮点": [...],
            "不足之处": [...]
        },
        "project_analysis": {
            "score": 90,
            "level": "优秀",
            "关键发现": [...],
            "亮点": [...],
            "不足之处": [...]
        },
        "soft_skill_analysis": {
            "score": 70,
            "level": "合格",
            "关键发现": [...],
            "亮点": [...],
            "不足之处": [...]
        }
    }
}
```

**数据传递**: `analysis_results` → 优化Agent

---

### Step 6: 优化建议 (OptimizationAgent)

**输入数据**:
```python
{
    "resume_data": {...},              # 简历数据
    "analysis_results": {...}          # 分析结果
}
```

**处理过程**: 基于分析结果生成针对性改进建议

**输出结果**:
```python
{
    "success": True,
    "optimization_suggestions": [
        {
            "category": "技术能力",     # 建议分类
            "suggestion": "建议补充前端技术栈，如Vue或React",
            "priority": "高",           # 优先级：高/中/低
            "current_state": "目前仅掌握后端技术",
            "target_state": "补充前端技术，成为全栈工程师",
            "actionable_steps": [
                "学习Vue.js基础语法",
                "完成一个前后端分离项目",
                "在简历中突出全栈能力"
            ],
            "example": "可以将'精通Java后端开发'改为'精通Java全栈开发，熟悉Vue.js前端框架'",
            "estimated_time": "2-3个月",
            "impact": "提升竞争力20%"
        },
        {
            "category": "项目经验",
            "suggestion": "增加项目量化数据",
            "priority": "中",
            "example": "将'参与电商平台开发'改为'参与电商平台开发，日订单量突破10万，响应时间优化30%'"
        }
    ],
    "priority_summary": {
        "高": 1,    # 高优先级建议数量
        "中": 3,
        "低": 2
    }
}
```

**数据传递**: `optimization_suggestions` → 报告Agent

---

### Step 7: 岗位匹配分析 (ReportAgent - 可选)

**输入数据**:
```python
{
    "resume_data": {...},
    "analysis_results": {...},
    "job_requirements": "Java后端工程师，3年以上经验，熟悉Spring Boot"
}
```

**处理过程**:
1. 尝试使用LLM进行语义匹配
2. 如果LLM失败，使用规则引擎作为fallback

**输出结果**:
```python
{
    "match_score": 85,                 # 匹配分数 0-100
    "match_level": "较好匹配",          # 匹配等级
    "analysis_method": "LLM",          # 使用的分析方法：LLM/Rules
    "job_requirements": "Java后端工程师...",
    "skill_analysis": {
        "matched_skills": ["Java", "Spring Boot", "MySQL"],
        "missing_skills": ["Kubernetes", "消息队列"],
        "additional_skills": ["Python", "Redis"],
        "skill_coverage": 75            # 技能覆盖率 75%
    },
    "experience_analysis": {
        "years_match": True,            # 年限是否匹配
        "project_relevance": 85,       # 项目相关性
        "gap_analysis": ""              # 差距分析
    },
    "education_analysis": {
        "degree_match": True,           # 学历是否匹配
        "major_relevance": 90          # 专业相关性
    },
    "strengths": [
        "技能匹配度高，覆盖75%的岗位要求技能",
        "工作经验丰富且与岗位高度相关"
    ],
    "weaknesses": [
        "缺少Kubernetes等容器编排经验"
    ],
    "recommendations": [
        "建议补充学习以下技能：Kubernetes, 消息队列",
        "建议在简历中突出电商项目经验"
    ],
    "summary": "综合匹配度为85分，属于较好匹配水平；技能匹配度高，具备岗位所需的大部分技能；项目经验与岗位高度相关。"
}
```

**数据传递**: `job_match_analysis` → 报告生成

---

### Step 8: 报告生成 (ReportAgent)

**输入数据**:
```python
{
    "analysis_results": {...},
    "resume_data": {...},
    "optimization_suggestions": [...],
    "job_match_analysis": {...},       # 可选
    "report_type": "full",             # full/hr_summary/candidate_summary
    "processing_info": {...}           # 处理过程信息
}
```

**处理过程**: 根据报告类型生成结构化报告

**输出结果**:
```python
{
    "success": True,
    "report": {
        "executive_summary": {
            "candidate_name": "张三",
            "total_score": 82.5,
            "score_level": "良好",
            "contact": {
                "phone": "13800138000",
                "email": "zhangsan@example.com"
            },
            "quick_overview": {
                "technical": 85,
                "experience": 75,
                "project": 90,
                "soft_skill": 70
            }
        },
        "cleaned_resume": {              # 清洗后的简历信息
            "personal_info": {...},
            "skills": [...],
            "work_experience": [...],
            "projects": [...],
            "education": [...],
            "cleaning_stats": {...},     # 清洗统计
            "deduplication_stats": {...} # 去重统计
        },
        "processing_summary": {          # 数据处理过程
            "steps_completed": [
                "parsed",
                "structured",
                "cleaned",
                "deduplicated"
            ],
            "steps_failed": [],
            "steps_summary": [
                {
                    "step": "parsed",
                    "status": "completed",
                    "fields_count": 20,
                    "parse_method": "ai"
                },
                {
                    "step": "cleaned",
                    "status": "completed",
                    "fields_count": 20,
                    "missing_values_handled": 3
                },
                {
                    "step": "deduplicated",
                    "status": "completed",
                    "deduplication_performed": True,
                    "deduplication_summary": {
                        "total_items_processed": 25,
                        "total_duplicates_removed": 3,
                        "items_merged": 2
                    }
                }
            ]
        },
        "detailed_analysis": {
            "technical": {...},
            "experience": {...},
            "project": {...},
            "soft_skill": {...}
        },
        "key_findings": [
            "[技术能力] 技术栈较为完整",
            "[项目经验] 有完整的电商项目经验"
        ],
        "optimization_suggestions": [...],
        "job_match_analysis": {...},      # 可选
        "metadata": {
            "generated_at": "2026-01-29T12:00:00",
            "job_requirements": "Java后端工程师..."
        }
    },
    "report_type": "full",
    "generated_at": "2026-01-29T12:00:00"
}
```

**数据传递**: `report` → 导出模块

---

### Step 9: 格式导出

**输入数据**: 上一步生成的 `report`

**支持的导出格式**:

#### 1. JSON格式
```python
agent.to_json(report)
# → 完整的JSON字符串，便于程序处理
```

#### 2. Markdown格式
```python
agent.to_markdown(report)
# → Markdown文档，便于阅读和版本控制
```

#### 3. HTML格式
```python
agent.to_html(report)
# → 精美的HTML页面，可直接在浏览器中查看
```

**输出示例**:
- `resume_analysis_20260129_120000.json` - JSON格式
- `resume_analysis_20260129_120000.md` - Markdown格式
- `resume_analysis_20260129_120000.html` - HTML格式

---

## 📊 数据流图

```
┌─────────────────────────────────────────────────────────────┐
│                    用户上传简历 (PDF/Word)                   │
└───────────────────────────┬─────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 1: 解析Agent (parsing_agent.py)                        │
│ ├─ 输入: {file_path: "resume.pdf", parse_method: "ai"}    │
│ ├─ 处理: LLM解析 → 结构映射                                 │
│ └─ 输出: {parsed_data: {...}, fields_count: 20}            │
└───────────────────────────┬─────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: 清洗Agent (cleaning_agent.py)                       │
│ ├─ 输入: parsed_data                                        │
│ ├─ 处理: 日期标准化 + 文本清洗 + 缺失值处理                 │
│ └─ 输出: {cleaned_data: {...}, missing_values_handled: 3}  │
└───────────────────────────┬─────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: 去重Agent (deduplication_agent.py)                   │
│ ├─ 输入: cleaned_data                                       │
│ ├─ 处理: 技能去重 + 项目去重 + 工作经历去重                 │
│ └─ 输出: {deduplicated_data: {...}, duplicates_removed: 3} │
└───────────────────────────┬─────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 4: 分析Agent (analysis_agent.py)                       │
│ ├─ 输入: deduplicated_data                                  │
│ ├─ 处理: 并行分析4个维度                                    │
│ │   ├─ 技术能力分析 (technical_analyzer.py)                │
│ │   ├─ 经验背景分析 (experience_analyzer.py)              │
│ │   ├─ 项目经验分析 (project_analyzer.py)                │
│ │   └─ 软技能分析 (soft_skill_analyzer.py)                │
│ └─ 输出: {analysis_results: {total_score: 82.5, ...}}      │
└───────────────────────────┬─────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 5: 优化Agent (optimization_agent.py)                   │
│ ├─ 输入: analysis_results                                   │
│ ├─ 处理: 基于分析结果生成改进建议                           │
│ └─ 输出: {optimization_suggestions: [...]}                │
└───────────────────────────┬─────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 6: 报告Agent (report_agent.py)                         │
│ ├─ 输入: analysis_results + optimization_suggestions        │
│ ├─ 处理: 生成结构化报告 + 可选岗位匹配分析                  │
│ └─ 输出: {report: {...}}                                    │
└───────────────────────────┬─────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 7: 格式导出                                            │
│ ├─ JSON格式 → 便于API和数据存储                             │
│ ├─ Markdown格式 → 便于文档管理和版本控制                    │
│ └─ HTML格式 → 便于展示和打印                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔑 关键数据结构

### 简历数据结构
```python
{
    "personal_info": {...},    # 个人信息
    "skills": [...],           # 技能列表
    "work_experience": [...],  # 工作经历
    "projects": [...],         # 项目经验
    "education": [...]         # 教育背景
}
```

### 分析结果结构
```python
{
    "total_score": 82.5,       # 总分
    "score_breakdown": {...},  # 分数明细
    "technical_analysis": {...},
    "experience_analysis": {...},
    "project_analysis": {...},
    "soft_skill_analysis": {...}
}
```

### 报告结构
```python
{
    "executive_summary": {...},      # 执行摘要
    "cleaned_resume": {...},         # 清洗后简历
    "processing_summary": {...},     # 处理过程
    "detailed_analysis": {...},      # 详细分析
    "key_findings": [...],           # 关键发现
    "optimization_suggestions": [...], # 优化建议
    "job_match_analysis": {...},     # 岗位匹配(可选)
    "metadata": {...}                # 元数据
}
```

## 📦 项目结构

```
AI_HR2/
├── agents/                    # Agent模块（7个Agent）
│   ├── __init__.py           # Agent导出
│   ├── base.py               # Agent基类（使用langchain_core）
│   ├── orchestrator.py       # 主控Agent（流程编排）
│   ├── parsing_agent.py      # 解析Agent
│   ├── cleaning_agent.py     # 清洗Agent
│   ├── deduplication_agent.py # 去重Agent
│   ├── analysis_agent.py     # 分析Agent（四维度分析）
│   ├── optimization_agent.py  # 优化Agent
│   └── report_agent.py       # 报告Agent
│
├── prompts/                   # Prompt模板管理（14个Prompt）
│   ├── __init__.py           # PromptManager（全局单例）
│   ├── base.py               # BasePrompt基类
│   ├── parsing_prompts.py    # 解析相关Prompt
│   ├── cleaning_prompts.py   # 清洗相关Prompt
│   ├── analysis_prompts.py   # 分析相关Prompt（4个）
│   ├── optimization_prompts.py # 优化相关Prompt
│   └── report_prompts.py     # 报告相关Prompt（4个）
│
├── core/                      # 核心模块
│   ├── __init__.py
│   ├── models.py             # 数据模型（8个模型类）
│   └── config.py             # 配置管理（YAML加载）
│
├── tools/                     # 工具层
│   ├── parsing/              # 解析工具（2个）
│   │   ├── file_parser.py    # 文件解析
│   │   └── structure_mapper.py # 结构映射
│   ├── cleaning/             # 清洗工具（3个）
│   │   ├── date_normalizer.py # 日期标准化
│   │   ├── text_normalizer.py # 文本清洗
│   │   └── missing_value_handler.py # 缺失值处理
│   └── analysis/             # 分析工具（4个）
│       ├── base_analyzer.py  # 分析器基类
│       ├── technical_analyzer.py # 技术分析
│       ├── experience_analyzer.py # 经验分析
│       ├── project_analyzer.py # 项目分析
│       └── soft_skill_analyzer.py # 软技能分析
│
├── utils/                     # 工具函数
│   ├── __init__.py
│   ├── error_handler.py      # 错误处理
│   └── validation.py         # 数据验证
│
├── app/                       # Streamlit前端应用
│   └── streamlit_app.py      # 前端主程序
│
├── config/                    # 配置文件
│   └── scoring.yaml          # 评分配置（权重、技能热度、学校分级）
│
├── tests/                     # 测试模块（109个测试，100%通过）
│   ├── test_*.py             # 单元测试
│   ├── test_integration.py   # 集成测试
│   └── TEST_REPORT.md        # 测试报告
│
├── docs/                      # 文档
│   ├── ARCHITECTURE_ANALYSIS.md  # 架构分析文档
│   ├── PROMPTMANAGER_USAGE.md    # PromptManager使用指南
│   └── plans/                # 实现计划文档
│
├── examples/                  # 示例代码
│   ├── simple_demo.py        # 简单演示
│   └── workflow_demo.py      # 完整流程演示
│
├── pyproject.toml            # 项目配置（pytest等）
├── requirements.txt          # 依赖列表
├── .env.example              # 环境变量示例
└── README.md                 # 本文件
```


---
## 🧪 测试

项目包含 **109个测试**，**通过率100%**。

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_integration.py -v

# 生成覆盖率报告
pytest tests/ --cov=. --cov-report=html

# 查看测试报告
cat tests/TEST_REPORT.md
```

测试覆盖：
- ✅ 单元测试（92个）
- ✅ 集成测试（7个）
- ✅ 前端测试（10个）

## 📊 数据流示例

### 输入：原始简历

```
张三
电话：138-0013-8000
邮箱：zhangsan@example.com

技能：Python, Java, Django

工作经历：
2020.01 - 至今：ABC公司，软件工程师
```

### 输出：分析报告

```json
{
  "total_score": 82.5,
  "score_breakdown": {
    "technical": {"score": 85, "weight": 0.25},
    "experience": {"score": 75, "weight": 0.20},
    "project": {"score": 90, "weight": 0.40},
    "soft_skill": {"score": 70, "weight": 0.15}
  },
  "technical_analysis": {
    "score": 85,
    "insights": ["技术栈全面"],
    "highlights": ["精通Python"],
    "weaknesses": ["前端经验较少"]
  },
  "optimization_suggestions": [
    {
      "category": "技术能力",
      "suggestion": "建议增加前端技术栈",
      "priority": "高"
    }
  ]
}
```

## 🐛 常见问题

### Q: 支持哪些简历格式？

A: 目前支持 PDF (.pdf) 和 Word (.docx) 格式。

### Q: 分析需要多长时间？

A: 通常 30-60 秒，取决于简历长度和 API 响应速度。

### Q: 可以换其他LLM吗？

A: 可以！项目使用 `langchain_core.language_models.BaseChatModel` 抽象，支持任何兼容的LLM：
- 智谱AI: `ChatZhipuAI`
- OpenAI: `ChatOpenAI`
- 通义千问: `ChatTongyi`
- 等等

### Q: 如何自定义Prompt？

A: 修改 `prompts/` 目录下的对应Prompt类，或注册新Prompt：

```python
from prompts import prompt_manager, BasePrompt

class MyPrompt(BasePrompt):
    def get_system_prompt(self) -> str:
        return "你是..."

    def get_user_prompt(self) -> str:
        return "请分析：{data}"

# 注册
prompt_manager.register("my_prompt", MyPrompt())
```
## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 📮 联系方式

如有问题，请提交 Issue。

---

**版本**: v0.2.0
**最后更新**: 2026-01-29
**测试状态**: ✅ 200+个测试全部通过

## 📝 更新日志

### v0.2.0 (2026-01-29)
- ✨ 新增HTML格式报告导出，支持现代化UI设计
- ✨ 新增岗位匹配分析功能（LLM + 规则引擎）
- ✨ 新增清洗后简历信息展示
- ✨ 新增数据处理过程统计信息
- ✨ 新增详细数据流文档
- 🐛 修复测试用例
- 📝 完善文档

### v0.1.0 (2026-01-28)
- 🎉 初始版本发布
- ✨ 支持PDF/Word简历解析
- ✨ 四维度分析能力
- ✨ 优化建议生成
- ✨ JSON/Markdown报告导出
