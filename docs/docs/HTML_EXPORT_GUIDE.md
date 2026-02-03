# HTML格式报告导出功能

## 概述

报告生成Agent现在支持将简历分析报告导出为精美的HTML格式，具有现代化的UI设计和响应式布局。

## 功能特性

### 1. 完整的内容展示

HTML报告包含以下所有部分：

- 📊 **执行摘要**: 总分、等级、各维度得分
- ⚙️ **数据处理过程**: 解析、清洗、去重等步骤
- 👤 **清洗后的简历信息**: 基本信息、技能、工作经历、项目、教育背景
- 📈 **详细分析**: 技术能力、经验背景、项目经验、软技能
- 🔍 **关键发现**: 整体关键发现列表
- 💡 **优化建议**: 分类优先级的改进建议
- 🎯 **岗位匹配分析**: 匹配分数、技能覆盖、优劣势分析

### 2. 现代化UI设计

#### 视觉效果

- **渐变背景**: 分数卡片使用紫色渐变背景
- **卡片设计**: 各模块使用卡片式布局，层次分明
- **颜色编码**:
  - 绿色: 优势/精通技能
  - 蓝色: 一般内容/熟练技能
  - 红色: 不足/高优先级
  - 黄色: 建议卡片
  - 灰色: 了解技能

#### 布局特点

- **响应式网格**: 自适应屏幕尺寸
- **最大宽度**: 1200px居中容器
- **圆角边框**: 8px圆角，柔和视觉
- **阴影效果**: 轻微阴影增加层次感

### 3. 响应式设计

- **移动端优化**: 支持各种屏幕尺寸
- **打印友好**: 专门优化的打印样式
- **弹性布局**: Grid和Flexbox混合使用

### 4. 技能标签样式

根据熟练度自动着色：

```html
<span class="skill-tag level-精通">Java</span>  <!-- 绿色 -->
<span class="skill-tag level-熟练">Python</span>  <!-- 蓝色 -->
<span class="skill-tag level-了解">Go</span>      <!-- 灰色 -->
```

## 使用方法

### 基本用法

```python
from agents.report_agent import ReportAgent

# 创建agent
agent = ReportAgent(llm=your_llm, verbose=False)

# 生成报告
result = await agent.run(input_data)
report = result["report"]

# 导出为HTML
html_content = agent.to_html(report)

# 保存到文件
with open("report.html", "w", encoding="utf-8") as f:
    f.write(html_content)
```

### 完整示例

```python
import asyncio
from agents.report_agent import ReportAgent

async def generate_html_report():
    # 准备输入数据
    input_data = {
        "analysis_results": analysis_results,
        "resume_data": resume_data,
        "optimization_suggestions": suggestions,
        "job_requirements": "Java工程师",
        "report_type": "full",
        "processing_info": processing_info
    }

    # 生成报告
    agent = ReportAgent(llm=your_llm)
    result = await agent.run(input_data)
    report = result["report"]

    # 导出HTML
    html = agent.to_html(report)

    # 保存文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"resume_analysis_{timestamp}.html"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"HTML报告已生成: {filename}")

asyncio.run(generate_html_report())
```

## HTML结构

### 文档结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>简历分析报告</title>
    <style>/* CSS样式 */</style>
</head>
<body>
    <div class="container">
        <!-- 报告内容 -->
    </div>
</body>
</html>
```

### 主要CSS类

| 类名 | 用途 | 说明 |
|------|------|------|
| `.container` | 主容器 | 最大宽度1200px，居中显示 |
| `.score-box` | 分数卡片 | 渐变背景，显示总分 |
| `.score-card` | 维度卡片 | 显示各维度得分 |
| `.score-grid` | 分数网格 | 响应式网格布局 |
| `.info-section` | 信息区块 | 浅灰背景，圆角 |
| `.skill-tag` | 技能标签 | 圆角标签，颜色分级 |
| `.strengths-list` | 优势列表 | 绿色背景 |
| `.weaknesses-list` | 不足列表 | 红色背景 |
| `.recommendation-card` | 建议卡片 | 黄色背景，优先级边框 |
| `.stats-grid` | 统计网格 | 数据统计展示 |
| `.stat-box` | 统计卡片 | 居中数值显示 |
| `.match-score` | 匹配分数 | 岗位匹配分数展示 |
| `.tech-stack` | 技术栈 | 项目技术标签 |

## 自定义样式

### 修改颜色主题

可以在生成的HTML中修改CSS变量或直接修改样式：

```css
/* 修改主色调 */
h2 {
    border-left-color: #your-color;
}

