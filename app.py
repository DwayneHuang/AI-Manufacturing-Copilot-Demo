"""
AI Manufacturing Copilot Demo
智能制造 Copilot — Streamlit 主入口（左侧 ERP Dashboard，右侧飞书 AI 聊天界面）
"""
import os  # 读取环境变量（如 GOOGLE_API_KEY）
import copy  # 深拷贝 mock 数据，避免直接污染原始常量
import streamlit as st  # Streamlit Web 框架

# ── 页面配置(必须作为第一个 Streamlit 命令) ──
st.set_page_config(
    page_title="AI ERP Copilot",  # 浏览器标签页标题
    page_icon="🏭",  # 浏览器标签页图标
    layout="wide",  # 宽屏布局，适合左右双栏 Dashboard + 聊天区
    initial_sidebar_state="expanded",  # 启动时默认展开左侧边栏
)

# ── 全局 CSS ──
from ui.styles import MAIN_CSS  # 导入自定义样式字符串
st.markdown(MAIN_CSS, unsafe_allow_html=True)  # 注入全局 CSS（必须开启 unsafe_allow_html=True）

# ── 初始化 Session State (共享数据源) ──
from data.mock_data import PRODUCTS, MATERIALS, BOM, INVENTORY, SUPPLIERS, PRODUCTION_PLAN  # 导入默认模拟数据
from data.store import get_store  # 导入数据仓库单例获取函数


def init_session_state():
    """首次加载时，将 Mock 数据深拷贝到 session_state"""
    defaults = {
        "products": PRODUCTS,  # 产品列表
        "materials": MATERIALS,  # 物料主数据
        "bom": BOM,  # 物料清单（BOM）结构
        "inventory": INVENTORY,  # 库存明细
        "suppliers": SUPPLIERS,  # 供应商信息
        "production_plan": PRODUCTION_PLAN,  # 生产计划
        "purchase_drafts": [],  # 采购申请草案列表（初始为空）
    }
    for key, value in defaults.items():  # 遍历默认键值
        if key not in st.session_state:  # 仅在当前会话尚未初始化时写入，避免每次 rerun 覆盖用户修改
            st.session_state[key] = copy.deepcopy(value)  # 深拷贝防止嵌套字典/列表被引用修改


init_session_state()  # 执行会话状态初始化

# ── 侧边栏：系统状态与说明 ──
with st.sidebar:  # 进入侧边栏上下文
    st.markdown("### AI ERP Copilot 架构")  # 侧边栏主标题
    st.caption("模拟 AI Agent × ERP API × 飞书集成")  # 架构副标题说明

    # 检测 LLM 状态
    has_gemini_key = False  # 默认未检测到 Gemini API Key
    if os.environ.get("GOOGLE_API_KEY"):  # 先检查系统环境变量
        has_gemini_key = True  # 找到环境变量则标记为可用
    else:
        try:
            if hasattr(st, "secrets") and "GOOGLE_API_KEY" in st.secrets:  # 再检查 Streamlit secrets 配置
                has_gemini_key = True  # 找到 secrets 配置则标记为可用
        except Exception:  # 本地无 secrets.toml 时可能抛异常，安全忽略
            pass

    if has_gemini_key:  # 已配置 Key：展示大模型模式状态
        st.success("**LLM 引擎**: Gemini 2.0 Flash (Function Calling 激活)")
    else:  # 未配置 Key：降级为确定性规则引擎模式
        st.info("**Agent 模式**: 确定性规则引擎 (离线零配置模式)\n\n*(配置 GOOGLE_API_KEY 即可切换为 Gemini 大模型)*")

    #st.markdown("---")  # 分隔线
    st.markdown("#### 核心特性矩阵:")  # 特性说明小标题
    st.markdown("""
- **确定性 ERP Tools**: BOM展开/库存/缺口/采购建议全部由 FastAPI / Python 函数精确计算，防止 AI 幻觉。
- **飞书工作台体验**: 右侧完整模拟飞书工作助理交互场景。
- **人工审批闭环**: 重要流程如采购仅生成草案，必须由人工在界面或对话中二次确认。
- **双向数据同步**: Dashboard 与聊天框共享同一后端，任意一端修改即时互通。
    """)  # 渲染核心能力列表

    #st.markdown("---")  # 分隔线
    st.markdown("#### 演示控制台:")  # 控制台操作区标题
    if st.button("🔄 重置演示数据", width="stretch", type="secondary"):  # 已修正：use_container_width=True -> width="stretch"（撑满容器宽度）
        store = get_store()  # 获取底层数据存储实例
        store.reset_to_defaults()  # 将 ERP 数据重置为默认初始值
        if "chat_messages" in st.session_state:  # 若聊天记录已存在，同步重置欢迎语
            from ui.styles import WELCOME_MESSAGE  # 导入欢迎语模板
            from ui.chat import _now  # 导入时间戳辅助函数
            st.session_state.chat_messages = [
                {"role": "assistant", "content": WELCOME_MESSAGE, "time": _now()}  # 重置为初始欢迎消息
            ]
        st.success("数据已恢复初始状态！")  # 提示重置成功
        st.rerun()  # 立即重新运行脚本，刷新页面视图

    if st.button("🧹 清空聊天记录", width="stretch"):  # 已修正：use_container_width=True -> width="stretch"
        from ui.styles import WELCOME_MESSAGE  # 导入欢迎语模板
        from ui.chat import _now  # 导入时间戳辅助函数
        st.session_state.chat_messages = [
            {"role": "assistant", "content": WELCOME_MESSAGE, "time": _now()}  # 清空历史并保留首条欢迎消息
        ]
        st.rerun()  # 立即刷新页面，显示清空后的聊天区

    st.markdown("---")  # 分隔线
    #st.caption("🚀 支持一键部署至 Streamlit Cloud\n\n📌 
    st.caption("独立 FastAPI 服务可通过 `python run_api.py` 启动")  # 部署与后端启动提示


