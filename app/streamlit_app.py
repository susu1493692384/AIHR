# app/streamlit_app.py
"""简历分析系统 - Streamlit前端应用"""
import streamlit as st
import os
import sys
import asyncio
from datetime import datetime
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 自动加载环境变量（优先于os.getenv）
from dotenv import load_dotenv
load_dotenv()  # 自动查找并加载 .env 文件

# 导入Agent
from agents import OrchestratorAgent
from agents.report_agent import ReportAgent

# 导入LLM辅助函数
from utils.llm_helpers import get_llm, get_skill_description as _get_skill_description
from utils.llm_helpers import get_school_description as _get_school_description
from utils.llm_helpers import get_company_description as _get_company_description


@st.cache_data(ttl=3600)
def get_skill_description(skill_name: str, level: str = "了解") -> str:
    """获取技能描述（使用Streamlit缓存）"""
    return _get_skill_description(skill_name, level)


@st.cache_data(ttl=86400)
def get_school_description(school_name: str) -> str:
    """获取学校描述（使用Streamlit缓存）"""
    return _get_school_description(school_name)


@st.cache_data(ttl=86400)
def get_company_description(company_name: str) -> str:
    """获取公司描述（使用Streamlit缓存）"""
    return _get_company_description(company_name)


def main():
    """主应用"""
    # 页面配置
    st.set_page_config(
        page_title="AI简历分析系统",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 标题
    st.title("📄 AI简历分析系统")
    st.markdown("> 基于大语言模型的智能简历分析系统")

    # 侧边栏 - 配置区域
    with st.sidebar:
        st.header("⚙️ 系统配置")

        # API Key配置
        st.markdown("---")
        st.markdown("### 🔑 API配置")
        api_key_input = st.text_input(
            "智谱AI API Key",
            type="password",
            help="输入智谱AI的API Key",
            key="api_key_input"
        )

        if api_key_input:
            os.environ["ZHIPU_API_KEY"] = api_key_input
            st.success("✅ API Key已更新")
            # 清除缓存（Streamlit 1.28+）
            st.cache_resource.clear()

        # 评分权重展示
        st.markdown("---")
        st.markdown("### 📊 评分权重")
        from core.config import ScoreConfig
        config = ScoreConfig.from_yaml("config/scoring.yaml")
        st.write(f"- **技术能力**: {config.weights['technical'] *100:.0f}%")
        st.write(f"- **经验背景**: {config.weights['experience'] *100:.0f}%")
        st.write(f"- **项目经验**: {config.weights['project'] *100:.0f}%")
        st.write(f"- **软技能**: {config.weights['soft_skill'] *100:.0f}%")

        # 使用说明
        st.markdown("---")
        st.markdown("### 📖 使用说明")
        with st.expander("查看详细说明"):
            st.markdown("""
            **步骤：**
            1. 上传PDF或DOCX格式的简历文件
            2. （可选）输入目标岗位描述
            3. 点击"开始分析"按钮
            4. 等待分析完成
            5. 查看分析报告

            **输出：**
            - 综合评分（0-100分）
            - 四个维度的详细分析
            - 优化改进建议
            - JSON格式报告
            """)

    # 主区域 - Tab页面
    tab1, tab2, tab3 = st.tabs([
        "📤 上传分析",
        "📊 分析结果",
        "📥 导出报告"
    ])

    # Tab 1: 上传和分析
    with tab1:
        upload_and_analyze_section()

    # Tab 2: 分析结果
    with tab2:
        display_results_section()

    # Tab 3: 导出报告
    with tab3:
        export_report_section()


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

    with col1:
        pass

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
            default=["完整报告"],
            help="选择要生成的报告类型"
        )
        # 映射回英文值
        report_types = [report_type_options[rt] for rt in selected_report_types]

    # 执行分析
    if analyze_button and uploaded_file is not None:
        try:
            import time
            start_time = time.time()

            # 保存临时文件
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

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

            # 创建OrchestratorAgent并传入进度回调
            orchestrator = OrchestratorAgent(llm, verbose=True, progress_callback=update_progress)

            # 准备输入数据
            input_data = {
                "file_path": temp_path,
                "text": None,
                "job_requirements": job_requirements if job_requirements else "",
                "report_types": report_types or ["full"]
            }

            # 捕获输出
            import sys
            from io import StringIO

            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()

            # 显示初始信息
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
                # 保留最后的步骤信息，不清空
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

                    # 显示日志内容
                    if any(tag in line for tag in ['[FILE]', '[TOOL]', '[CLEAN]', '[ROTATE]', '[CHART]', '[LIGHT]', '[NOTE]']):
                        if '[FILE]' in line:
                            st.info(f"📄 **{line.strip()}**")
                        elif '[TOOL]' in line:
                            st.info(f"🔧 **{line.strip()}**")
                        elif '[CLEAN]' in line:
                            st.info(f"🧹 **{line.strip()}**")
                        elif '[ROTATE]' in line:
                            st.info(f"🔄 **{line.strip()}**")
                        elif '[CHART]' in line:
                            st.info(f"📈 **{line.strip()}**")
                        elif '[LIGHT]' in line:
                            st.info(f"💡 **{line.strip()}**")
                        elif '[NOTE]' in line:
                            st.info(f"📝 **{line.strip()}**")
                    elif '[OK]' in line:
                        st.success(f"  ✅ {line.strip()}")
                    elif '[WARNING]' in line:
                        st.warning(f"  ⚠️ {line.strip()}")
                    elif '[X]' in line:
                        st.error(f"  ❌ {line.strip()}")
                    else:
                        # 缩进显示详细信息
                        if line.strip().startswith('  '):
                            st.caption(f"    {line.strip()}")
                        elif line.strip().startswith(' 输入:') or line.strip().startswith(' 处理:') or line.strip().startswith(' 输出:'):
                            if '输入:' in line:
                                st.markdown(f"  🔹 **{line.strip()}**")
                            elif '处理:' in line:
                                st.markdown(f"  ⚙️ {line.strip()}")
                            elif '输出:' in line:
                                st.markdown(f"  ➡️ **{line.strip()}**")
                            else:
                                st.text(f"  {line.strip()}")
                        else:
                            st.caption(f"  {line.strip()}")

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

                # 添加一个按钮，让用户选择是否刷新查看结果
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

        except Exception as e:
            # 清理临时文件
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)

            # 错误处理
            from utils.error_handler import ErrorHandler
            error_info = ErrorHandler.handle_error(e, "analysis")
            st.error(f"❌ {error_info['user_message']}")

            if error_info.get("detail_message"):
                with st.expander("💡 详细信息"):
                    st.code(error_info['detail_message'])

            # 显示完整错误栈
            import traceback
            with st.expander("🔍 技术详情"):
                st.code(traceback.format_exc())


