# 前端 V3.2 更新说明 - 技能描述功能

## 更新日期
2026-01-30

## 更新内容

### 新增：技能列表点击展开功能

每个技能现在可以点击展开，查看该技能的详细描述。

---

## 功能说明

### 1. 技能列表交互

**更新前**：
```
🌟 精通技能
• Python
• Go
```

**更新后**：
```
🌟 精通技能
📖 Python（精通） ▼
📖 Go（精通） ▼
```

### 2. 点击展开显示描述

点击技能后，展开显示由LLM生成的技能描述：

```
📖 Python（精通） ▼
Python是一种广泛使用的高级编程语言，具有简洁的语法和强大的功能，适用于Web开发、数据分析、人工智能等多个领域。
```

### 3. 不同熟练度的图标

| 熟练度 | 图标 | 说明 |
|--------|------|------|
| 精通 | 📖 | 绿色书本图标 |
| 熟练 | 📘 | 蓝色书本图标 |
| 熟悉 | 📕 | 橙色书本图标 |
| 了解 | 📙 | 灰色书本图标 |

---

## 实现细节

### 1. LLM生成的技能描述

**函数**: `get_skill_description(skill_name, level)`

**Prompt**:
```
请简单描述以下技能是什么？（1-2句话）

技能名称：{skill_name}
熟练度：{level}

要求：
1. 简洁明了，1-2句话
2. 说明这个技能是什么、用来做什么
3. 不要使用markdown格式
4. 不要包含示例代码

请直接返回描述内容：
```

**示例输出**：
```
Python是一种广泛使用的高级编程语言，具有简洁的语法和强大的功能，适用于Web开发、数据分析、人工智能等多个领域。

Docker是一个开源的容器化平台，可以帮助开发者打包应用及其依赖项，实现跨平台部署和环境一致性。
```

### 2. 缓存机制

使用 `@st.cache_data(ttl=3600)` 缓存技能描述，避免重复调用LLM：

```python
@st.cache_data(ttl=3600)  # 缓存1小时
def get_skill_description(skill_name: str, level: str = "了解") -> str:
    # LLM调用生成描述
    ...
```

**优势**：
- ✅ 同一个技能的描述只生成一次
- ✅ 缓存1小时，避免频繁调用API
- ✅ 提升用户体验，响应速度快

### 3. 错误处理

如果LLM调用失败，返回默认描述：

```python
except Exception:
    return f"{skill_name}是{level}级别的技术能力。"
```

---

## 代码修改

### 文件：app/streamlit_app.py

#### 1. 添加技能描述函数（第48-77行）

```python
@st.cache_data(ttl=3600)  # 缓存1小时
def get_skill_description(skill_name: str, level: str = "了解") -> str:
    """获取技能描述（使用LLM生成）"""
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
        description = description.replace("*", "").replace("#", "").strip()
        return description
    except Exception:
        return f"{skill_name}是{level}级别的技术能力。"
```

#### 2. 修改技能列表显示（第758-783行）

```python
col1, col2 = st.columns(2)

with col1:
    if expert_skills:
        st.markdown("**🌟 精通技能**")
        for skill in expert_skills:
            with st.expander(f"📖 {skill['name']}（精通）", expanded=False):
                description = get_skill_description(skill['name'], "精通")
                st.markdown(f"{description}")

    if senior_skills:
        st.markdown("**✓ 熟练技能**")
        for skill in senior_skills:
            with st.expander(f"📘 {skill['name']}（熟练）", expanded=False):
                description = get_skill_description(skill['name'], "熟练")
                st.markdown(f"{description}")

with col2:
    if familiar_skills:
        st.markdown("**○ 熟悉技能**")
        for skill in familiar_skills:
            with st.expander(f"📕 {skill['name']}（熟悉）", expanded=False):
                description = get_skill_description(skill['name'], "熟悉")
                st.markdown(f"{description}")

    if beginner_skills:
        st.markdown("**◐ 了解技能**")
        for skill in beginner_skills:
            with st.expander(f"📙 {skill['name']}（了解）", expanded=False):
                description = get_skill_description(skill['name'], "了解")
                st.markdown(f"{description}")
```

---

## 使用场景

### 1. HR了解技能

HR可以点击技能，快速了解这个技能是做什么的：

```
📙 Kubernetes（了解）▼
Kubernetes是一个开源的容器编排平台，用于自动化部署、扩展和管理容器化应用程序。
```

### 2. 技术面试官参考

技术面试官可以查看候选人对技能的熟练度，以及AI生成的技能描述：

```
📖 React（精通）▼
React是Facebook开发的一个用于构建用户界面的JavaScript库，采用组件化开发模式，虚拟DOM技术提高了性能，广泛应用于单页应用开发。
```

### 3. 学习者参考

求职者可以查看技能描述，了解自己还需要掌握哪些技能：

```
📘 Redis（熟练）▼
Redis是一个开源的内存数据结构存储系统，可以用作数据库、缓存和消息代理，支持多种数据结构，性能极高。
```