# ── 页面顶部 Header ──
with st.container(key="main_header"):
    col_head1, col_head2 = st.columns([3, 1])  # 顶部拆分为 4:1 两列（左标题说明，右同步状态徽章）
    with col_head1:  # 左侧主标题区
        st.markdown(
            """
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:0px;">
                <span style="font-size:32px;"></span>
                <div>
                    <h2 style="margin:0; color:#1F2329; font-size:20px; line-height: 0.5;">AI ERP Copilot</h2>
                    <p style="margin:0; color:#646A73; font-size:12px;">
                        面向制造业的智能生产与采购协同助手 — 基于 Agent 与 ERP API，构建飞书式聊天与 GUI 双交互的 AI 助手，实现业务查询、数据联动及采购审批。
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,  # 允许渲染自定义 HTML 头部结构
        )
    with col_head2:  # 右侧实时同步状态标签区
        st.markdown(
            """
            <div style="text-align:right; padding-top:8px;">
                <span style="background:#E8F3FF; color:#165DFF; font-size:12px; font-weight:600; padding:4px 8px; border-radius:4px;">
                    ● 数据双向实时同步中
                </span>
            </div>
            """,
            unsafe_allow_html=True,  # 允许渲染胶囊状态标签 HTML
        )

#st.markdown("---")  # 顶部 Header 与主内容区之间的分割线

# ── 左右分栏核心布局 (3:2 黄金比例) ──
from ui.dashboard import render_dashboard  # 导入左侧 ERP Dashboard 渲染函数
from ui.chat import render_chat  # 导入右侧飞书风格 AI 聊天框渲染函数

col_left, col_right = st.columns([3, 2], gap= 20)  # 按 3:2 比例创建左右主列，列间距设为 large

with col_left:  # 左侧栏渲染 ERP 看板
    with st.container(border=True, key="dashboard_frame"):
        render_dashboard()

with col_right:  # 右侧栏渲染 AI 对话助手
    with st.container(border=True, key="chat_frame"):
        render_chat()

# ── 底部状态 ──
st.markdown("---")  # 主内容区与底部说明之间的分割线
with st.container(key="main_caption"):
    st.caption(
        "* **系统说明**: 本系统采用双向数据同步架构，左侧 Dashboard 与右侧 AI 聊天助手完全共享底层 ERP 数据仓库。"
        "在任意一侧进行库存更新、排产调整、采购草案生成及审批，均会毫秒级联动刷新全局计算结果。"
    )  # 底部架构联动说明