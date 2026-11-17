"""
Chat UI — 右侧飞书风格聊天面板
模拟飞书聊天交互，作为 AI Agent 的自然语言入口
"""
import streamlit as st
from datetime import datetime
from ui.styles import FEISHU_HEADER_HTML, WELCOME_MESSAGE
from agent.copilot import CopilotAgent


def _now() -> str:
    """获取当前时间字符串"""
    return datetime.now().strftime("%H:%M")


def render_chat():
    """渲染右侧飞书聊天面板"""
    # ── 飞书风格头部 ──
    st.markdown(FEISHU_HEADER_HTML, unsafe_allow_html=True)

    # ── 初始化聊天记录 ──
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": WELCOME_MESSAGE, "time": _now()}
        ]

    if "copilot" not in st.session_state:
        st.session_state.copilot = CopilotAgent()

    # ── 快捷操作按钮 ──
    _render_quick_actions()

    # ── 聊天消息区 ──
    chat_container = st.container(height=480)
    with chat_container:
        for msg in st.session_state.chat_messages:
            avatar = "🤖" if msg["role"] == "assistant" else "👤"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])
                if msg.get("time"):
                    st.caption(f"发送于 {msg['time']}")

    # ── 底部输入区 ──
    user_input = st.chat_input("输入业务指令... 例如：查看智能手表的BOM / 分析物料缺口", key="chat_input")
    if user_input:
        _handle_user_input(user_input)


def _render_quick_actions():
    """快捷操作按钮行"""
    cols = st.columns(4)
    quick_actions = [
        ("📋 查BOM", "查看智能手表X1 Pro的BOM清单"),
        ("📦 查库存", "查询当前所有物料库存总览"),
        ("⚠️ 算缺口", "分析当前生产计划下的物料缺口"),
        ("🛒 提采购", "创建采购申请草案"),
    ]
    for col, (label, query) in zip(cols, quick_actions):
        with col:
            if st.button(label, key=f"quick_{label}", use_container_width=True):
                _handle_user_input(query)


def _handle_user_input(user_input: str):
    """处理用户输入，调用 Copilot Agent 并刷新界面"""
    st.session_state.chat_messages.append({
        "role": "user",
        "content": user_input,
        "time": _now(),
    })

    history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.chat_messages[:-1]
    ]

    copilot: CopilotAgent = st.session_state.copilot
    with st.spinner("AI 正在调用 ERP 确定性计算引擎..."):
        reply = copilot.chat(user_input, history)

    st.session_state.chat_messages.append({
        "role": "assistant",
        "content": reply,
        "time": _now(),
    })
    st.rerun()