.score-card {
    border-left-color: #your-color;
}

.score-card .score-value {
    color: #your-color;
}
```

### 添加公司Logo

在`<div class="container">`开始处添加：

```html
<div class="company-logo">
    <img src="logo.png" alt="Company Logo" style="height: 50px;">
</div>
```

## 浏览器兼容性

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ 移动端浏览器

## 打印功能

HTML报告已优化打印样式，可以直接在浏览器中打印或保存为PDF：

1. 打开HTML文件
2. 按 `Ctrl + P` (或 `Cmd + P`)
3. 选择"保存为PDF"
4. 点击保存

打印时会自动：
- 移除背景色
- 调整边距
- 优化字体

## 文件大小

典型的HTML报告：
- 简单报告: ~50-80 KB
- 完整报告: ~100-150 KB
- 包含大量数据: ~200 KB

## 性能优化

- CSS内联样式，无外部依赖
- 无JavaScript，纯静态HTML
- 快速加载，即开即用
- 支持离线查看

## 测试覆盖

完整的单元测试覆盖：

```bash
pytest tests/test_html_export.py -v
```

测试内容：
- ✅ HTML基本结构
- ✅ 执行摘要展示
- ✅ 清洗后简历信息
- ✅ 详细分析展示
- ✅ 优化建议展示
- ✅ 岗位匹配分析
- ✅ CSS样式正确性
- ✅ 响应式设计
- ✅ 技能标签样式
- ✅ 优劣势样式
- ✅ 元数据展示

## 导出格式对比

| 格式 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **JSON** | 结构化，易于程序处理 | 不便阅读 | API接口、数据存储 |
| **Markdown** | 简洁、易编辑、版本控制友好 | 样式有限 | 文档管理、Git仓库 |
| **HTML** | 美观、交互性强、可打印 | 文件较大 | 展示、分享、存档 |

## 示例输出

HTML报告效果预览：

```
┌─────────────────────────────────────────┐
│      📋 简历分析报告                     │
├─────────────────────────────────────────┤
│                                         │
│  ┌───────────────────────────────────┐ │
│  │     总分: 82.5 分                 │ │
│  │     等级: 良好                    │ │
│  └───────────────────────────────────┘ │
│                                         │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ │
│  │技术  │ │经验  │ │项目  │ │软技 │ │
│  │ 85分 │ │ 80分 │ │ 82分 │ │ 83分 │ │
│  └──────┘ └──────┘ └──────┘ └──────┘ │
│                                         │
│  👤 清洗后的简历信息                    │
│  • 基本信息                            │
│  • 技能清单 (Java 精通, Python 熟练)  │
│  • 工作经历                            │
│  • 项目经验                            │
│  • 教育背景                            │
│                                         │
│  📈 详细分析                            │
│  🎯 岗位匹配分析 (85分 - 较好匹配)    │
│  💡 优化建议                            │
│                                         │
└─────────────────────────────────────────┘
```

## 最佳实践

1. **文件命名**: 使用时间戳命名，便于归档
   ```python
   filename = f"resume_analysis_{timestamp}.html"
   ```

2. **批量处理**: 处理多份报告时创建单独目录
   ```python
   import os
   os.makedirs("reports", exist_ok=True)
   ```

3. **版本控制**: HTML文件建议不提交到Git，使用生成脚本

4. **备份重要**: 重要报告建议同时保存JSON和HTML格式

## 未来增强

可能的功能增强：

- [ ] 添加深色模式切换
- [ ] 支持自定义主题
- [ ] 添加图表可视化
- [ ] 支持导出为Word文档
- [ ] 添加注释和批注功能
- [ ] 多语言支持

## 相关文档

- [Markdown导出指南](MARKDOWN_EXPORT_GUIDE.md)
- [JSON格式说明](JSON_FORMAT_SPEC.md)
- [报告生成API](REPORT_API.md)
