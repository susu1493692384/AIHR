# 项目文件说明

**更新时间**: 2026-01-28
**用途**: 帮助理解项目中每个文件和目录的作用

---

## 📁 根目录文件

### 核心文件

| 文件名 | 大小 | 作用 | 说明 |
|--------|------|------|------|
| **README.md** | 9.7KB | 项目说明文档 | 包含功能特性、安装步骤、使用方法、配置说明 |
| **DEPLOYMENT.md** | 8.5KB | 部署指南 | 完整的部署步骤、常见问题、生产环境配置 |
| **requirements.txt** | 290B | Python依赖列表 | 所有必需的Python包及其版本 |
| **pyproject.toml** | 849B | 项目配置 | pytest配置、包信息、构建配置 |
| **.gitignore** | 91行 | Git忽略规则 | 指定Git不需要跟踪的文件 |
| **.env.example** | 38B | 环境变量示例 | API Key配置模板 |

### 配置文件

| 目录/文件 | 作用 |
|----------|------|
| **config/scoring.yaml** | 评分配置（权重、技能热度、学校分级） |

---

## 📂 目录结构详解

### 🤖 agents/ - Agent模块

**作用**: 实现简历分析的各个Agent（共7个）

| 文件 | 说明 | 关键点 |
|------|------|--------|
| **base.py** | Agent基类 | 使用langchain_core.BaseChatModel |
| **orchestrator.py** | 主控Agent | 协调所有Agent的执行顺序 |
| **parsing_agent.py** | 解析Agent | 解析PDF/DOCX文件 |
| **structure_mapping_agent.py** | 结构映射Agent | 提取结构化信息 |
| **cleaning_agent.py** | 清洗Agent | 数据清洗、标准化 |
| **deduplication_agent.py** | 去重Agent | 数据去重 |
| **analysis_agent.py** | 分析Agent | 四维度并行分析 |
| **optimization_agent.py** | 优化Agent | 生成改进建议 |
| **report_agent.py** | 报告Agent | 生成各类报告 |

**依赖**: langchain_core, prompts

---

### 💬 prompts/ - Prompt模板管理

**作用**: 管理所有LLM的Prompt模板（共14个）

| 文件 | 说明 | Prompt数量 |
|------|------|----------|
| **__init__.py** | PromptManager | 全局单例，管理所有Prompt |
| **base.py** | BasePrompt基类 | Prompt抽象类 |
| **parsing_prompts.py** | 解析相关Prompt | 2个 |
| **cleaning_prompts.py** | 清洗相关Prompt | 2个 |
| **analysis_prompts.py** | 分析相关Prompt | 4个（技术/经验/项目/软技能） |
| **optimization_prompts.py** | 优化相关Prompt | 2个 |
| **report_prompts.py** | 报告相关Prompt | 4个 |

**关键类**: `PromptManager` - 自动注册所有Prompt

---

### 🔧 tools/ - 工具层

**作用**: 实现具体的解析、清洗、分析功能

#### tools/parsing/ - 解析工具
| 文件 | 说明 |
|------|------|
| **file_parser.py** | 文件类型检测、PDF/DOCX解析 |
| **structure_mapper.py** | 文本结构化映射 |

#### tools/cleaning/ - 清洗工具
| 文件 | 说明 |
|------|------|
| **date_normalizer.py** | 日期格式标准化（2020.01 → 2020-01） |
| **text_normalizer.py** | 文本清洗（去空格、特殊字符） |
| **missing_value_handler.py** | 缺失值处理 |

#### tools/analysis/ - 分析工具
| 文件 | 说明 |
|------|------|
| **base_analyzer.py** | 分析器基类 |
| **technical_analyzer.py** | 技术能力分析器 |
| **experience_analyzer.py** | 经验背景分析器 |
| **project_analyzer.py** | 项目经验分析器 |
| **soft_skill_analyzer.py** | 软技能分析器 |

---

### 🧱 core/ - 核心模块

| 文件 | 说明 | 主要类/函数 |
|------|------|-----------|
| **models.py** | 数据模型定义 | PersonalInfo, Education, WorkExperience, Project, Skill, ParsedResume, AnalysisResult等 |
| **config.py** | 配置管理 | ScoreConfig（从YAML加载配置） |

---

### 🛠️ utils/ - 工具函数

| 文件 | 说明 | 主要功能 |
|------|------|----------|
| **error_handler.py** | 错误处理 | 自定义异常类、ErrorHandler统一处理 |
| **validation.py** | 数据验证 | 文件路径、类型、分数验证 |

---

### 🖥️ app/ - 前端应用

