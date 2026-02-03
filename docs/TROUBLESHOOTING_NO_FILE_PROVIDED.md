# 错误排查：No resume text or file provided

## 错误信息

```
❌ 分析失败: 解析失败: No resume text or file provided
```

## 问题原因

这个错误表明在解析简历时，系统没有收到有效的简历数据。可能的原因有：

### 原因1：文件未正确上传（最常见）

**症状**：
- 点击"开始分析"按钮后立即报错
- 没有看到任何分析步骤的进度

**原因**：
- Streamlit的 `file_uploader` 可能在某些情况下返回 `None` 即使有文件
- 按钮状态与实际文件状态不同步

**检查方法**：
在 Streamlit 应用中添加调试信息：

```python
# 在 streamlit_app.py 的 analyze_button 之前添加
if uploaded_file is not None:
    st.info(f"✅ 文件已上传: {uploaded_file.name} ({uploaded_file.size} 字节)")
else:
    st.warning("⚠️ 请先上传简历文件")
```

### 原因2：临时文件创建失败

**症状**：
- 文件上传成功
- 点击分析后立即报错

**原因**：
临时文件路径无效或权限问题

**代码位置**：`streamlit_app.py:186-188`

```python
temp_path = f"temp_{uploaded_file.name}"
with open(temp_path, "wb") as f:
    f.write(uploaded_file.getbuffer())
```

**检查方法**：
在创建临时文件后添加验证：

```python
temp_path = f"temp_{uploaded_file.name}"
with open(temp_path, "wb") as f:
    f.write(uploaded_file.getbuffer())

# 验证文件创建成功
if not os.path.exists(temp_path):
    st.error(f"❌ 临时文件创建失败: {temp_path}")
    st.stop()
else:
    st.success(f"✅ 临时文件已创建: {temp_path} ({os.path.getsize(temp_path)} 字节)")
```

### 原因3：文件路径传递问题

**症状**：
- 临时文件创建成功
- 但 ParsingAgent 无法读取

**原因**：
相对路径 vs 绝对路径问题

**代码位置**：`streamlit_app.py:209`

```python
input_data = {
    "file_path": temp_path,  # 可能是相对路径
    "text": None,
    ...
}
```

**解决方案**：使用绝对路径

```python
import os
temp_path = os.path.abspath(f"temp_{uploaded_file.name}")
```

### 原因4：ParsingAgent 输入验证失败

**症状**：
- 文件上传成功
- 临时文件创建成功
- 但 ParsingAgent 的 `validate_input()` 返回 False

**代码位置**：`agents/parsing_agent.py:49-53`

```python
if not self.validate_input(input_data):
    return {
        "success": False,
        "error": "Invalid input data"
    }
```

**检查方法**：
查看 ParsingAgent 的验证逻辑

## 解决方案

### 方案1：修复 Streamlit 前端（推荐）

修改 `app/streamlit_app.py` 的文件处理部分：

```python
# 在 upload_and_analyze_section() 函数中
# 找到这段代码（约第180行）

if analyze_button and uploaded_file is not None:
    try:
        import time
        import os
        start_time = time.time()

        # ========== 添加：文件验证 ==========
        st.info(f"📄 文件信息: {uploaded_file.name} ({uploaded_file.size} 字节, {uploaded_file.type})")

        # 保存临时文件（使用绝对路径）
        temp_path = os.path.abspath(f"temp_{uploaded_file.name}")

        # 添加：文件路径显示
        st.caption(f"💾 临时文件路径: {temp_path}")

        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # ========== 添加：验证文件创建成功 ==========
        if not os.path.exists(temp_path):
            st.error(f"❌ 临时文件创建失败: {temp_path}")
            st.stop()

        file_size = os.path.getsize(temp_path)
        if file_size == 0:
            st.error(f"❌ 临时文件为空: {temp_path}")
            os.remove(temp_path)
            st.stop()

        st.success(f"✅ 临时文件已创建: {os.path.basename(temp_path)} ({file_size} 字节)")
        # ========== 验证结束 ==========

        # ... 后续代码保持不变
```

### 方案2：增强 ParsingAgent 的错误信息

修改 `agents/parsing_agent.py` 的 `run()` 方法：

```python
async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """执行简历解析任务"""
    # 添加详细的输入验证
    file_path = input_data.get("file_path")
    resume_text = input_data.get("text") or input_data.get("file_content")

    # 详细的错误信息
    if not resume_text and not file_path:
        return {
            "success": False,
            "error": "No resume text or file provided. Please provide either 'text', 'file_content', or 'file_path' in the input data.",
            "debug_info": {
                "input_keys": list(input_data.keys()),
                "has_text": "text" in input_data,
                "has_file_content": "file_content" in input_data,
                "has_file_path": "file_path" in input_data,
                "file_path_value": file_path
            }
        }

    # 如果提供了文件路径，验证文件存在
    if file_path and not os.path.exists(file_path):
        return {
            "success": False,
            "error": f"File not found: {file_path}",
            "debug_info": {
                "file_path": file_path,
                "current_directory": os.getcwd(),
                "file_exists": os.path.exists(file_path)
            }
        }

    # ... 后续代码
```

