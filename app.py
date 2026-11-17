"""
AI Manufacturing Copilot Demo
智能制造 Copilot — Streamlit 主入口

左侧: ERP Dashboard (BOM / 库存 / 物料缺口 / 采购管理)
右侧: 飞书风格 AI Agent 聊天界面
"""
import os
import copy
import streamlit as st

# ── 页面配置(必须作为第一个 Streamlit 命令) ──
st.set_page_config(
    page_title="智造 Copilot · AI Manufacturing",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 全局 CSS ──
from ui.styles import MAIN_CSS
st.markdown(MAIN_CSS, unsafe_allow_html=True)

# ── 初始化 Session State (共享数据源) ──
from data.mock_data import PRODUCTS, MATERIALS, BOM, INVENTORY, SUPPLIERS, PRODUCTION_PLAN
from data.store import get_store


def init_session_state():
    """首次加载时，将 Mock 数据深拷贝到 session_state"""
    defaults = {
        "products": PRODUCTS,
        "materials": MATERIALS,
        "bom": BOM,
        "inventory": INVENTORY,
        "suppliers": SUPPLIERS,
        "production_plan": PRODUCTION_PLAN,
        "purchase_drafts": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = copy.deepcopy(value)


init_session_state()

# ── 侧边栏：系统状态与说明 ──
with st.sidebar:
    st.markdown("### 🏭 智造 Copilot 架构")
    st.caption("AI Agent × 确定性 ERP 核心计算 × 飞书集成")

    # 检测 LLM 状态
    has_gemini_key = False
    if os.environ.get("GOOGLE_API_KEY"):
        has_gemini_key = True
    else:
        try:
            if hasattr(st, "secrets") and "GOOGLE_API_KEY" in st.secrets:
                has_gemini_key = True
        except Exception:
            pass

    if has_gemini_key:
        st.success("🤖 **LLM 引擎**: Gemini 2.0 Flash (Function Calling 激活)")
    else:
        st.info("⚡ **Agent 模式**: 确定性规则引擎 (离线零配置模式)\n\n*(配置 GOOGLE_API_KEY 即可切换为 Gemini 大模型)*")

    st.markdown("---")
    st.markdown("#### 📐 核心特性矩阵")
    st.markdown("""
- **确定性 ERP Tools**: BOM展开/库存/缺口/采购建议全部由 FastAPI / Python 函数精确计算。
- **飞书工作台体验**: 右侧完整模拟飞书工作助理交互场景。
- **人工审批闭环**: 采购仅生成草案，必须由人工在界面或对话中核准。
- **双向数据同步**: Dashboard 与聊天框共享同一后端，任意一端修改即时互通。
    """)

    st.markdown("---")
    st.markdown("#### ⚙️ 演示控制台")
    if st.button("🔄 重置所有演示数据", use_container_width=True, type="secondary"):
        store = get_store()
        store.reset_to_defaults()
        if "chat_messages" in st.session_state:
            from ui.styles import WELCOME_MESSAGE
            from ui.chat import _now
            st.session_state.chat_messages = [
                {"role": "assistant", "content": WELCOME_MESSAGE, "time": _now()}
            ]
        st.success("数据已恢复初始状态！")
        st.rerun()

    if st.button("🧹 清空聊天记录", use_container_width=True):
        from ui.styles import WELCOME_MESSAGE
        from ui.chat import _now
        st.session_state.chat_messages = [
            {"role": "assistant", "content": WELCOME_MESSAGE, "time": _now()}
        ]
        st.rerun()

    st.markdown("---")
    st.caption("🚀 支持一键部署至 Streamlit Cloud\n\n📌 独立 FastAPI 服务可通过 `python run_api.py` 启动")


# ── 页面顶部 Header ──
col_head1, col_head2 = st.columns([4, 1])
with col_head1:
    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:4px;">
            <span style="font-size:32px;">🏭</span>
            <div>
                <h2 style="margin:0; color:#1F2329;">AI Manufacturing Copilot</h2>
                <p style="margin:0; color:#646A73; font-size:14px;">
                    面向制造业的智能生产与采购协同助手 — ERP 确定性计算引擎 × 飞书交互 × 人工审批闭环
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col_head2:
    st.markdown(
        """
        <div style="text-align:right; padding-top:8px;">
            <span style="background:#E8F3FF; color:#165DFF; font-size:12px; font-weight:600; padding:4px 8px; border-radius:4px;">
                ● 双向实时同步中
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── 左右分栏核心布局 (3:2 黄金比例) ──
from ui.dashboard import render_dashboard
from ui.chat import render_chat

col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    render_dashboard()

with col_right:
    render_chat()

# ── 底部状态 ──
st.markdown("---")
st.caption(
    "💡 **系统说明**: 本系统采用双向数据同步架构，左侧 Dashboard 与右侧飞书 AI 助手完全共享底层 ERP 数据仓库。"
    "在任意一侧进行库存更新、排产调整、采购草案生成及审批，均会毫秒级联动刷新全局计算结果。"
)
