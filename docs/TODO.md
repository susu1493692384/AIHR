# 待办事项与开发计划

## 📅 文档信息
- **创建日期**: 2026-02-03
- **版本**: v1.0
- **状态**: 待开发
- **优先级**: 中

---

## ✅ 已完成的修改

### 1. HTML报告导出优化
**日期**: 2026-02-03
**修改文件**: `agents/report_agent.py`

#### 修改内容：
1. **移除数据处理过程展示**
   - 删除了"⚙️ 数据处理过程"章节
   - 移除了步骤执行情况、解析方法、字段数等内部信息
   - 原因：HR和求职者不需要看到这些技术细节

2. **移除数据清洗统计展示**
   - 删除了"数据清洗统计"章节
   - 移除了处理字段数、缺失值处理、去重统计等信息
   - 原因：清洗过程是后台操作，不需要在报告中展示

3. **修复项目Q&A显示问题**
   - 修复了 `_format_dimension_analysis()` 方法的数据路径
   - 确保面试问题（interview_questions）正确显示在HTML报告中
   - 修改位置：`agents/report_agent.py:328`
   ```python
   # 修复前
   "raw_analysis": dimension_data
   # 修复后
   "raw_analysis": dimension_data.get("raw_analysis", dimension_data)
   ```

#### 当前HTML报告结构：
```
┌─────────────────────────────────────────┐
│  📋 简历分析报告                          │
├─────────────────────────────────────────┤
│  1. 📊 执行摘要                          │
│     - 总分、等级、各维度得分              │
│                                         │
│  2. 👤 清洗后的简历信息                  │
│     - 基本信息、技能、工作经历           │
│     - 项目、教育背景                     │
│                                         │
│  3. 📈 详细分析                          │
│     - 技术能力分析（含技能标签）         │
│     - 经验背景分析                       │
│     - 项目经验分析（含Q&A面试问题） ✅  │
│     - 软技能分析                         │
│                                         │
│  4. 🔍 关键发现                          │
│                                         │
│  5. 💡 优化建议                          │
│                                         │
│  6. 🎯 岗位匹配分析（如提供）             │
│                                         │
│  7. 📊 元数据                            │
│     - 生成时间、岗位要求                 │
└─────────────────────────────────────────┘
```

---

## 🚧 待开发功能

### 高优先级

#### 1. 证书与资质识别功能
**状态**: 数据结构已预留，功能未实现
**工作量**: 2-3天

##### 需求描述：
支持识别简历中的证书、资质认证、比赛获奖等信息，并在报告中展示和评分。

##### 技术方案：

**1.1 修改解析Prompt**
- 文件：`prompts/parsing_prompts.py`
- 在系统提示词中添加证书提取要求
- 在JSON示例中添加certificates字段

```python
# 修改 parsing_prompts.py
def get_system_prompt(self) -> str:
    return """你是一位专业的简历解析专家...

你的任务是从简历文本中识别并提取以下关键信息：
1. 个人信息（姓名、电话、邮箱、地址等）
2. 教育经历（学校、专业、学位、时间等）
3. 工作经历（公司、职位、时间、描述等）
4. 项目经验（项目名称、角色、时间、技术栈等）
5. 技能清单（技能名称、熟练度）
6. 证书资质（证书名称、颁发机构、获得时间、级别）← 新增
```

**1.2 添加证书数据模型**
- 文件：`core/models.py`
- 在 ParsedResume 中添加 certificates 字段

```python
@dataclass
class Certificate:
    """证书数据模型"""
    name: str  # 证书名称
    issuer: str = ""  # 颁发机构
    date: str = ""  # 获得时间 (YYYY-MM)
    level: str = ""  # 级别（初级/中级/高级/专业级）
    certificate_type: str = "other"  # 类型（certification/award/other）

@dataclass
class ParsedResume:
    """解析后的简历数据模型"""
    # ... 其他字段
    certificates: List[Certificate] = None  # 新增

    def __post_init__(self):
        if self.certificates is None:
            self.certificates = []
```

**1.3 创建证书分析器**
- 文件：`tools/analysis/certificate_analyzer.py`（新建）

