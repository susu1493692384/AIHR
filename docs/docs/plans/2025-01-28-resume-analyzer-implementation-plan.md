# 简历分析智能体 - 执行计划

## 项目概述

基于LangChain构建的多Agent协作简历分析系统，使用智谱API，前端使用Streamlit。

**核心目标**：
- 支持PDF/Word格式简历上传
- 自动解析、清洗、分析简历内容
- 多维度评分（技术能力25% + 经验背景20% + 项目经验40% + 软技能15%）
- 生成结构化JSON分析报告
- 提供优化建议

---

## 实施计划

### 第一阶段：项目初始化（预计1-2小时）

#### 1.1 创建项目结构
```bash
mkdir -p resume_analyzer/{app,core,agents,tools,prompts,utils,config,tests}
cd resume_analyzer
```

#### 1.2 安装依赖
创建 `requirements.txt`：
```
# 核心框架
langchain>=0.1.0
langchain-core>=0.1.0
langchain-zhipu>=0.1.0
langgraph>=0.0.0

# 文件解析
PyPDF2>=3.0.0
python-docx>=1.0.0

# 前端
streamlit>=1.28.0

# 工具
python-dotenv>=1.0.0
pyyaml>=6.0

# 测试
pytest>=7.4.0
pytest-asyncio>=0.21.0
```

安装依赖：
```bash
pip install -r requirements.txt
```

#### 1.3 配置环境变量
创建 `.env` 文件：
```bash
ZHIPU_API_KEY=your_api_key_here
```

创建 `.env.example`：
```bash
ZHIPU_API_KEY=your_zhipu_api_key
```

---

### 第二阶段：核心模块开发（预计6-8小时）

#### 2.1 数据模型（core/models.py）
**文件**: `core/models.py`

**任务清单**：
- [ ] 定义 `PersonalInfo` 数据类
- [ ] 定义 `Education` 数据类
- [ ] 定义 `WorkExperience` 数据类
- [ ] 定义 `Project` 数据类
- [ ] 定义 `Skill` 数据类
- [ ] 定义 `ParsedResume` 数据类
- [ ] 定义 `CleanedResume` 数据类
- [ ] 定义 `AnalysisResult` 数据类
- [ ] 定义 `ResumeAnalysisReport` 数据类
- [ ] 定义 `ResumeAnalysisState` (TypedDict)

**预计时间**: 1小时

---

#### 2.2 配置管理（core/config.py）
**文件**: `core/config.py`

**任务清单**：
- [ ] 创建 `ScoreConfig` 类
- [ ] 实现权重配置（技术25%、经验20%、项目40%、软技能15%）
- [ ] 实现技能热度配置
- [ ] 实现学校分级配置
- [ ] 添加YAML加载/保存方法

**配置文件**:
- [ ] 创建 `config/scoring.yaml`
- [ ] 创建 `config/skill_demand.yaml`
- [ ] 创建 `config/school_tier.yaml`

**预计时间**: 30分钟

---

### 第三阶段：工具模块开发（预计4-6小时）

#### 3.1 解析工具（tools/parsing/）
**目录**: `tools/parsing/`

**任务清单**：

**file_parser.py**:
- [ ] 实现 `FileParserTool` 类
- [ ] 实现 `_parse_pdf()` 方法
- [ ] 实现 `_parse_docx()` 方法
- [ ] 添加文件类型检测

**text_extractor.py**:
- [ ] 实现 `TextExtractorTool` 类
- [ ] 实现区块识别方法
- [ ] 实现个人信息提取
- [ ] 实现教育经历提取
- [ ] 实现工作经历提取
- [ ] 实现项目经验提取
- [ ] 实现技能提取

**structure_mapper.py**:
- [ ] 实现 `StructureMapperTool` 类
- [ ] 实现数据模型映射方法

**预计时间**: 2.5小时

---

#### 3.2 清洗工具（tools/cleaning/）
**目录**: `tools/cleaning/`

**任务清单**：

**date_normalizer.py**:
- [ ] 实现 `DateNormalizerTool` 类
- [ ] 实现日期格式标准化
- [ ] 实现"至今"关键词处理
- [ ] 添加时长计算方法

**deduplication.py**:
- [ ] 实现 `DeduplicationTool` 类
- [ ] 实现技能去重（相似度匹配）
- [ ] 实现项目去重
- [ ] 实现工作经历去重

**missing_value_handler.py**:
- [ ] 实现 `MissingValueHandlerTool` 类
- [ ] 实现个人信息缺失处理
- [ ] 实现工作经历缺失处理
- [ ] 实现项目经验缺失处理