### 方案3：添加调试日志

在 `streamlit_app.py` 中添加详细的调试信息：

```python
# 在执行分析之前（第234行之前）
st.markdown("---")
st.markdown("### 🔍 调试信息")

debug_info = {
    "文件名": uploaded_file.name if uploaded_file else "None",
    "文件大小": f"{uploaded_file.size} 字节" if uploaded_file else "N/A",
    "文件类型": uploaded_file.type if uploaded_file else "N/A",
    "临时文件路径": temp_path if 'temp_path' in locals() else "未创建",
    "文件存在": os.path.exists(temp_path) if 'temp_path' in locals() else False,
    "LLM配置": str(type(llm)),
}

for key, value in debug_info.items():
    st.text(f"{key}: {value}")

st.markdown("---")
```

## 快速测试

### 测试1：文件上传测试

在 Streamlit 中运行：

```python
import streamlit as st

uploaded_file = st.file_uploader("上传文件", type=["pdf", "docx"])

if uploaded_file:
    st.write(f"文件名: {uploaded_file.name}")
    st.write(f"文件大小: {uploaded_file.size}")
    st.write(f"文件类型: {uploaded_file.type}")

    # 测试创建临时文件
    import os
    temp_path = os.path.abspath(f"temp_{uploaded_file.name}")
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.write(f"临时文件路径: {temp_path}")
    st.write(f"文件存在: {os.path.exists(temp_path)}")
    st.write(f"文件大小: {os.path.getsize(temp_path)} 字节")
```

### 测试2：ParsingAgent 直接测试

```python
# test_parsing.py
import asyncio
from agents.parsing_agent import ParsingAgent
from langchain_zhipu import ChatZhipuAI

async def test():
    llm = ChatZhipuAI(model="glm-4-flash", temperature=0.3)
    agent = ParsingAgent(llm, verbose=True)

    # 测试1：文件路径
    result = await agent.run({
        "file_path": "test.pdf"  # 确保文件存在
    })
    print("测试1结果:", result)

    # 测试2：文本内容
    result = await agent.run({
        "text": "姓名：张三\n电话：13800138000"
    })
    print("测试2结果:", result)

asyncio.run(test())
```

## 常见问题FAQ

### Q1: 为什么上传文件后还是报错？

**A**: 可能的原因：
1. 文件格式不支持（只支持 PDF 和 DOCX）
2. 文件损坏或为空
3. 文件路径中包含特殊字符
4. 临时目录权限不足

**解决方法**：
- 确认文件格式正确
- 尝试重命名文件（避免中文和特殊字符）
- 检查当前目录的写权限

### Q2: 按钮是灰色的，点击后还是报错？

**A**: 这是 Streamlit 的缓存问题

**解决方法**：
```python
# 在 sidebar 添加一个刷新按钮
if st.button("🔄 重新加载"):
    st.rerun()
```

### Q3: 如何查看详细的错误日志？

**A**: 在 Streamlit 应用中，verbose 模式已经开启。查看：
1. "📋 查看分析步骤" 展开面板中的日志
2. "📝 详细执行日志" 中的输出

## 修复后的完整代码

修改 `app/streamlit_app.py` 的 `upload_and_analyze_section()` 函数：