```python
class CertificateAnalyzer(BaseAnalyzer):
    """证书分析器"""

    dimension_name = "certificate"
    weight = 0.0  # 初始权重为0，不参与总分计算

    def analyze(self, resume: CleanedResume) -> AnalysisResult:
        certificates = resume.cleaned_data.certificates

        if not certificates:
            return AnalysisResult(
                dimension=self.dimension_name,
                score=0,
                detail_scores={"证书数量": 0},
                insights=["简历中未发现证书信息"],
                highlights=[],
                weaknesses=[],
                raw_analysis={"certificates": []}
            )

        # 评分规则
        score = 0
        highlights = []

        for cert in certificates:
            # 国际认证（10分）
            if any(keyword in cert.name.lower() for keyword in
                   ['aws', 'microsoft', 'google', 'oracle', 'cisco']):
                score += 10
                highlights.append(f"获得国际认证：{cert.name}")

            # 国内认证（5分）
            elif any(keyword in cert.name.lower() for keyword in
                     ['软考', 'PMP', 'ACP', 'CEAC']):
                score += 5
                highlights.append(f"获得国内认证：{cert.name}")

            # 比赛获奖（15分）
            if cert.certificate_type == 'award':
                score += 15
                highlights.append(f"比赛获奖：{cert.name}")

        # 封顶100分
        score = min(score, 100)

        return AnalysisResult(
            dimension=self.dimension_name,
            score=score,
            detail_scores={
                "证书数量": len(certificates),
                "国际认证": len([c for c in certificates if 'aws' in c.name.lower()]),
                "比赛获奖": len([c for c in certificates if c.certificate_type == 'award'])
            },
            insights=[f"共获得{len(certificates)}项证书资质"],
            highlights=highlights,
            weaknesses=["建议考取更多行业相关证书"] if len(certificates) < 2 else [],
            raw_analysis={"certificates": [cert.__dict__ for cert in certificates]}
        )
```

**1.4 更新字段映射**
- 文件：`tools/parsing/structure_mapper.py`
- 确保 certificates 字段被正确映射和验证

```python
# 在 _validate_and_fix 中添加
array_fields = ["education", "work_experience", "projects", "skills", "certificates"]
```

**1.5 在前端展示**
- 文件：`app/streamlit_app.py`
- 在简历信息展示区域添加证书Tab

```python
# 在简历详情tabs中添加
with st.tabs(["基本信息", "技能", "工作经历", "项目", "教育", "证书"]):
    # ... 其他tab

    with tab_certificates:  # 新增证书tab
        certificates = resume_data.get("certificates", [])
        if certificates:
            for cert in certificates:
                with st.expander(f"🏆 {cert.get('name', '未知证书')}", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**颁发机构**: {cert.get('issuer', '未知')}")
                    with col2:
                        st.write(f"**获得时间**: {cert.get('date', '未知')}")
                    with col3:
                        st.write(f"**级别**: {cert.get('level', '未知')}")
        else:
            st.info("暂无证书信息")
```

**1.6 在HTML报告中展示**
- 文件：`agents/report_agent.py`
- 在 `to_html()` 方法中添加证书展示部分

```python
# 在清洗后的简历信息部分添加
certificates = cleaned_resume.get("certificates", [])
if certificates:
    html_parts.append("<h3>证书资质</h3>")
    for cert in certificates:
        html_parts.append('<div class="info-section">')
        html_parts.append(f'<p><strong>证书名称:</strong> {cert.get("name", "")}</p>')
        html_parts.append(f'<p><strong>颁发机构:</strong> {cert.get("issuer", "")}</p>')
        html_parts.append(f'<p><strong>获得时间:</strong> {cert.get("date", "")}</p>')
        html_parts.append('</div>')
```

##### 测试要点：
1. 测试LLM能否正确提取证书信息
2. 测试各种证书名称的识别（中英文）
3. 测试前端展示和HTML导出
4. 测试评分计算逻辑

---

#### 2. 性能优化：并行生成面试问题
**状态**: 待实现
**工作量**: 1-2天
**预期收益**: 减少20-30秒执行时间

##### 问题分析：
当前系统为每个项目串行调用LLM生成面试问题，如果有5个项目，需要调用5次LLM，耗时约25-40秒。