**text_normalizer.py**:
- [ ] 实现 `TextNormalizationTool` 类
- [ ] 实现全角半角转换
- [ ] 实现标点符号统一
- [ ] 实现空格规范化

**预计时间**: 1.5小时

---

#### 3.3 分析工具（tools/analysis/）
**目录**: `tools/analysis/`

**任务清单**：




**预计时间**: 2小时

---

### 第四阶段：Agent开发（预计3-4小时）

#### 4.1 基础Agent类
**文件**: `agents/base.py`

**任务清单**：
- [ ] 实现 `BaseAgent` 抽象类
- [ ] 实现 `_create_agent()` 方法
- [ ] 定义 `get_system_prompt()` 抽象方法
- [ ] 定义 `run()` 抽象方法

**预计时间**: 30分钟

---

#### 4.2 具体Agent实现
**目录**: `agents/`

**任务清单**：

**parsing_agent.py**:
- [ ] 实现 `ParsingAgent` 类
- [ ] 集成解析工具
- [ ] 实现 `run()` 方法

**cleaning_agent.py**:
- [ ] 实现 `CleaningAgent` 类
- [ ] 集成清洗工具
- [ ] 实现数据清洗流程

**analysis_agent.py**:
- [ ] 实现 `AnalysisAgent` 类
- [ ] 集成4个分析工具
- [ ] 实现并行分析逻辑

**optimization_agent.py**:
- [ ] 实现 `OptimizationAgent` 类
- [ ] 基于分析结果生成建议

**report_agent.py**:
- [ ] 实现 `ReportAgent` 类
- [ ] 聚合所有分析结果
- [ ] 生成结构化报告

**orchestrator.py**:
- [ ] 实现 `OrchestratorAgent` 类
- [ ] 使用LangGraph构建执行图
- [ ] 实现状态管理
- [ ] 实现错误处理和重试

**预计时间**: 2.5小时

---

### 第五阶段：Prompt模板（预计1-2小时）

**目录**: `prompts/`

**任务清单**：

**base.py**:
- [ ] 实现 `BasePrompt` 抽象类
- [ ] 实现 `PromptTemplate` 工具类

**parsing_prompts.py**:
- [ ] 实现解析系统Prompt
- [ ] 实现解析用户Prompt

**cleaning_prompts.py**:
- [ ] 实现清洗系统Prompt
- [ ] 实现清洗用户Prompt

**analysis_prompts.py**:
- [ ] 实现分析系统Prompt
- [ ] 实现技术能力分析Prompt
- [ ] 实现项目经验分析Prompt

**optimization_prompts.py**:
- [ ] 实现优化建议Prompt

**report_prompts.py**:
- [ ] 实现报告生成Prompt
- [ ] 实现HR摘要生成Prompt
- [ ] 实现求职者摘要生成Prompt

**__init__.py**:
- [ ] 实现 `PromptManager` 类

**预计时间**: 1.5小时

---

### 第六阶段：工具函数（预计1小时）

**目录**: `utils/`

**任务清单**：

**file_handler.py**:
- [ ] 实现文件保存方法
- [ ] 实现临时文件清理

**text_utils.py**:
- [ ] 实现文本相似度计算
- [ ] 实现关键词提取

**date_utils.py**:
- [ ] 实现日期解析工具
- [ ] 实现时长计算工具

**validation.py**:
- [ ] 实现数据验证函数
- [ ] 实现分数验证函数

**error_handler.py**:
- [ ] 实现自定义异常类
- [ ] 实现 `ErrorHandler` 类
- [ ] 实现 `DataValidator` 类
- [ ] 实现 `FallbackHandler` 类

**report_exporter.py**:
- [ ] 实现 `to_json()` 方法
- [ ] 实现 `to_dict()` 方法
- [ ] 实现 `to_markdown()` 方法

**预计时间**: 1小时

---

### 第七阶段：前端开发（预计2-3小时）

**文件**: `app/main.py`

**任务清单**：
- [ ] 配置Streamlit页面
- [ ] 实现文件上传组件
- [ ] 添加岗位描述输入（可选）
- [ ] 实现分析按钮
- [ ] 实现结果展示
  - [ ] 总分仪表盘
  - [ ] 各维度进度条
  - [ ] 优化建议展开面板
  - [ ] JSON报告导出
- [ ] 添加加载状态提示
- [ ] 添加错误处理展示

**预计时间**: 2小时