---

## 用户体验提升

### 交互优化

✅ **点击展开**
- 默认收起，保持界面整洁
- 点击感兴趣的技能查看详情

✅ **视觉区分**
- 不同熟练度使用不同颜色的书本图标
- 清晰的视觉层次

✅ **响应迅速**
- 缓存机制，第二次查看无需等待
- LLM快速生成简洁描述

### 信息丰富

✅ **LLM生成描述**
- 动态生成，覆盖所有技能
- 比静态字典更灵活

✅ **上下文感知**
- 根据技能名称和熟练度生成描述
- 针对性强，信息准确

✅ **简洁明了**
- 1-2句话描述
- 突出重点，易于理解

---

## 示例展示

### 完整的技能列表

```
┌─────────────────────────┬─────────────────────────┐
│ 🌟 精通技能            │ ○ 熟悉技能              │
│ 📖 Python（精通） ▼      │ 📕 MySQL（熟悉） ▼     │
│ 📖 Go（精通） ▼         │                         │
│                        │ ◐ 了解技能              │
│ ✓ 熟练技能             │ 📙 Git（了解） ▼         │
│ 📘 Java（熟练） ▼       │ 📙 Docker（了解） ▼      │
│ 📘 Spring（熟练） ▼     │                         │
│ 📘 MySQL（熟练） ▼      │                         │
└─────────────────────────┴─────────────────────────┘
```

### 展开后显示

```
📖 Python（精通）▼
Python是一种广泛使用的高级编程语言，具有简洁的语法和强大的功能库，广泛应用于Web开发、数据分析、人工智能、科学计算等领域。

📘 Java（熟练）▼
Java是一种面向对象的编程语言，具有跨平台、安全、稳定等特点，广泛用于企业级应用开发、Android应用开发、大数据处理等领域。
```

---

## 技术细节

### LLM模型

**模型**: `glm-4-flash`（智谱AI）
**Temperature**: `0.3`（较低温度，输出稳定）
**缓存时间**: `1小时`（避免频繁调用）

### Streamlit组件

**组件**: `st.expander`
- 默认收起（`expanded=False`）
- 点击后展开显示描述
- 再次点击可以收起

### 性能考虑

**首次点击**：
- 调用LLM生成描述
- 响应时间约1-3秒

**后续点击**：
- 从缓存读取
- 响应时间<100ms

---

## 测试

### 启动应用
```bash
streamlit run app/streamlit_app.py
```

### 查看功能
1. 上传简历并分析
2. 切换到"技术能力"标签页
3. 找到技能列表区域
4. 点击任意技能展开
5. 查看LLM生成的技能描述

### 验证缓存
1. 第一次点击某个技能 → 等待LLM生成
2. 收起后再次点击 → 立即显示（从缓存读取）

---

## 后续优化建议

### 1. 技能相关性推荐

可以根据技能推荐相关的其他技能：

```
📖 Python（精通）▼
Python是一种广泛使用的高级编程语言...

💡 相关技能推荐：Django、Flask、FastAPI、NumPy
```

### 2. 技能学习资源

可以添加学习链接或资源推荐：

```
📖 Python（精通）▼
Python是一种广泛使用的高级编程语言...

📚 学习资源：
- 官方文档：https://docs.python.org
- 在线教程：Real Python
- 练习平台：LeetCode
```

### 3. 技能趋势

可以显示技能的市场需求和薪资水平：

```
📖 Python（精通）▼
Python是一种广泛使用的高级编程语言...

📊 市场需求：🔥 极高
💰 平均薪资：20-40K/月
📈 趋势：持续上升
```

---

## 常见问题

### Q1: 为什么有些技能的描述不准确？

**A**: LLM生成的内容可能有误差，可以通过以下方式优化：
- 调整Prompt，增加更多上下文
- 使用更强大的模型（如 `glm-4`）
- 建立技能描述数据库，优先使用静态描述

### Q2: 能否自定义技能描述？

**A**: 可以修改 `get_skill_description` 函数：
```python
# 从数据库读取静态描述
SKILL_DESCRIPTIONS = {
    "Python": "Python是一种...",
    "Java": "Java是一种...",
}

def get_skill_description(skill_name: str, level: str = "了解") -> str:
    if skill_name in SKILL_DESCRIPTIONS:
        return SKILL_DESCRIPTIONS[skill_name]
    # 否则使用LLM生成
    ...
```

### Q3: 缓存时间可以调整吗？

**A**: 可以修改 `@st.cache_data(ttl=3600)` 的参数：
```python
@st.cache_data(ttl=7200)  # 缓存2小时
@st.cache_data(ttl=1800)  # 缓存30分钟
@st.cache_data(ttl=None)   # 永久缓存
```

---

**更新完成时间**: 2026-01-30
**文档版本**: v1.0
**相关文件**:
- [app/streamlit_app.py](../app/streamlit_app.py)
- [前端V3.1更新](FRONTEND_V3.1_UPDATE.md)