##### 解决方案：

**2.1 并行调用LLM**
- 文件：`tools/analysis/project_analyzer_simple.py`

```python
import asyncio

async def _generate_all_interview_questions(self, projects: List) -> List:
    """并行生成所有项目的面试问题"""

    async def generate_single(proj):
        return generate_interview_questions(
            project_name=proj.name,
            project_role=proj.role,
            tech_stack=proj.tech_stack or [],
            project_description=proj.description or ""
        )

    # 创建所有任务
    tasks = [generate_single(proj) for proj in projects]

    # 并行执行
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 处理结果
    interview_questions_list = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"[警告] 项目{i}面试问题生成失败: {result}")
            interview_questions_list.append([])
        else:
            interview_questions_list.append(result)

    return interview_questions_list

# 在 analyze 方法中调用
interview_questions_list = await self._generate_all_interview_questions(projects)
```

**2.2 批量生成面试问题**（备选方案）
- 一次LLM调用生成所有项目的面试问题

```python
def generate_batch_interview_questions(projects: List) -> Dict:
    """批量生成面试问题"""

    projects_info = []
    for proj in projects[:5]:  # 限制5个项目
        projects_info.append({
            "name": proj.name,
            "role": proj.role,
            "tech_stack": ', '.join(proj.tech_stack[:5]),
            "description": proj.description[:200]
        })

    user_prompt = f"""请为以下{len(projects_info)}个项目各生成3个面试问题：

{json.dumps(projects_info, ensure_ascii=False, indent=2)}

请以JSON格式返回，格式示例：
{{
    "项目A": [
        {{"question": "...", "answer": "..."}},
        ...
    ],
    ...
}}
"""
```

##### 测试要点：
1. 测试并发调用的性能提升
2. 测试异常处理（某个项目失败不影响其他）
3. 测试API限流情况

---

### 中优先级

#### 3. 进度回调延迟优化
**状态**: 待实现
**工作量**: 0.5天

##### 问题描述：
每次进度更新后有0.3秒延迟，7个步骤共2.1秒。

##### 解决方案：
```python
# orchestrator.py:57
# 修改前
asyncio.sleep(0.3)

# 修改后
asyncio.sleep(0.1)  # 减少到0.1秒
```

---

#### 4. 优化建议的规则工具增强
**状态**: 待实现
**工作量**: 1天

##### 问题描述：
LLM生成优化建议失败时，回退的规则工具建议较为简单。

##### 解决方案：
增强 `tools/optimization/suggestion_generator.py`，添加：
- 基于行业关键词的建议
- 基于数据对比的建议
- 基于最佳实践的模板建议

---

### 低优先级

#### 5. 多语言支持
**状态**: 待实现
**工作量**: 3-5天

##### 功能描述：
支持英文简历的解析和分析。

##### 实现要点：
1. 修改解析Prompt支持英文
2. 添加多语言评分关键词
3. 前端国际化

---

#### 6. 历史记录管理
**状态**: 待实现
**工作量**: 2-3天

##### 功能描述：
保存历史分析记录，支持查询、对比、删除。

##### 实现要点：
1. 设计数据库表结构
2. 添加历史记录API
3. 前端展示历史列表

---

## 📋 技术架构说明

### 数据流程图

```
┌─────────────┐
│ 简历文件    │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────────┐
│ ParsingAgent (解析)              │
│ - 文件读取                       │
│ - 文本提取                       │
│ - LLM结构化解析                  │ ← LLM调用 #1
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ StructureMappingAgent (映射)     │
│ - 字段标准化                     │
│ - 日期格式化                     │
│ - 枚举值映射                     │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ CleaningAgent (清洗)             │
│ - 缺失值处理                     │
│ - 文本标准化                     │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ DeduplicationAgent (去重)        │
│ - 技能去重                       │
│ - 项目去重                       │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ AnalysisAgent (分析)             │
│ ├─ TechnicalAnalyzer (规则)      │
│ ├─ ExperienceAnalyzer (规则)     │
│ ├─ ProjectAnalyzer (规则)        │
│ │  └─ 面试问题生成                │ ← LLM调用 #N (每个项目1次)
│ └─ SoftSkillAnalyzer (规则)      │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ OptimizationAgent (优化建议)      │
│ - LLM生成建议                    │ ← LLM调用 #1
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ ReportAgent (报告)               │
│ ├─ 岗位匹配分析                   │ ← LLM调用 #1 (可选)
│ └─ HTML导出                      │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ 最终报告                          │
│ - JSON格式                       │
│ - HTML格式                       │
│ - Markdown格式                   │
└──────────────────────────────────┘
```