---

### 第八阶段：测试（预计2-3小时）

**目录**: `tests/`

**任务清单**：

**单元测试**:
- [ ] 测试解析工具（`test_parsing_tools.py`）
- [ ] 测试清洗工具（`test_cleaning_tools.py`）
- [ ] 测试分析工具（`test_analysis_tools.py`）

**集成测试**:
- [ ] 测试解析Agent（`test_parsing_agent.py`）
- [ ] 测试分析Agent（`test_analysis_agent.py`）
- [ ] 测试完整流程（`test_end_to_end.py`）

**测试配置**:
- [ ] 创建 `conftest.py`
- [ ] 创建测试fixtures
- [ ] 准备测试样本文件

**预计时间**: 2.5小时

---

### 第九阶段：文档和收尾（预计1小时）

**任务清单**：
- [ ] 编写 `README.md`
- [ ] 创建 `.gitignore`
- [ ] 添加代码注释补充
- [ ] 性能优化
- [ ] 最终测试

**预计时间**: 1小时

---

## 开发顺序建议

### 推荐开发路径

```
1. 项目初始化
   └── 创建目录、安装依赖、配置环境

2. 核心基础
   ├── core/models.py (数据模型)
   ├── core/config.py (配置管理)
   └── utils/error_handler.py (错误处理)

3. 工具层（自底向上）
   ├── tools/parsing/ (解析工具)
   ├── tools/cleaning/ (清洗工具)
   └── tools/analysis/ (分析工具)

4. Agent层
   ├── agents/base.py (基类)
   ├── agents/parsing_agent.py
   ├── agents/cleaning_agent.py
   ├── agents/analysis_agent.py
   ├── agents/optimization_agent.py
   ├── agents/report_agent.py
   └── agents/orchestrator.py (主控)

5. Prompt层
   └── prompts/ (所有Prompt模板)

6. 工具函数
   └── utils/ (辅助函数)

7. 前端
   └── app/main.py (Streamlit应用)

8. 测试
   └── tests/ (单元测试 + 集成测试)

9. 文档
   └── README.md + 其他文档
```

---

## 关键里程碑

| 里程碑 | 完成标志 | 预计时间 |
|--------|----------|----------|
| M1: 项目初始化完成 | 目录结构创建、依赖安装完成 | 1-2小时 |
| M2: 核心模型完成 | 所有数据类定义完成 | 3-4小时 |
| M3: 工具层完成 | 解析、清洗、分析工具全部实现 | 7-10小时 |
| M4: Agent层完成 | 所有Agent实现并通过测试 | 10-14小时 |
| M5: 前端完成 | Streamlit应用可运行 | 12-17小时 |
| M6: 测试完成 | 单元测试和集成测试通过 | 14-20小时 |
| M7: 项目完成 | 文档齐全，可交付 | 15-21小时 |

---

## 开发注意事项

### 技术要点
1. **异步处理**: 所有Agent和Tool使用async/await
2. **错误处理**: 统一使用ErrorHandler处理异常
3. **日志记录**: 使用logging记录关键操作
4. **配置管理**: 敏感信息使用环境变量
5. **代码注释**: 保持注释详细，便于维护

### 测试要点
1. **Mock LLM**: 测试时Mock智谱API调用
2. **测试数据**: 准备多样化的简历样本
3. **边界测试**: 测试空数据、异常格式等边界情况
4. **性能测试**: 测试大文件解析性能

### 优化方向
1. **并发优化**: 4个分析维度并行执行
2. **缓存优化**: LLM响应缓存
3. **流式输出**: Streamlit实时显示分析进度

---

## 依赖项检查清单

- [ ] Python 3.9+
- [ ] 智谱API Key
- [ ] 网络连接（调用API）
- [ ] 测试简历样本文件

---

## 风险与应对

| 风险 | 应对措施 |
|------|----------|
| API调用失败 | 实现重试机制和降级策略 |
| 解析错误率高 | 收集错误样本，优化解析规则 |
| 评分不准确 | 调整评分标准，增加校验 |
| 性能问题 | 优化并发，添加缓存 |
| 测试覆盖不足 | 补充边界测试用例 |

---

## 下一步行动

1. **确认执行计划** - 检查计划是否完整可行
2. **开始实施** - 按照开发顺序开始编码
3. **持续验证** - 每完成一个模块立即测试
4. **调整优化** - 根据测试结果调整设计

---

**文档版本**: v1.0
**创建日期**: 2025-01-28
**状态**: 待实施