```python
def upload_and_analyze_section():
    """上传和分析区域"""
    st.header("📤 简历上传与分析")

    # 文件上传
    uploaded_file = st.file_uploader(
        "📄 选择简历文件",
        type=["pdf", "docx"],
        accept_multiple_files=False,
        help="支持 PDF 和 Word (DOCX) 格式"
    )

    # 岗位描述输入（可选）
    st.markdown("---")
    st.markdown("### 💼 岗位描述（可选）")
    job_requirements = st.text_area(
        "输入目标岗位描述",
        placeholder="例如：5年以上Python开发经验，熟悉Django/Flask框架...",
        height=100,
        help="提供目标岗位要求，可以获得更精准的分析结果"
    )

    # 分析按钮
    st.markdown("---")
    col1, col2, col3 = st.columns([3, 2, 2])

    with col2:
        analyze_button = st.button(
            "🚀 开始分析",
            type="primary",
            disabled=uploaded_file is None,
            use_container_width=True
        )

    with col3:
        # 报告类型映射
        report_type_options = {
            "完整报告": "full",
            "HR摘要": "hr_summary",
            "求职者摘要": "candidate_summary"
        }
        selected_report_types = st.multiselect(
            "报告类型",
            list(report_type_options.keys()),
            default=["完整报告", "HR摘要"],
            help="选择要生成的报告类型"
        )
        report_types = [report_type_options[rt] for rt in selected_report_types]

    # 执行分析
    if analyze_button and uploaded_file is not None:
        try:
            import time
            import os
            start_time = time.time()

            # ========== 文件验证和创建 ==========
            st.info(f"📄 文件信息: **{uploaded_file.name}** ({uploaded_file.size} 字节)")

            # 使用绝对路径创建临时文件
            temp_path = os.path.abspath(f"temp_{uploaded_file.name}")

            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # 验证文件创建成功
            if not os.path.exists(temp_path):
                st.error(f"❌ 临时文件创建失败: {temp_path}")
                st.stop()

            file_size = os.path.getsize(temp_path)
            if file_size == 0:
                st.error(f"❌ 临时文件为空: {temp_path}")
                os.remove(temp_path)
                st.stop()

            st.success(f"✅ 文件已就绪: {os.path.basename(temp_path)} ({file_size} 字节)")
            # ========== 验证结束 ==========

            # 获取LLM
            llm = get_llm()

            # 创建进度显示元素
            progress_placeholder = st.empty()
            progress_bar = st.progress(0, "准备开始...")

            # 定义进度回调函数
            def update_progress(current_step: int, total_steps: int, step_name: str):
                """更新进度的回调函数"""
                progress = current_step / total_steps
                progress_bar.progress(progress, f"{step_name} ({current_step}/{total_steps})")
                progress_placeholder.markdown(f"### 🔄 正在执行: {step_name}")

            # 创建OrchestratorAgent
            orchestrator = OrchestratorAgent(llm, verbose=True, progress_callback=update_progress)

            # 准备输入数据
            input_data = {
                "file_path": temp_path,  # 使用绝对路径
                "text": None,
                "job_requirements": job_requirements if job_requirements else "",
                "report_types": report_types or ["full"]
            }

            # 捕获输出
            import sys
            from io import StringIO

            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()

            # 显示步骤说明
            with st.expander("📋 查看分析步骤", expanded=True):
                st.markdown("**即将执行以下7个分析步骤：**")
                st.markdown("**步骤 1/7**: 📄 **解析简历** - 提取PDF/DOCX文本并解析为结构化数据")
                st.markdown("**步骤 2/7**: 🔧 **结构映射** - 将字段名标准化（中文→英文）")
                st.markdown("**步骤 3/7**: 🧹 **数据清洗** - 标准化日期、清理文本、处理缺失值")
                st.markdown("**步骤 4/7**: 🔄 **数据去重** - 去除重复的技能、项目、工作经历")
                st.markdown("**步骤 5/7**: 📊 **多维度分析** - 技术、经验、项目、软技能4个维度并行分析")
                st.markdown("**步骤 6/7**: 💡 **优化建议** - 生成简历改进建议")
                st.markdown("**步骤 7/7**: 📝 **生成报告** - 整合分析结果生成完整报告")

            try:
                # 执行分析
                result = asyncio.run(orchestrator.run(input_data))
            finally:
                elapsed_time = time.time() - start_time
                sys.stdout = old_stdout
                verbose_output = captured_output.getvalue()

                # 更新进度为完成
                progress_bar.progress(1.0, "✅ 分析完成！")
                progress_placeholder.markdown("### ✅ 分析完成！")

            st.markdown("---")
            st.markdown("### 📊 分析结果概览")
            st.markdown(f"⏱️ **总耗时**: {elapsed_time:.1f} 秒")

            st.markdown("---")
            st.markdown("### 📝 详细执行日志")

            # 显示执行日志
            for line in verbose_output.split('\n'):
                if not line.strip():
                    continue
                # ... 日志显示逻辑保持不变

            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)

            if result.get("success"):
                # 显示成功消息
                st.success("✅ 分析完成！")
                st.info("📌 请切换到「分析结果」标签页查看详细报告")

                # 保存结果到session state
                st.session_state.analysis_result = result
                st.session_state.uploaded_file_name = uploaded_file.name

                # 刷新按钮
                if st.button("🔄 刷新查看分析结果", type="secondary"):
                    st.rerun()
            else:
                error = result.get("error", "未知错误")

                # 检查错误类型
                if "余额" in str(error) or "1113" in str(error):
                    st.error("❌ API Key余额不足或无可用资源包")
                    st.info("💡 请访问智谱AI开放平台充值：https://open.bigmodel.cn/")
                elif "429" in str(error):
                    st.error("❌ API请求频率过高（429错误）")
                    st.info("💡 请稍等片刻后重试")
                else:
                    st.error(f"❌ 分析失败: {error}")
                    # 显示调试信息
                    with st.expander("🔍 调试信息"):
                        st.json({
                            "file_name": uploaded_file.name,
                            "file_size": uploaded_file.size,
                            "temp_path": temp_path,
                            "temp_exists": os.path.exists(temp_path),
                            "input_keys": list(input_data.keys())
                        })

        except Exception as e:
            # 清理临时文件
            if 'temp_path' in locals() and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass

            # 显示详细错误
            st.error(f"❌ 发生异常: {str(e)}")
            st.exception(e)
```

## 总结

这个错误的根本原因是**文件上传或临时文件创建失败**。按照上述方案修复后，系统会：

1. ✅ 验证文件上传成功
2. ✅ 验证临时文件创建成功
3. ✅ 使用绝对路径避免路径问题
4. ✅ 显示详细的调试信息
5. ✅ 提供清晰的错误提示

如果问题仍然存在，请检查：
- 文件格式是否为 PDF 或 DOCX
- 文件大小是否为 0
- 当前目录是否有写权限
- LLM API Key 是否配置正确