### 性能分析

**当前耗时分布**（80+秒）：

| 步骤 | 耗时 | LLM调用 | 说明 |
|------|------|---------|------|
| 解析简历 | 5-10秒 | 1次 | 提取结构化数据 |
| 项目面试问题生成 | 15-40秒 | N次 | 每个项目1次（主要瓶颈）|
| 优化建议 | 5-10秒 | 1次 | 生成改进建议 |
| 岗位匹配 | 5-10秒 | 1次（可选）| 匹配度分析 |
| 规则处理 | 1-2秒 | 0次 | 结构映射、清洗、去重 |
| 进度延迟 | 2.1秒 | 0次 | UI更新延迟 |
| **总计** | **33-73秒** | **4+N次** | 加上网络延迟可达80+秒 |

### 评分权重配置

**当前权重**（配置文件：`config/scoring.yaml`）：

```yaml
weights:
  technical: 0.25      # 技术能力 25%
  experience: 0.20      # 经验背景 20%
  project: 0.40         # 项目经验 40%（最重）
  soft_skill: 0.15      # 软技能 15%
  certificate: 0.0      # 证书资质 0%（待添加）
```

**总分计算公式**：
```
总分 = 技术分×0.25 + 经验分×0.20 + 项目分×0.40 + 软技能分×0.15
```

---

## 🔧 开发指南

### 添加新的评分维度

1. **创建分析器**
   - 继承 `BaseAnalyzer`
   - 实现 `analyze()` 方法
   - 返回 `AnalysisResult`

2. **注册到系统**
   - 在 `config/scoring.yaml` 中添加权重
   - 在 `AnalysisAgent` 中注册

3. **更新UI**
   - 在 `streamlit_app.py` 中添加展示
   - 在 `report_agent.py` 中添加导出逻辑

### 修改LLM Prompt

1. **位置**：`prompts/*.py`
2. **流程**：
   - 修改 Prompt 类
   - 在 `__init__.py` 中注册
   - 测试输出格式
   - 更新文档

### 调试技巧

**开启详细日志**：
```python
# 初始化agent时设置verbose=True
agent = ParsingAgent(llm, verbose=True)
```

**查看中间结果**：
```python
# 获取中间结果
state = orchestrator.get_state()
parsed = state.get("intermediate_results", {}).get("parsed", {})
```

---

## 📝 注意事项

### LLM调用失败处理
系统在LLM调用失败时会自动回退到规则工具，确保核心功能可用：
- 岗位匹配 → LLMJobMatcher（规则工具）
- 优化建议 → SuggestionGenerator（规则工具）
- 面试问题 → 跳过（不影响主流程）

### API Key配置
需要在 `.env` 文件中配置：
```bash
ZHIPU_API_KEY=your_api_key_here
ZHIPU_MODEL=glm-4-flash
```

### 数据验证
所有Agent都有输入验证，失败时返回错误信息：
```python
{
    "success": False,
    "error": "错误描述"
}
```

---

## 📌 近期计划

### 第一阶段（本周）
- [ ] 完成证书识别功能开发
- [ ] 测试证书提取和展示
- [ ] 更新用户文档

### 第二阶段（下周）
- [ ] 性能优化：并行生成面试问题
- [ ] 进度回调延迟优化
- [ ] 性能测试和对比

### 第三阶段（后续）
- [ ] 增强优化建议规则工具
- [ ] 添加更多分析维度
- [ ] 历史记录管理功能

---

## 📧 联系方式

如有疑问或建议，请通过以下方式联系：
- 创建Issue
- 提交Pull Request
- 查看项目文档

---

**文档维护**: 请在修改功能后及时更新此文档