| 文件 | 说明 | 技术 |
|------|------|------|
| **streamlit_app.py** | Streamlit前端应用 | 使用OrchestratorAgent，支持文件上传、结果展示、报告导出 |

**功能**:
- API Key配置
- 文件上传（PDF/DOCX）
- 岗位描述输入
- 三Tab页面布局
- JSON/Markdown导出

---

### ⚙️ config/ - 配置文件

| 文件 | 说明 | 内容 |
|------|------|------|
| **scoring.yaml** | 评分配置 | 权重分配、技能热度分级、学校分级 |

---

### 🧪 tests/ - 测试模块

**测试统计**: 109个测试，100%通过

| 类型 | 文件 | 数量 | 覆盖内容 |
|------|------|------|----------|
| **单元测试** | test_*.py | 92个 | 各模块功能测试 |
| **集成测试** | test_integration.py | 7个 | 端到端流程测试 |
| **验证测试** | test_*_verification.py | 6个 | 实现计划验证 |
| **前端测试** | test_frontend.py | 10个 | Streamlit应用测试 |
| **文档** | TEST_REPORT.md | - | 详细测试报告 |

---

### 📚 docs/ - 文档

| 文件 | 说明 |
|------|------|
| **ARCHITECTURE_ANALYSIS.md** | 架构分析文档 |
| **PROMPTMANAGER_USAGE.md** | PromptManager使用指南 |
| **plans/** | 实现计划文档 |

---

### 📝 examples/ - 示例代码

| 文件 | 说明 |
|------|------|
| **simple_demo.py** | 简单演示程序 |
| **workflow_demo.py** | 完整流程演示 |

---

## 🔄 数据流转说明

### 输入 → 输出完整流程

```
用户上传简历 (PDF/DOCX)
    ↓
[app/streamlit_app.py]
    ↓
[agents/orchestrator.py] 调度执行
    ↓
┌─────────────────────────────────────┐
│ 步骤1: 解析          │
│ └─> tools/parsing/file_parser.py    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 步骤2: 结构映射     │
│ └─> tools/parsing/structure_mapper.py│
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 步骤3: 清洗          │
│ └─> tools/cleaning/*.py             │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 步骤4: 四维度分析   │
│ └─> tools/analysis/*.py             │
│   (使用 prompts/analysis_prompts.py) │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 步骤5: 优化建议     │
│ └─> agents/optimization_agent.py    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 步骤6: 生成报告     │
│ └─> agents/report_agent.py          │
└─────────────────────────────────────┘
    ↓
返回结果并展示
```

---

## 🎯 快速定位指南

### 我想修改评分权重

→ 编辑 `config/scoring.yaml`

### 我想修改Prompt

→ 编辑 `prompts/` 下对应的Prompt类

### 我想新增一个Agent

→ 参考 `agents/base.py`，创建新的Agent类

### 我想修改前端UI

→ 编辑 `app/streamlit_app.py`

### 我想添加新的分析维度

→ 1. 在 `prompts/analysis_prompts.py` 添加新Prompt
→ 2. 在 `agents/analysis_agent.py` 添加分析方法
→ 3. 在 `config/scoring.yaml` 添加权重配置

### 测试是否通过

→ 运行 `pytest tests/ -v`

---

## 📦 文件大小参考

| 组件 | 大小（代码行数） |
|------|-----------------|
| agents/ | ~2000行 |
| prompts/ | ~1500行 |
| tools/ | ~1500行 |
| utils/ | ~100行 |
| core/ | ~300行 |
| app/ | ~560行 |
| tests/ | ~5000行 |
| **总计** | **~11000行** |

---

## ✅ 最小运行环境

### 必需文件

```
AI_HR2/
├── agents/              # Agent实现
├── prompts/             # Prompt模板
├── tools/               # 工具函数
├── core/                # 核心模块
├── utils/               # 工具函数
├── app/                 # 前端应用
├── config/scoring.yaml # 配置文件
├── requirements.txt     # 依赖
└── .env                 # 环境变量
```

### 可选文件

```
docs/          # 文档（开发参考）
examples/      # 示例代码
tests/         # 测试（开发时使用）
```

---

## 🔍 文件命名规范

### Agent模块
- `*_agent.py` - Agent实现文件
- `base.py` - 基类文件

### Prompt模块
- `*_prompts.py` - 同类Prompt集合
- `base.py` - 基类文件

### 工具模块
- `*_normalizer.py` - 标准化工具
- `*_analyzer.py` - 分析器工具
- `*_handler.py` - 处理器工具

---

**文档版本**: v1.0
**最后更新**: 2026-01-28