def display_results_section():
    """显示分析结果区域"""
    st.header("📊 分析报告")

    if "analysis_result" not in st.session_state:
        st.info("📭 请先上传简历进行分析")
        return

    result = st.session_state.analysis_result
    state = result.get("state", {})

    # 文件名
    filename = st.session_state.get("uploaded_file_name", "未知文件")

    # 1. 总分概览
    st.markdown(f"### 📋 分析结果 - {filename}")

    # 总分仪表盘
    total_score = state.get("total_score", 0)
    score_color = get_score_color(total_score)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.metric(
            label="综合评分",
            value=f"{total_score:.1f}",
            delta=None,
            delta_color="normal",
            help="基于四个维度的加权总分"
        )

    with col2:
        st.markdown(f"#### {score_color} 等级")
        st.markdown(get_score_level_text(total_score))

    st.markdown("---")

    # 2. 各维度得分
    st.subheader("📈 各维度得分")

    score_breakdown = state.get("score_breakdown", {})

    # 定义维度列表（需要在两处使用）
    dimensions = [
        ("技术能力", "technical", "🔧"),
        ("经验背景", "experience", "💼"),
        ("项目经验", "project", "📁"),
        ("软技能", "soft_skill", "💡")
    ]

    # 显示总分计算过程
    with st.expander("💡 查看总分计算详情", expanded=False):
        st.markdown("### 总分计算方式")

        total_calculated = 0
        dimension_data = []

        for name, key, emoji in dimensions:
            data = score_breakdown.get(key, {})
            score = data.get("score", 0)
            weight = data.get("weight", 0)
            weighted_score = score * weight
            total_calculated += weighted_score

            dimension_data.append({
                "name": name,
                "key": key,
                "score": score,
                "weight": weight,
                "weighted_score": weighted_score
            })

        # 创建表格显示计算过程
        import pandas as pd

        # 格式化显示
        display_df = pd.DataFrame({
            "维度": [f"{emoji} {row['name']}" for row in dimension_data],
            "得分": [f"{row['score']:.1f}" for row in dimension_data],
            "权重": [f"{row['weight']:.0%}" for row in dimension_data],
            "加权得分": [f"{row['weighted_score']:.2f}" for row in dimension_data]
        })

        st.table(display_df)

        st.markdown("---")
        st.markdown(f"**总分 = Σ(维度得分 × 权重) = {total_calculated:.2f}**")

        # 评分等级说明
        st.info("""
        📊 **评分等级标准**：
        - **85分以上**: 优秀 - 综合能力突出，推荐录用
        - **75-85分**: 良好 - 综合能力较强，优先考虑
        - **65-75分**: 合格 - 基本符合要求，可以考虑
        - **65分以下**: 不推荐 - 综合能力不足，谨慎考虑
        """)

    st.markdown("---")

    # 创建四个维度的卡片
    col1, col2, col3, col4 = st.columns(4)

    for col, (name, key, emoji) in zip([col1, col2, col3, col4], dimensions):
        with col:
            data = score_breakdown.get(key, {})
            score = data.get("score", 0)
            weight = data.get("weight", 0)
            weighted_score = data.get("weighted_score", 0)
            detail_scores = data.get("detail_scores", {})

            st.metric(
                label=f"{emoji} {name}",
                value=f"{score:.1f}",
                delta=f"权重{weight:.0%}",
                delta_color="normal"
            )

            # 显示详细分项得分/展示维度
            if detail_scores:
                # 使用中文名称映射
                detail_names = {
                    "technical": {
                        # v2.1更新：技术能力使用展示维度
                        "技能总数": "技能总数",
                        "精通": "精通",
                        "熟练": "熟练",
                        "熟悉": "熟悉",
                        "了解": "了解",
                        "热门技术": "热门技术",
                        "验证技能": "验证技能",
                        "验证比例": "验证比例"
                    },
                    "experience": {
                        "years": "年限",
                        "company": "公司",
                        "growth": "发展",
                        "industry": "行业",
                        # 新增：经验背景详细字段
                        "教育背景_学历层次": "学历",
                        "教育背景_学校层次": "学校",
                        "工作经验_年限": "年限",
                        "工作经验_公司质量": "公司",
                        "工作经验_职位级别": "职位",
                        "工作经验_职业发展": "发展",
                        "实习经验_质量": "实习质量",
                        "实习经验_时长": "实习时长"
                    },
                    "project": {
                        "quantity": "数量",
                        "complexity": "复杂度",
                        "tech_depth": "深度",
                        "achievements": "成果",
                        # 新增：项目经验详细字段
                        "项目数量": "数量",
                        "项目质量": "质量",
                        "技术深度": "技术深度",
                        "业务价值": "业务价值"
                    },
                    "soft_skill": {
                        "expression": "表达",
                        "learning": "学习",
                        "teamwork": "协作",
                        "leadership": "领导力"
                    }
                }


    # 3. 详细分析（展开器）
    st.markdown("---")
    st.subheader("📋 详细分析")

    # 分析步骤
    steps_completed = state.get("steps_completed", [])
    steps_failed = state.get("steps_failed", [])

    if steps_completed:
        st.success(f"✅ 完成的步骤: {', '.join(steps_completed)}")
    if steps_failed:
        st.warning(f"⚠️ 失败的步骤: {', '.join(steps_failed)}")

    # Tab页面显示详细分析
    tab_a, tab_b, tab_c, tab_d = st.tabs(["技术能力", "经验背景", "项目经验", "软技能"])

    # 从score_breakdown获取各维度的详细分析
    score_breakdown = state.get("score_breakdown", {})

    # 技术能力详情
    with tab_a:
        tech_data = score_breakdown.get("technical", {})
        display_dimension_detail_with_scores(
            "技术能力",
            tech_data.get("score", 0),
            tech_data.get("detail_scores", {}),
            tech_data.get("raw_analysis", {})
        )

    # 经验背景详情
    with tab_b:
        exp_data = score_breakdown.get("experience", {})
        exp_raw = exp_data.get("raw_analysis", {})
        exp_detail = exp_data.get("detail_scores", {})
        exp_total = exp_data.get("score", 0)

        display_dimension_detail_with_scores(
            "经验背景",
            exp_total,
            exp_detail,
            exp_raw
        )

        # 新增：经验背景总分计算方式
        st.markdown("**总分计算方式（三维度加权 + 归一化）：**")

        st.info("📌 以下显示经验背景总分的详细计算过程")

        # 步骤1：显示各维度得分
        st.markdown("**步骤1：计算各维度原始得分**")

        with st.expander("📖 查看评分标准", expanded=False):
            st.markdown("""
            | 维度 | 评分标准 | 最高分 |
            |------|----------|--------|
            | 教育背景 | 学历分数 + 学校分数 | 200分（100+100） |
            | 工作经验 | 工作年限 × 每年分数 | 100分 |
            | 实习经验 | 实习月数 × 每月分数 | 100分 |

            **权重分配**：
            - 教育背景：50%
            - 工作经验：50%
            - 实习经验：1%
            """)

        # 创建表格显示各维度得分
        import pandas as pd

        # 从 detail_scores 中提取各维度得分
        education_score = (
            exp_detail.get("教育背景_学历层次", 0) +
            exp_detail.get("教育背景_学校层次", 0)
        )
        work_score = exp_detail.get("工作经验_年限", 0)
        internship_score = exp_detail.get("实习经验_时长", 0)

        table_data = [
            {"维度": "教育背景", "得分": f"{education_score:.1f}", "说明": "学历 + 学校"},
            {"维度": "工作经验", "得分": f"{work_score:.1f}", "说明": "工作年限 × 20分/年"},
            {"维度": "实习经验", "得分": f"{internship_score:.1f}", "说明": "实习月数 × 33.2分/月"}
        ]

        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # 步骤2：显示加权计算
        st.markdown("**步骤2：计算加权总分**")

        # 从配置获取权重（或使用默认值）
        from core.config import ScoreConfig
        try:
            config = ScoreConfig.from_yaml('config/scoring.yaml')
            weights = config.experience_dimension_weights
        except:
            weights = {"education": 0.50, "work": 0.50, "internship": 0.01}

        edu_weight = weights.get("education", 0.50)
        work_weight = weights.get("work", 0.50)
        intern_weight = weights.get("internship", 0.01)

        weighted_education = education_score * edu_weight
        weighted_work = work_score * work_weight
        weighted_internship = internship_score * intern_weight
        weighted_total = weighted_education + weighted_work + weighted_internship

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric(
                "教育背景加权",
                f"{weighted_education:.1f}分",
                help=f"{education_score:.1f} × {edu_weight}"
            )
        with col_b:
            st.metric(
                "工作经验加权",
                f"{weighted_work:.1f}分",
                help=f"{work_score:.1f} × {work_weight}"
            )
        with col_c:
            st.metric(
                "实习经验加权",
                f"{weighted_internship:.1f}分",
                help=f"{internship_score:.1f} × {intern_weight}"
            )

        st.markdown(f"""
        **计算过程**：
        ```
        加权总分 = 教育背景 × {edu_weight} + 工作经验 × {work_weight} + 实习经验 × {intern_weight}
                 = {education_score:.1f} × {edu_weight} + {work_score:.1f} × {work_weight} + {internship_score:.1f} × {intern_weight}
                 = {weighted_education:.1f} + {weighted_work:.1f} + {weighted_internship:.1f}
                 = {weighted_total:.1f}分
        ```
        """)

        # 步骤3：归一化到0-100
        st.markdown("**步骤3：归一化到0-100分**")

        # 计算理论最高分
        max_education = 200  # 博士100 + 985 100
        max_work = 100       # 3年 × 20分/年
        max_internship = 100 # 4个月 × 33.2分/月（约133分，但封顶100分）

        max_possible = (
            max_education * edu_weight +
            max_work * work_weight +
            max_internship * intern_weight
        )

        st.markdown(f"""
        **计算过程**：
        ```
        理论最高分 = {max_education} × {edu_weight} + {max_work} × {work_weight} + {max_internship} × {intern_weight}
                   = {max_education * edu_weight:.1f} + {max_work * work_weight:.1f} + {max_internship * intern_weight:.1f}
                   = {max_possible:.1f}分

        归一化得分 = (加权总分 / 理论最高分) × 100
                   = ({weighted_total:.1f} / {max_possible:.1f}) × 100
                   = {exp_total:.1f}分
        ```
        """)

        # 显示最终结果
        st.success(f"🎯 **经验背景总分：{exp_total:.1f}分**")

        # 设计理念说明
        with st.expander("💡 了解评分设计理念", expanded=False):
            st.markdown(f"""
            **为什么要三维度加权？**

            1. **平衡教育与经验**
               - 教育背景和工作经验各占50%
               - 避免单一维度压倒性影响
               - 适合不同类型的候选人

            2. **归一化处理的优势**
               - 理论最高分可达{max_possible:.0f}分，归一化到100分
               - 分数更直观，便于理解
               - 不同配置下的分数可以比较

            3. **灵活的配置化设计**
               - 权重可通过 config/scoring.yaml 调整
               - 学历分数、学校分数都可配置
               - 工作经验评分规则（每年分数、封顶）可配置

            **当前配置**：
            - 教育背景权重：{edu_weight*100:.0f}%
            - 工作经验权重：{work_weight*100:.0f}%
            - 实习经验权重：{intern_weight*100:.0f}%
            """)

        # 显示原始简历信息（教育背景和工作经验）
        st.markdown("---")
        st.markdown("### 📝 简历详细信息")

        resume_data = state.get("resume_data", {})

        # 教育背景
        education = resume_data.get("education", [])
        if education:
            st.markdown("#### 🎓 教育背景")
            for edu in education:
                school = edu.get("school", "")
                degree = edu.get("degree", "")
                major = edu.get("major", "")
                start_time = edu.get("start_time", edu.get("start_date", ""))
                end_time = edu.get("end_time", edu.get("end_date", ""))
                time_range = f"{start_time} ~ {end_time}" if start_time or end_time else "未知时间"

                with st.expander(f"📚 {school} - {degree}", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**学校**: {school}")
                        st.write(f"**学历**: {degree}")
                    with col2:
                        st.write(f"**专业**: {major}")
                        st.write(f"**时间**: {time_range}")

                    # LLM生成的学校描述
                    with st.spinner(f"正在获取{school}的信息..."):
                        school_description = get_school_description(school)
                        st.info(f"📍 {school_description}")

                    if edu.get("description"):
                        st.write(f"**描述**: {edu['description']}")
        else:
            st.info("暂无教育背景信息")

        # 工作经验
        work_experience = resume_data.get("work_experience", [])
        if work_experience:
            st.markdown("#### 💼 工作经验")
            for work in work_experience:
                company = work.get("company", "")
                position = work.get("position", "")
                start_time = work.get("start_time", work.get("start_date", ""))
                end_time = work.get("end_time", work.get("end_date", ""))
                time_range = f"{start_time} ~ {end_time}" if start_time or end_time else "未知时间"

                with st.expander(f"🏢 {company} - {position}", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**公司**: {company}")
                        st.write(f"**职位**: {position}")
                    with col2:
                        st.write(f"**时间**: {time_range}")
                        if work.get("industry"):
                            st.write(f"**行业**: {work['industry']}")
                        if work.get("company_scale"):
                            st.write(f"**规模**: {work['company_scale']}")

                    # LLM生成的公司描述
                    with st.spinner(f"正在获取{company}的信息..."):
                        company_description = get_company_description(company)
                        st.info(f"🏢 {company_description}")

                    if work.get("description"):
                        st.write(f"**职责描述**: {work['description']}")

                    achievements = work.get("achievements", [])
                    if achievements:
                        st.write("**主要业绩**:")
                        for achievement in achievements:
                            st.write(f"- {achievement}")
        else:
            st.info("暂无工作经验信息")

    # 项目经验详情
    with tab_c:
        proj_data = score_breakdown.get("project", {})
        display_dimension_detail_with_scores(
            "项目经验",
            proj_data.get("score", 0),
            proj_data.get("detail_scores", {}),
            proj_data.get("raw_analysis", {})
        )

    # 软技能详情
    with tab_d:
        soft_data = score_breakdown.get("soft_skill", {})
        display_dimension_detail_with_scores(
            "软技能",
            soft_data.get("score", 0),
            soft_data.get("detail_scores", {}),
            soft_data.get("raw_analysis", {})
        )

    # 4. 优化建议（可展开）
    st.markdown("---")
    st.subheader("💡 优化建议")

    optimization_suggestions = state.get("optimization_suggestions", [])

    # 检查是否有解析错误
    if optimization_suggestions and len(optimization_suggestions) > 0:
        first_suggestion = optimization_suggestions[0]

        # 检查是否为错误格式
        if isinstance(first_suggestion, dict) and "error" in first_suggestion:
            st.error(f"⚠️ 优化建议生成失败：{first_suggestion['error']}")
            st.info("💡 提示：LLM返回的JSON格式有误，请检查日志或重新分析")
        elif isinstance(first_suggestion, str):
            st.error(f"⚠️ 优化建议格式错误：{first_suggestion}")
        else:
            # 正常显示优化建议
            for i, suggestion in enumerate(optimization_suggestions, 1):
                # 跳过无效建议
                if not isinstance(suggestion, dict):
                    continue

                priority = suggestion.get("priority", "中")
                priority_emoji = {
                    "高": "🔴",
                    "中": "🟡",
                    "低": "🟢"
                }.get(priority, "⚪")

                # 在标题中显示问题摘要（前30字）
                category = suggestion.get('category', '建议')
                problem = suggestion.get('problem_analysis', '')
                problem_preview = problem[:30] + "..." if len(problem) > 30 else problem

                with st.expander(f"{i}. {priority_emoji} {category}: {problem_preview}", expanded=False):
                    # 新格式：详细建议（紧凑布局）
                    if suggestion.get("problem_analysis"):
                        st.markdown("**🔍 问题**")
                        st.write(suggestion.get("problem_analysis", ""))

                        st.markdown("**📋 改进步骤**")
                        action_steps = suggestion.get("action_steps", [])
                        if isinstance(action_steps, list):
                            for step in action_steps:
                                st.markdown(f"- {step}")
                        else:
                            st.write(action_steps)

                        # 改进示例（可选，如果有内容才显示）
                        before_after = suggestion.get("before_after", "")
                        if before_after and len(before_after.strip()) > 10:
                            with st.expander("✨ 查看改进示例", expanded=False):
                                st.markdown(before_after)

                        st.markdown("**🎯 预期效果**")
                        st.success(suggestion.get("expected_benefit", ""))
                    # 旧格式：简单建议（向后兼容）
                    else:
                        st.write(suggestion.get("suggestion", ""))
                        if suggestion.get("example"):
                            st.info(f"💡 示例: {suggestion['example']}")
    else:
        st.info("✨ 各项指标表现良好，暂无明显改进建议")

    # 5. 分析时间
    if "completed_at" in state:
        st.caption(f"分析完成时间: {state['completed_at']}")


def display_dimension_detail_with_scores(
    dimension_name: str,
    total_score: float,
    detail_scores: dict,
    dimension_data: dict
):
    """显示维度详细分析（包含分项得分/展示维度）"""

    # 中文名称映射
    detail_name_mapping = {
        "technical": {
            # v2.1更新：技术能力使用展示维度（统计信息而非分数）
            "技能总数": "技能总数",
            "精通": "精通",
            "熟练": "熟练",
            "熟悉": "熟悉",
            "了解": "了解",
        },
        "experience": {
            # 经验背景评分（极简版）
            "教育背景_学历层次": "学历层次",
            "教育背景_学校层次": "学校层次",
            "工作经验_年限": "工作年限",
            "实习经验_时长": "实习时长"
        },
        "project": {
            # 极简评分
            "平均质量": "平均质量"
        },
        "soft_skill": {
            "expression": "表达能力",
            "learning": "学习能力",
            "teamwork": "团队协作",
            "leadership": "领导力"
        }
    }

    # 维度键名（用于查找映射）
    # 注意：先匹配更具体的词（项目、软技能），再匹配包含关系（经验、技术）
    if "项目" in dimension_name:
        dimension_key = "project"
    elif "软" in dimension_name or "软技能" in dimension_name:
        dimension_key = "soft_skill"
    elif "技术" in dimension_name:
        dimension_key = "technical"
    elif "经验" in dimension_name:
        dimension_key = "experience"
    else:
        # 默认处理
        dimension_key = dimension_name.replace("能力", "").replace("背景", "").replace("经验", "").replace("技能", "")

    st.markdown(f"### 总分: {total_score:.1f} / 100")

    # 分项得分或展示维度
    if detail_scores:
        # 技术能力特殊处理：显示为"技能统计"而非"分项得分"
        if dimension_key == "technical":
            # 技能熟练度分布
            if all(key in detail_scores for key in ["精通", "熟练", "熟悉", "了解"]):
                st.markdown("**熟练度分布：**")
                exp_col1, exp_col2 = st.columns(2)
                with exp_col1:
                    st.metric("精通", detail_scores.get("精通", 0), help="专家级，能独立设计系统架构")
                    st.metric("熟练", detail_scores.get("熟练", 0), help="高级，能独立完成复杂任务")
                with exp_col2:
                    st.metric("熟悉", detail_scores.get("熟悉", 0), help="中级，能在指导下完成常规任务")
                    st.metric("了解", detail_scores.get("了解", 0), help="初级，基础认知，需要学习")

            # 其他统计信息
            stat_col1, stat_col2, stat_col3 = st.columns(3)
            with stat_col1:
                if "技能总数" in detail_scores:
                    st.metric("技能总数", detail_scores["技能总数"], help="掌握的技能总数量")
                if "热门技术" in detail_scores:
                    st.metric("热门技术", detail_scores["热门技术"], help="A类热门技术数量")
            with stat_col2:
                if "验证技能" in detail_scores:
                    st.metric("验证技能", detail_scores["验证技能"], help="在项目中验证过的技能数")
            with stat_col3:
                if "验证比例" in detail_scores:
                    st.metric("验证比例", detail_scores["验证比例"], help="验证技能占比")

            # 总分计算说明
            st.markdown("---")

            # 显示技术能力得分明细（按熟练度加权平均）
            # dimension_data 本身就是 raw_analysis
            skill_breakdown = dimension_data.get("skill_breakdown", {})

            # 显示技能列表
            if skill_breakdown and "skills" in skill_breakdown:
                st.markdown("#### 📋 技能列表")

                skills = skill_breakdown["skills"]

                # 按熟练度分组显示
                expert_skills = [s for s in skills if s["level"] == "精通"]
                senior_skills = [s for s in skills if s["level"] == "熟练"]
                familiar_skills = [s for s in skills if s["level"] == "熟悉"]
                beginner_skills = [s for s in skills if s["level"] == "了解"]

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

                st.markdown("---")

            st.markdown("**总分计算方式（按熟练度加权平均）：**")

            if skill_breakdown and "skills" in skill_breakdown:
                st.info("📌 以下显示技术能力总分的详细计算过程（按熟练度加权平均）")

                # 步骤1：显示每个技能的得分计算
                st.markdown("**步骤1：计算每个技能的加权分**")

                with st.expander("📖 查看评分标准", expanded=False):
                    st.markdown("""
                    | 熟练度 | 等级分 | 权重 | 说明 |
                    |--------|--------|------|------|
                    | 精通 | 80分 | 1.5 | 核心技能，权重最高 |
                    | 熟练 | 60分 | 1.0 | 主要技能，标准权重 |
                    | 熟悉 | 40分 | 0.7 | 可用技能，权重较低 |
                    | 了解 | 20分 | 0.5 | 入门技能，权重最低 |
                    """)

                # 创建表格显示每个技能的得分
                import pandas as pd

                # 准备表格数据
                table_data = []
                for skill_info in skill_breakdown["skills"]:
                    table_data.append({
                        "技能": skill_info["name"],
                        "等级": skill_info["level"],
                        "等级分": skill_info["level_score"],
                        "权重": skill_info["weight"],
                        "加权分": skill_info["weighted_score"],
                        "计算": f"{skill_info['level_score']} × {skill_info['weight']}"
                    })

                df = pd.DataFrame(table_data)
                st.dataframe(df, use_container_width=True, hide_index=True)

                # 步骤2：显示汇总计算
                st.markdown("**步骤2：计算加权平均分**")

                weighted_sum = skill_breakdown.get("weighted_sum", 0)
                weight_sum = skill_breakdown.get("weight_sum", 0)
                avg_weighted_score = skill_breakdown.get("avg_weighted_score", 0)

                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric(
                        "加权总分",
                        f"{weighted_sum:.2f}分",
                        help="所有技能的加权分之和"
                    )
                with col_b:
                    st.metric(
                        "权重总和",
                        f"{weight_sum:.2f}",
                        help="所有熟练度权重之和"
                    )

                st.markdown(f"""
                **计算过程**：
                ```
                加权平均分 = 加权总分 / 权重总和
                            = {weighted_sum:.2f} / {weight_sum:.2f}
                            = {avg_weighted_score:.2f}分
                ```
                """)

                # 步骤3：归一化到0-100
                st.markdown("**步骤3：归一化到0-100分**")

                st.markdown(f"""
                **计算过程**：
                ```
                最终得分 = (加权平均分 / 满分80) × 100
                        = ({avg_weighted_score:.2f} / 80) × 100
                        = {total_score:.1f}分
                ```
                """)

                # 显示最终结果
                st.success(f"🎯 **技术能力总分：{total_score:.1f}分**")

                # 设计理念说明
                with st.expander("💡 了解评分设计理念", expanded=False):
                    st.markdown("""
                    **为什么要按熟练度加权？**

                    1. **突出核心技能**
                       - 精通技能权重1.5倍，能显著提升总分
                       - 1个精通技能 > 5个了解技能
                       - 符合实际招聘需求

                    2. **避免技能堆砌**
                       - 了解技能权重低（0.5），堆砌收益低
                       - 鼓励深度学习而非广度撒网
                       - 客观反映真实能力

                    3. **加权平均的优势**
                       - 比简单平均更准确
                       - 体现技能的熟练度分布
                       - 权重反映技能的重要性
                    """)
            else:
                # 即使没有详细数据，也显示计算说明
                st.info("📌 技术能力总分采用按熟练度加权平均计算")

                st.markdown("**计算公式**: 总分 = (Σ(技能等级分 × 熟练度权重) / Σ(熟练度权重)) / 满分80 × 100")

                st.caption("""
                💡 **详细说明**：

                1️⃣ **技能等级评分**：
                - 精通：80分（核心技能，权重1.5）
                - 熟练：60分（主要技能，权重1.0）
                - 熟悉：40分（可用技能，权重0.7）
                - 了解：20分（入门技能，权重0.5）

                2️⃣ **加权计算**：
                - 每个技能的加权分 = 技能等级分 × 熟练度权重
                - 例如：精通Python = 80分 × 1.5 = 120分

                3️⃣ **加权平均分**：
                - 加权平均分 = 所有技能的加权分之和 / 所有权重之和
                - 例如：(120 + 60 + 28) / (1.5 + 1.0 + 0.7) = 208 / 3.2 = 65分

                4️⃣ **最终得分**：
                - 总分 = (加权平均分 / 满分80) × 100
                - 归一化到0-100分范围

                📊 **当前总分**：**{total_score:.1f}分**
                """)
        elif dimension_key == "project":
            # 项目经验：显示分项得分 + 项目详细评分

            # 总分计算说明
            st.markdown("**总分计算方式（平均项目分 + 归一化）：**")

            # 检查是否有项目数据
            project_scores = dimension_data.get("project_scores", [])

            if project_scores:
                st.info("📌 以下显示项目经验总分的详细计算过程")

                # 步骤1：显示每个项目的评分标准
                st.markdown("**步骤1：计算每个项目的原始得分**")

                with st.expander("📖 查看评分标准", expanded=False):
                    st.markdown("""
                    | 评分项 | 满分 | 评分标准 |
                    |--------|------|----------|
                    | 基础分 | 10分 | 有项目名称、角色、时间得10分；只有名称或角色得5分 |
                    | 技术栈分 | 15分 | 0项技术0分；1-3项5分；4-6项10分；7+项15分 |
                    | 描述质量分 | 15分 | 根据描述长度和是否有成果综合评分（0-15分） |
                    | 规模分 | 10分 | 根据团队规模和项目时长综合评分（0-10分） |
                    | **项目总分** | **50分** | **基础分 + 技术栈分 + 描述质量分 + 规模分** |

                    **最终得分**：
                    - 项目经验总分 = 所有项目的平均分，归一化到0-100
                    - 例如：3个项目分别得40分、45分、35分，平均40分，归一化后为 (40/50)×100 = 80分
                    """)

                # 步骤2：显示每个项目的得分
                st.markdown("**步骤2：所有项目得分汇总**")

                import pandas as pd

                # 准备表格数据
                table_data = []
                for proj in project_scores:
                    score_breakdown = proj.get('score_breakdown', {})
                    table_data.append({
                        "项目名称": proj.get('name', '未知'),
                        "基础分": score_breakdown.get('基础分', 0),
                        "技术栈分": score_breakdown.get('技术栈分', 0),
                        "描述质量分": score_breakdown.get('描述质量分', 0),
                        "规模分": score_breakdown.get('规模分', 0),
                        "项目得分": proj.get('score', 0)
                    })

                df = pd.DataFrame(table_data)
                st.dataframe(df, use_container_width=True, hide_index=True)

                # 步骤3：计算平均分
                st.markdown("**步骤3：计算平均分并归一化**")

                total_score_sum = sum(proj.get('score', 0) for proj in project_scores)
                project_count = len(project_scores)
                avg_score = total_score_sum / project_count if project_count > 0 else 0
                normalized_score = (avg_score / 50) * 100 if avg_score > 0 else 0

                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric(
                        "平均项目分",
                        f"{avg_score:.1f}分",
                        help=f"{total_score_sum:.1f} ÷ {project_count}个项目"
                    )
                with col_b:
                    st.metric(
                        "归一化得分",
                        f"{normalized_score:.1f}分",
                        help=f"({avg_score:.1f} ÷ 50) × 100"
                    )

                st.markdown(f"""
                **计算过程**：
                ```
                平均项目分 = {total_score_sum:.1f} ÷ {project_count} = {avg_score:.1f}分
                归一化得分 = (平均项目分 / 满分50) × 100
                           = ({avg_score:.1f} / 50) × 100
                           = {normalized_score:.1f}分
                ```
                """)

                # 显示最终结果
                st.success(f"🎯 **项目经验总分：{total_score:.1f}分**")

                # 设计理念说明
                with st.expander("💡 了解评分设计理念", expanded=False):
                    st.markdown(f"""
                    **为什么要用平均项目分？**

                    1. **避免项目数量偏差**
                       - 采用平均分而非总分，避免项目多的候选人占优势
                       - 3个高质量项目 > 10个低质量项目
                       - 关注项目质量而非数量

                    2. **多维度综合评分**
                       - 基础分（10分）：确保项目有基本完整信息
                       - 技术栈分（15分）：鼓励掌握多种技术
                       - 描述质量分（15分）：重视项目描述的完整性
                       - 规模分（10分）：认可大规模、长周期的项目

                    3. **归一化的优势**
                       - 满分50分，归一化到100分更直观
                       - 便于与其他维度比较
                       - 符合常规的百分制评分习惯

                    **当前统计**：
                    - 项目数量：{project_count}个
                    - 最高分项目：{max(proj.get('score', 0) for proj in project_scores)}分
                    - 最低分项目：{min(proj.get('score', 0) for proj in project_scores)}分
                    - 平均得分：{avg_score:.1f}分 / 50分
                    """)
            else:
                # 没有项目数据时显示通用说明
                st.info("📌 项目经验总分采用平均项目分并归一化到0-100")

                st.markdown("**计算公式**: 总分 = (Σ(各项目得分) / 项目数量) / 满分50 × 100")

                st.caption("""
                💡 **详细说明**：

                1️⃣ **单项项目评分**（最高50分）：
                - 基础分（10分）：有项目名称、角色、时间
                - 技术栈分（15分）：根据技术数量评分（0-15分）
                - 描述质量分（15分）：根据描述长度和成果评分（0-15分）
                - 规模分（10分）：根据团队规模和项目时长评分（0-10分）

                2️⃣ **平均分计算**：
                - 平均项目分 = 所有项目得分之和 / 项目数量
                - 例如：(40 + 45 + 35) / 3 = 40分

                3️⃣ **归一化到0-100**：
                - 总分 = (平均项目分 / 50) × 100
                - 例如：(40 / 50) × 100 = 80分

                📊 **当前总分**：**{total_score:.1f}分**
                """)

            st.markdown("---")
            st.markdown("#### 📊 分项得分")

            name_map = detail_name_mapping.get(dimension_key, {})

            # 显示分项得分（2列布局）
            cols = st.columns(min(len(detail_scores), 4))
            for i, (key, value) in enumerate(detail_scores.items()):
                col = cols[i % len(cols)]
                with col:
                    chinese_name = name_map.get(key, key)
                    if isinstance(value, (int, float)):
                        st.metric(
                            label=chinese_name,
                            value=f"{value:.1f}",
                            help=f"{chinese_name}"
                        )

            # 显示项目详细评分（dimension_data 本身就是 raw_analysis）
            project_scores = dimension_data.get("project_scores", [])

            if project_scores:
                st.markdown("---")
                st.markdown("#### 📋 项目详细评分")

                # 说明
                st.info("💡 每个项目最高50分 = 基础分(10) + 技术栈分(0-15) + 描述质量分(0-15) + 规模分(0-10)")

                # 按得分降序排序
                sorted_projects = sorted(project_scores, key=lambda x: x.get("score", 0), reverse=True)

                for proj in sorted_projects:
                    score = proj.get('score', 0)
                    score_color = "🟢" if score >= 40 else "🟡" if score >= 30 else "🔴"

                    # 标题：项目名称 + 得分
                    with st.expander(f"{score_color} 《{proj.get('name', '未知项目')}》 - {score}/50分", expanded=False):
                        # 基本信息
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**角色**: {proj.get('role', '未知')}")
                        with col2:
                            st.write(f"**时间**: {proj.get('start_time', '')} ~ {proj.get('end_time', '进行中')}")
                        with col3:
                            st.metric("得分", f"{score}/50")

                        # 技术栈
                        tech_stack = proj.get('tech_stack', [])
                        if tech_stack:
                            st.markdown("**🔧 技术栈**")
                            tags = ", ".join([f"`{tech}`" for tech in tech_stack[:8]])  # 最多显示8个
                            if len(tech_stack) > 8:
                                tags += f" ... (+{len(tech_stack) - 8}项)"
                            st.markdown(tags)

                        # 项目描述
                        description = proj.get('description', '')
                        if description:
                            with st.expander("📝 项目描述", expanded=False):
                                st.write(description)

                        # 成果
                        achievements = proj.get('achievements', [])
                        if achievements:
                            st.markdown("**✨ 成果**")
                            for achievement in achievements:
                                st.write(f"- {achievement}")

                        # 评分明细
                        score_breakdown = proj.get('score_breakdown', {})
                        if score_breakdown:
                            st.markdown("---")
                            st.markdown("**📊 评分明细**")

                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("基础分", f"{score_breakdown.get('基础分', 0)}/10", help="项目名称、角色、时间")
                            with col2:
                                st.metric("技术栈", f"{score_breakdown.get('技术栈分', 0)}/15", help="技术数量丰富度")
                            with col3:
                                st.metric("描述质量", f"{score_breakdown.get('描述质量分', 0)}/15", help="描述长度 + 成果")
                            with col4:
                                st.metric("规模分", f"{score_breakdown.get('规模分', 0)}/10", help="团队规模 + 项目时长")

                        # 团队规模（如果有）
                        team_size = proj.get('team_size')
                        if team_size:
                            if not score_breakdown:  # 如果没有显示评分明细，就显示团队规模
                                st.markdown("---")
                            st.info(f"👥 团队规模：{team_size}人")

                        # 面试问题（如果有）
                        interview_questions = proj.get('interview_questions', [])
                        if interview_questions:
                            st.markdown("---")
                            st.markdown("💡 **面试准备建议**")
                            for i, qa in enumerate(interview_questions, 1):
                                difficulty = "初级" if i == 1 else "中级" if i == 2 else "高级"
                                with st.expander(f"Q{i}: {qa['question']}", expanded=False):
                                    st.markdown(f"**难度**: {difficulty}")
                                    st.markdown(f"**参考答案**: {qa['answer']}")

                        else:
                            # 如果没有面试问题，显示调试信息
                            if 'interview_questions' in proj:
                                st.caption("💡 面试问题生成失败（可能是API Key未配置或LLM调用失败）")
                            else:
                                st.caption("💡 面试问题功能需要配置API Key")

        else:
            # 其他维度保持原样（分项得分）
            st.markdown("#### 📊 分项得分")

            name_map = detail_name_mapping.get(dimension_key, {})

            # 使用4列布局显示分项得分
            cols = st.columns(len(detail_scores))
            for col, (key, value) in zip(cols, detail_scores.items()):
                with col:
                    chinese_name = name_map.get(key, key)
                    # 判断是否为数值类型
                    if isinstance(value, (int, float)):
                        st.metric(
                            label=chinese_name,
                            value=f"{value:.1f}",
                            help=f"{chinese_name}得分"
                        )
                    else:
                        # 字符串类型（如"75%"）直接显示
                        st.metric(
                            label=chinese_name,
                            value=str(value),
                            help=f"{chinese_name}"
                        )

    st.markdown("---")

    # 显示原有的详细分析内容
    if dimension_data:
        # 关键发现
        if "key_findings" in dimension_data and dimension_data["key_findings"]:
            st.markdown("#### 🔍 关键发现")
            for finding in dimension_data["key_findings"]:
                st.write(f"• {finding}")

        # 优势
        if "strengths" in dimension_data and dimension_data["strengths"]:
            st.markdown("#### ✨ 优势")
            for strength in dimension_data["strengths"]:
                st.write(f"✓ {strength}")

        # 不足
        if "weaknesses" in dimension_data and dimension_data["weaknesses"]:
            st.markdown("#### 📈 待改进")
            for weakness in dimension_data["weaknesses"]:
                st.write(f"- {weakness}")

    if not detail_scores and not dimension_data:
        st.info("暂无详细分析数据")


def export_report_section():
    """导出报告区域"""
    st.header("📥 导出分析报告")

    if "analysis_result" not in st.session_state:
        st.info("📭 请先上传简历进行分析")
        return

    result = st.session_state.analysis_result
    reports = result.get("reports", {})
    state = result.get("state", {})

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📋 可用的报告类型")

        available_reports = []
        for report_type, report_data in reports.items():
            available_reports.append(report_type)

        if available_reports:
            for report_type in available_reports:
                st.write(f"- **{report_type}**: {get_report_type_name(report_type)}")
        else:
            st.info("没有可用的报告")

    with col2:
        st.subheader("📊 数据摘要")

        total_score = state.get("total_score", 0)
        st.metric("综合评分", f"{total_score:.1f}分")

        if "steps_completed" in state:
            completed = state["steps_completed"]
            st.caption(f"已完成 {len(completed)} 个分析步骤")

    # 导出按钮
    st.markdown("---")
    st.subheader("📤 导出报告")

    col1, col2 = st.columns([2, 2])

    with col1:
        # 选择要导出的报告类型
        export_format = st.selectbox(
            "选择导出格式",
            ["JSON", "Markdown", "HTML"],
            index=0
        )

    with col2:
        # 选择要导出的报告内容
        export_content = st.selectbox(
            "选择报告内容",
            list(reports.keys()) if reports else ["无"],
            index=0
        )

    # 导出按钮
    export_button = st.button(
        "📥 导出报告",
        type="primary",
        disabled=not reports,
        use_container_width=True
    )

    if export_button and reports:
        report_data = reports.get(export_content, {})

        # 导出逻辑
        try:
            if export_format == "JSON":
                # 导出为JSON
                json_str = json.dumps(report_data, ensure_ascii=False, indent=2)
                st.download_button(
                    label="📥 下载JSON报告",
                    data=json_str,
                    file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                st.success("✅ JSON报告已准备就绪，请点击上方下载按钮")

            elif export_format == "Markdown":
                # 导出为Markdown
                md_content = generate_markdown_report(state, report_data)
                st.download_button(
                    label="📥 下载Markdown报告",
                    data=md_content,
                    file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
                st.success("✅ Markdown报告已准备就绪，请点击上方下载按钮")

            elif export_format == "HTML":
                # 导出为HTML
                html_content = generate_html_report(state, report_data)
                st.download_button(
                    label="📥 下载HTML报告",
                    data=html_content,
                    file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html"
                )
                st.success("✅ HTML报告已准备就绪，请点击上方下载按钮")
                st.info("💡 提示：HTML报告包含精美的样式，可直接在浏览器中打开查看或打印为PDF")

        except Exception as e:
            st.error(f"❌ 导出失败: {str(e)}")


def generate_markdown_report(state: dict, report_data: dict) -> str:
    """生成Markdown格式的报告（完整版）"""
    lines = []

    # 标题和基本信息
    lines.append("# 📋 简历分析报告\n")
    lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # ========== 1. 综合评分（顶层） ==========
    if "total_score" in report_data:
        total_score = report_data.get("total_score", state.get("total_score", 0))
        lines.append("## 🎯 综合评分\n")
        lines.append(f"### **总分**: {total_score:.1f} 分")
        lines.append(f"**等级**: {report_data.get('score_level', get_score_level_text(total_score))}")
        lines.append(f"**推荐意见**: {report_data.get('recommendation', '')}\n")

        # 得分明细
        if "score_breakdown" in report_data:
            score_breakdown = report_data["score_breakdown"]
            lines.append("#### 📊 得分明细\n")

            if "dimensions" in score_breakdown:
                for dim_key, dim_data in score_breakdown["dimensions"].items():
                    name = dim_data.get("name", "")
                    score = dim_data.get("score", 0)
                    weight = dim_data.get("weight", 0)
                    weighted = dim_data.get("weighted_score", 0)
                    contrib = dim_data.get("contribution_percentage", 0)

                    lines.append(f"- **{name}**")
                    lines.append(f"  - 得分: {score:.1f} 分")
                    lines.append(f"  - 权重: {weight:.0%}")
                    lines.append(f"  - 加权得分: {weighted_score:.2f}")
                    lines.append(f"  - 贡献比例: {contrib:.1f}%")
                    lines.append("")

    # ========== 2. 执行摘要 ==========
    if "executive_summary" in report_data:
        exec_summary = report_data["executive_summary"]
        lines.append("## 📋 执行摘要\n")

        if "candidate_name" in exec_summary:
            lines.append(f"**候选人姓名**: {exec_summary['candidate_name']}\n")

        total_score = exec_summary.get("total_score", state.get("total_score", 0))
        lines.append(f"**综合评分**: {total_score:.1f} 分\n")
        lines.append(f"**等级**: {exec_summary.get('score_level', get_score_level_text(total_score))}\n")

        # 联系方式
        if "contact" in exec_summary:
            contact = exec_summary["contact"]
            lines.append("**联系方式**:")
            if "phone" in contact and contact["phone"]:
                lines.append(f"- 📞 电话: {contact['phone']}")
            if "email" in contact and contact["email"]:
                lines.append(f"- 📧 邮箱: {contact['email']}")
            lines.append("")

        # 快速概览
        if "quick_overview" in exec_summary:
            overview = exec_summary["quick_overview"]
            lines.append("**各维度得分概览**:")
            lines.append(f"- 🔧 技术能力: {overview.get('technical', 0)} 分")
            lines.append(f"- 💼 经验背景: {overview.get('experience', 0)} 分")
            lines.append(f"- 📁 项目经验: {overview.get('project', 0)} 分")
            lines.append(f"- 💡 软技能: {overview.get('soft_skill', 0)} 分")
            lines.append("")

    # ========== 3. 清洗后的简历信息 ==========
    if "cleaned_resume" in report_data:
        cleaned_resume = report_data["cleaned_resume"]
        lines.append("## 👤 清洗后的简历信息\n")

        # 基本信息
        if "personal_info" in cleaned_resume:
            personal_info = cleaned_resume["personal_info"]
            if any(personal_info.values()):
                lines.append("### 基本信息\n")
                if personal_info.get("name"):
                    lines.append(f"- **姓名**: {personal_info['name']}")
                if personal_info.get("phone"):
                    lines.append(f"- **电话**: {personal_info['phone']}")
                if personal_info.get("email"):
                    lines.append(f"- **邮箱**: {personal_info['email']}")
                if personal_info.get("location"):
                    lines.append(f"- **所在地**: {personal_info['location']}")
                if personal_info.get("gender"):
                    lines.append(f"- **性别**: {personal_info['gender']}")
                if personal_info.get("birth_date"):
                    lines.append(f"- **出生日期**: {personal_info['birth_date']}")
                lines.append("")

        # 技能清单
        if "skills" in cleaned_resume and cleaned_resume["skills"]:
            lines.append("### 🛠️ 技能清单\n")
            skills = cleaned_resume["skills"]
            for skill in skills:
                name = skill.get("name", "")
                level = skill.get("level", "")
                category = skill.get("category", "")
                level_text = f" ({level})" if level else ""
                category_text = f" [{category}]" if category else ""
                lines.append(f"- {name}{level_text}{category_text}")
            lines.append("")

        # 工作经历
        if "work_experience" in cleaned_resume and cleaned_resume["work_experience"]:
            lines.append("### 💼 工作经历\n")
            for exp in cleaned_resume["work_experience"]:
                company = exp.get("company", "")
                position = exp.get("position", "")
                start = exp.get("start_time", "")
                end = exp.get("end_time", "")
                desc = exp.get("description", "")

                lines.append(f"#### {company} | {position}")
                lines.append(f"- **时间**: {start} ~ {end}")

                if exp.get("industry"):
                    lines.append(f"- **行业**: {exp['industry']}")
                if exp.get("company_scale"):
                    lines.append(f"- **规模**: {exp['company_scale']}")

                if desc:
                    lines.append(f"- **描述**: {desc}")

                achievements = exp.get("achievements", [])
                if achievements:
                    lines.append("- **主要业绩**:")
                    for achievement in achievements:
                        lines.append(f"  - {achievement}")
                lines.append("")

        # 项目经验（包含Q&A）
        if "projects" in cleaned_resume and cleaned_resume["projects"]:
            lines.append("### 📁 项目经验\n")
            for proj in cleaned_resume["projects"]:
                name = proj.get("name", "")
                role = proj.get("role", "")
                start = proj.get("start_time", "")
                end = proj.get("end_time", "")
                score = proj.get("score", 0)

                score_emoji = "🟢" if score >= 40 else "🟡" if score >= 30 else "🔴"
                lines.append(f"#### {score_emoji} {name} - {role} ({score}分)" if score else f"#### {name} - {role}")
                lines.append(f"- **时间**: {start} ~ {end}")

                # 技术栈
                tech_stack = proj.get("tech_stack", [])
                if tech_stack:
                    lines.append(f"- **技术栈**: {', '.join(tech_stack[:8])}" +
                                (f" ... (+{len(tech_stack)-8}项)" if len(tech_stack) > 8 else ""))

                # 项目描述
                description = proj.get("description", "")
                if description:
                    lines.append(f"- **描述**: {description}")

                # 团队规模
                if proj.get("team_size"):
                    lines.append(f"- **团队规模**: {proj['team_size']} 人")

                # 成果
                achievements = proj.get("achievements", [])
                if achievements:
                    lines.append("- **成果**:")
                    for achievement in achievements:
                        lines.append(f"  - {achievement}")

                # 面试问题（Q&A）
                interview_questions = proj.get("interview_questions", [])
                if interview_questions:
                    lines.append("- **💡 面试准备建议**:")
                    for i, qa in enumerate(interview_questions, 1):
                        difficulty = "初级" if i == 1 else "中级" if i == 2 else "高级"
                        lines.append(f"  - **Q{i}: {qa['question']}** ({difficulty})")
                        lines.append(f"    - 参考答案: {qa['answer']}")
                lines.append("")

        # 教育背景
        if "education" in cleaned_resume and cleaned_resume["education"]:
            lines.append("### 🎓 教育背景\n")
            for edu in cleaned_resume["education"]:
                school = edu.get("school", "")
                degree = edu.get("degree", "")
                major = edu.get("major", "")
                start = edu.get("start_time", "")
                end = edu.get("end_time", "")

                lines.append(f"#### {school}")
                lines.append(f"- **学历**: {degree}")
                if major:
                    lines.append(f"- **专业**: {major}")
                if start or end:
                    lines.append(f"- **时间**: {start} ~ {end}")
                lines.append("")

        # 清洗统计
        if "cleaning_stats" in cleaned_resume or "deduplication_stats" in cleaned_resume:
            lines.append("### 📊 数据清洗统计\n")

            cleaning_stats = cleaned_resume.get("cleaning_stats", {})
            if cleaning_stats:
                lines.append("**清洗统计**:")
                lines.append(f"- 处理字段数: {cleaning_stats.get('fields_processed', 0)}")
                lines.append(f"- 缺失值处理: {cleaning_stats.get('missing_values_handled', 0)} 项")
                lines.append("")

            dedup_stats = cleaned_resume.get("deduplication_stats", {})
            if dedup_stats:
                lines.append("**去重统计**:")
                if dedup_stats.get("summary"):
                    summary = dedup_stats["summary"]
                    lines.append(f"- 总处理项数: {summary.get('total_items_processed', 0)}")
                    lines.append(f"- 删除重复项: {summary.get('total_duplicates_removed', 0)}")
                    lines.append(f"- 合并项数: {summary.get('items_merged', 0)}")
                    lines.append("")

                for field in ["skills", "projects", "work_experience"]:
                    field_dedup = dedup_stats.get(field, {})
                    if field_dedup and field_dedup.get("removed", 0) > 0:
                        field_name = {"skills": "技能", "projects": "项目", "work_experience": "工作经历"}[field]
                        lines.append(f"- **{field_name}去重**:")
                        lines.append(f"  - 原始数量: {field_dedup.get('original_count', 0)}")
                        lines.append(f"  - 删除重复: {field_dedup.get('removed', 0)}")
                        if field_dedup.get("merged", 0) > 0:
                            lines.append(f"  - 合并重复: {field_dedup.get('merged', 0)}")
                        lines.append(f"  - 最终数量: {field_dedup.get('final_count', 0)}")
                        lines.append("")

    # ========== 4. 详细分析 ==========
    if "detailed_analysis" in report_data:
        detailed = report_data["detailed_analysis"]
        lines.append("## 📊 各维度详细分析\n")

        dimensions_mapping = {
            "technical": ("技术能力", "🔧"),
            "experience": ("经验背景", "💼"),
            "project": ("项目经验", "📁"),
            "soft_skill": ("软技能", "💡")
        }

        for dim_key, (dim_name, emoji) in dimensions_mapping.items():
            if dim_key in detailed:
                dim_data = detailed[dim_key]
                lines.append(f"### {emoji} {dim_name}\n")

                # 得分和等级
                score = dim_data.get("score", 0)
                level = dim_data.get("level", "未知")
                lines.append(f"**得分**: {score:.1f} 分 / 100")
                lines.append(f"**等级**: {level}\n")

                # 分项得分（如果有）
                raw_analysis = dim_data.get("raw_analysis", {})
                if "detail_scores" in raw_analysis:
                    detail_scores = raw_analysis["detail_scores"]
                    lines.append("**分项得分**:")
                    for key, value in detail_scores.items():
                        if isinstance(value, (int, float)):
                            lines.append(f"- {key}: {value}")
                    lines.append("")

                # 关键发现
                if "key_findings" in dim_data and dim_data["key_findings"]:
                    lines.append("**关键发现**:")
                    for finding in dim_data["key_findings"]:
                        lines.append(f"- {finding}")
                    lines.append("")

                # 优势
                if "strengths" in dim_data and dim_data["strengths"]:
                    lines.append("**✨ 优势**:")
                    for strength in dim_data["strengths"]:
                        lines.append(f"- {strength}")
                    lines.append("")

                # 不足
                if "weaknesses" in dim_data and dim_data["weaknesses"]:
                    lines.append("**📈 待改进**:")
                    for weakness in dim_data["weaknesses"]:
                        lines.append(f"- {weakness}")
                    lines.append("")

                # 项目详细评分（仅project维度）
                if dim_key == "project" and "project_scores" in raw_analysis:
                    project_scores = raw_analysis["project_scores"]
                    if project_scores:
                        lines.append("**📋 项目详细评分**:\n")
                        for proj in project_scores:
                            p_name = proj.get("name", "")
                            p_score = proj.get("score", 0)
                            lines.append(f"**{p_name}** - {p_score}/50分")

                            score_breakdown = proj.get("score_breakdown", {})
                            if score_breakdown:
                                lines.append(f"- 基础分: {score_breakdown.get('基础分', 0)}/10")
                                lines.append(f"- 技术栈分: {score_breakdown.get('技术栈分', 0)}/15")
                                lines.append(f"- 描述质量分: {score_breakdown.get('描述质量分', 0)}/15")
                                lines.append(f"- 规模分: {score_breakdown.get('规模分', 0)}/10")
                            lines.append("")

    # ========== 5. 关键发现汇总 ==========
    if "key_findings" in report_data and report_data["key_findings"]:
        lines.append("## 🔍 关键发现汇总\n")
        for i, finding in enumerate(report_data["key_findings"], 1):
            lines.append(f"{i}. {finding}")
        lines.append("")

    # ========== 6. 优化建议 ==========
    if "optimization_suggestions" in report_data and report_data["optimization_suggestions"]:
        lines.append("## 💡 优化建议\n")

        # 按优先级分组
        high_priority = []
        medium_priority = []
        low_priority = []

        for suggestion in report_data["optimization_suggestions"]:
            priority = suggestion.get("priority", "中")
            if priority == "高":
                high_priority.append(suggestion)
            elif priority == "中":
                medium_priority.append(suggestion)
            else:
                low_priority.append(suggestion)

        # 显示高优先级建议
        if high_priority:
            lines.append("### 🔴 高优先级建议\n")
            for i, suggestion in enumerate(high_priority, 1):
                category = suggestion.get("category", "建议")

                # 新格式
                if suggestion.get("problem_analysis"):
                    lines.append(f"#### {i}. {category}\n")
                    lines.append(f"**🔍 问题**: {suggestion.get('problem_analysis', '')}")

                    action_steps = suggestion.get("action_steps", [])
                    if action_steps:
                        lines.append("**📋 改进步骤**:")
                        for step in action_steps:
                            lines.append(f"- {step}")

                    before_after = suggestion.get("before_after", "")
                    if before_after:
                        lines.append(f"**✨ 改进示例**:\n```\n{before_after}\n```\n")

                    expected = suggestion.get("expected_benefit", "")
                    if expected:
                        lines.append(f"**🎯 预期效果**: {expected}")
                    lines.append("")
                # 旧格式（兼容）
                else:
                    desc = suggestion.get("suggestion", "")
                    lines.append(f"{desc}\n")
                    if "example" in suggestion and suggestion["example"]:
                        example = suggestion["example"]
                        lines.append("**示例**:")
                        if isinstance(example, dict):
                            for key, value in example.items():
                                lines.append(f"- **{key}**: {value}")
                        else:
                            lines.append(f"- {example}")
                        lines.append("")

        # 显示中优先级建议
        if medium_priority:
            lines.append("### 🟡 中优先级建议\n")
            for i, suggestion in enumerate(medium_priority, 1):
                category = suggestion.get("category", "建议")
                desc = suggestion.get("suggestion", "")
                lines.append(f"#### {i}. {category}")
                lines.append(f"{desc}\n")
                if "example" in suggestion and suggestion["example"]:
                    example = suggestion["example"]
                    lines.append("**示例**:")
                    if isinstance(example, dict):
                        for key, value in example.items():
                            lines.append(f"- **{key}**: {value}")
                    else:
                        lines.append(f"- {example}")
                    lines.append("")

        # 显示低优先级建议
        if low_priority:
            lines.append("### 🟢 低优先级建议\n")
            for i, suggestion in enumerate(low_priority, 1):
                category = suggestion.get("category", "建议")
                desc = suggestion.get("suggestion", "")
                lines.append(f"#### {i}. {category}")
                lines.append(f"{desc}\n")

    # ========== 7. 岗位匹配分析 ==========
    if "job_match_analysis" in report_data and report_data["job_match_analysis"]:
        job_match = report_data["job_match_analysis"]
        if job_match:
            lines.append("## 🎯 岗位匹配分析\n")

            if isinstance(job_match, dict):
                # 匹配分数和等级
                match_score = job_match.get("match_score", 0)
                match_level = job_match.get("match_level", "")
                lines.append(f"**匹配分数**: {match_score} 分")
                lines.append(f"**匹配等级**: {match_level}\n")

                # 技能分析
                if "skill_analysis" in job_match:
                    skill_analysis = job_match["skill_analysis"]
                    lines.append("**技能匹配**:")
                    lines.append(f"- 技能覆盖率: {skill_analysis.get('skill_coverage', 0)}%")

                    if skill_analysis.get("matched_skills"):
                        lines.append(f"- 匹配技能: {', '.join(skill_analysis['matched_skills'][:5])}")

                    if skill_analysis.get("missing_skills"):
                        lines.append(f"- 缺失技能: {', '.join(skill_analysis['missing_skills'][:5])}")
                    lines.append("")

                # 优势和不足
                if job_match.get("strengths"):
                    lines.append("**✅ 优势**:")
                    for strength in job_match["strengths"]:
                        lines.append(f"- {strength}")
                    lines.append("")

                if job_match.get("weaknesses"):
                    lines.append("**⚠️ 不足**:")
                    for weakness in job_match["weaknesses"]:
                        lines.append(f"- {weakness}")
                    lines.append("")

                # 总结
                if job_match.get("summary"):
                    lines.append(f"**总结**: {job_match['summary']}")
            else:
                lines.append(f"{job_match}")
            lines.append("")

    # ========== 8. 数据处理过程 ==========
    if "processing_summary" in report_data and report_data["processing_summary"]:
        processing = report_data["processing_summary"]
        lines.append("## ⚙️ 数据处理过程\n")

        # 步骤执行情况
        steps_completed = processing.get("steps_completed", [])
        steps_failed = processing.get("steps_failed", [])

        if steps_completed:
            lines.append(f"**完成步骤**: {', '.join(steps_completed)}")

        if steps_failed:
            lines.append(f"**失败步骤**: {', '.join(steps_failed)}")
        lines.append("")

        # 各步骤详情
        if "steps_summary" in processing:
            step_name_map = {
                "parsed": "📄 简历解析",
                "structured": "🔧 结构映射",
                "cleaned": "🧹 数据清洗",
                "deduplicated": "🔄 数据去重"
            }

            lines.append("**处理步骤详情**:\n")
            for step in processing["steps_summary"]:
                step_name = step.get("step", "")
                display_name = step_name_map.get(step_name, step_name)
                lines.append(f"**{display_name}**")

                if step_name == "parsed":
                    lines.append(f"- 解析方法: {step.get('parse_method', 'unknown')}")
                    lines.append(f"- 识别字段数: {step.get('fields_count', 0)}")

                elif step_name == "deduplicated" and step.get("deduplication_performed"):
                    dedup_sum = step.get("deduplication_summary", {})
                    lines.append(f"- 处理项数: {dedup_sum.get('total_items_processed', 0)}")
                    lines.append(f"- 删除重复: {dedup_sum.get('total_duplicates_removed', 0)} 项")
                    lines.append(f"- 合并项数: {dedup_sum.get('items_merged', 0)} 项")

                lines.append("")

    # ========== 9. 元数据 ==========
    if "metadata" in report_data:
        metadata = report_data["metadata"]
        lines.append("---\n")
        lines.append("## 📝 报告元数据\n")

        if metadata.get("generated_at"):
            lines.append(f"**生成时间**: {metadata['generated_at']}\n")

        if metadata.get("report_version"):
            lines.append(f"**报告版本**: {metadata['report_version']}\n")

        if metadata.get("generator"):
            lines.append(f"**生成工具**: {metadata['generator']}\n")

        if metadata.get("candidate_name"):
            lines.append(f"**候选人**: {metadata['candidate_name']}\n")

        if metadata.get("job_requirements") and metadata["job_requirements"] != "未提供特定岗位要求":
            lines.append(f"**岗位要求**: {metadata['job_requirements']}\n")

        if metadata.get("parse_info"):
            parse_info = metadata["parse_info"]
            lines.append("**解析信息**:")
            lines.append(f"- 解析方法: {parse_info.get('parse_method', 'unknown')}")
            lines.append(f"- 识别字段数: {parse_info.get('fields_count', 0)}")

    return "\n".join(lines)


def get_report_type_name(report_type: str) -> str:
    """获取报告类型的中文名称"""
    mapping = {
        "full": "完整报告",
        "hr_summary": "HR摘要",
        "candidate_summary": "求职者摘要"
    }
    return mapping.get(report_type, report_type)


def get_score_color(score: float) -> str:
    """根据分数获取颜色emoji"""
    if score >= 90:
        return "🟢 优秀"
    elif score >= 80:
        return "🟡 良好"
    elif score >= 70:
        return "🟠 合格"
    elif score >= 60:
        return "🟡 及格"
    else:
        return "🔴 不及格"


def generate_html_report(state: dict, report_data: dict) -> str:
    """生成HTML格式的报告"""
    # 使用ReportAgent的to_html方法
    llm = get_llm()
    report_agent = ReportAgent(llm=llm, verbose=False)

    # 如果report_data已经是完整的report对象，直接使用
    # 否则从state构建完整的report
    if "executive_summary" in report_data and "detailed_analysis" in report_data:
        # report_data已经是完整的report
        report = report_data
    else:
        # 需要从state和report_data构建完整report
        report = {
            "executive_summary": {
                "candidate_name": state.get("resume_data", {}).get("personal_info", {}).get("name", ""),
                "total_score": state.get("total_score", 0),
                "score_level": get_score_level_text(state.get("total_score", 0)),
                "contact": state.get("resume_data", {}).get("personal_info", {}),
                "quick_overview": state.get("score_breakdown", {})
            },
            "cleaned_resume": {
                "personal_info": state.get("resume_data", {}).get("personal_info", {}),
                "skills": state.get("resume_data", {}).get("skills", []),
                "work_experience": state.get("resume_data", {}).get("work_experience", []),
                "projects": state.get("resume_data", {}).get("projects", []),
                "education": state.get("resume_data", {}).get("education", [])
            },
            "processing_summary": state.get("processing_info", {}),
            "detailed_analysis": {
                "technical": report_data.get("technical_analysis", {}),
                "experience": report_data.get("experience_analysis", {}),
                "project": report_data.get("project_analysis", {}),
                "soft_skill": report_data.get("soft_skill_analysis", {})
            },
            "key_findings": [],
            "optimization_suggestions": state.get("optimization_suggestions", []),
            "job_match_analysis": state.get("job_match_analysis"),
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "job_requirements": state.get("job_requirements", "")
            }
        }

    return report_agent.to_html(report)


def get_score_level_text(score: float) -> str:
    """根据分数获取等级文本"""
    if score >= 90:
        return "**优秀** - 综合能力非常强，完全符合要求"
    elif score >= 80:
        return "**良好** - 综合能力较强，基本符合要求"
    elif score >= 70:
        return "**合格** - 综合能力一般，部分符合要求"
    elif score >= 60:
        return "**及格** - 综合能力较弱，勉强符合要求"
    else:
        return "**不及格** - 综合能力不足，不符合要求"


if __name__ == "__main__":
    main()
