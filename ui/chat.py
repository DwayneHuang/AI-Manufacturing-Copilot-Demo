"""
Chat UI — 右侧飞书风格聊天面板
模拟飞书聊天交互，作为 AI Agent 的自然语言入口
"""
import streamlit as st  # Streamlit Web 框架
from datetime import datetime  # 用于生成消息发送时间戳
from ui.styles import FEISHU_HEADER_HTML, WELCOME_MESSAGE  # 导入飞书头部 HTML 与默认欢迎语
from agent.copilot import CopilotAgent  # 导入 AI 助手核心类


def _now() -> str:
    """获取当前时间字符串（HH:MM 格式）"""
    return datetime.now().strftime("%H:%M")  # 格式化为小时:分钟


def render_chat():
    """渲染右侧飞书聊天面板"""
    # ── 飞书风格头部 ──
    st.markdown(FEISHU_HEADER_HTML, unsafe_allow_html=True)  # 渲染顶部蓝紫渐变头部与机器人图标/标题

    # ── 初始化聊天记录 ──
    if "chat_messages" not in st.session_state:  # 首次进入会话时初始化历史消息列表
        st.session_state.chat_messages = [
            {"role": "assistant", "content": WELCOME_MESSAGE, "time": _now()}  # 默认放入一条助手欢迎语
        ]

    if "copilot" not in st.session_state:  # 首次进入时实例化 CopilotAgent 并存入 session_state 保持跨 rerun 状态
        st.session_state.copilot = CopilotAgent()

    # ── 快捷操作按钮 ──
    _render_quick_actions()  # 渲染 4 个高频指令快捷按钮

    # ── 聊天消息区 ──
    chat_container = st.container(height=400, key="feishu_chat_area")  # 创建固定高度 400px 的可滚动聊天容器（想改聊天框高度可调 height）
    with chat_container:  # 在滚动容器内渲染所有历史消息
        for msg in st.session_state.chat_messages:  # 遍历消息列表
            avatar = "⚙️" if msg["role"] == "assistant" else "👤"  # 按发送角色选择头像
            with st.chat_message(msg["role"], avatar=avatar):  # 渲染单条聊天气泡
                st.markdown(msg["content"])  # 渲染消息正文（支持 Markdown 表格、列表、加粗等）
                if msg.get("time"):  # 若存在时间戳则显示发送时间
                    st.caption(f"发送于 {msg['time']}")

    # ── 底部输入区 ──
    user_input = st.chat_input("输入业务指令... 例如：查看智能手表的BOM / 分析物料缺口", height=60, key="chat_input")  # 底部聊天输入框
    if user_input:  # 用户提交非空文本后触发处理流程
        _handle_user_input(user_input)


def _render_quick_actions():
    """快捷操作按钮行"""
    cols = st.columns(4)  # 将快捷按钮区均分为 4 列
    quick_actions = [  # 定义快捷按钮：(按钮显示文案, 点击后发送的自然语言指令)
        ("📋 查BOM", "查看智能手表X1 Pro的BOM清单"),
        ("📦 查库存", "查询当前所有物料库存总览"),
        ("⚠️ 算缺口", "分析当前生产计划下的物料缺口"),
        ("🛒 提采购", "创建采购申请草案"),
    ]
    for col, (label, query) in zip(cols, quick_actions):  # 将每个按钮绑定到对应列
        with col:
            if st.button(label, key=f"quick_{label}", width="stretch"):  # 已修正废弃参数：use_container_width=True -> width="stretch"
                _handle_user_input(query)  # 点击后直接走统一输入处理逻辑


def _handle_user_input(user_input: str):
    """处理用户输入，调用 Copilot Agent 并刷新界面"""
    st.session_state.chat_messages.append({  # 追加用户刚发送的消息到历史记录
        "role": "user",
        "content": user_input,
        "time": _now(),
    })

    history = [  # 提取不包含刚追加这条消息的历史上下文，传给 Agent
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.chat_messages[:-1]
    ]

    copilot: CopilotAgent = st.session_state.copilot  # 取出当前会话的 Agent 实例
    with st.spinner("AI 正在调用 ERP 确定性计算引擎..."):  # 推理与工具调用期间显示加载提示
        reply = copilot.chat(user_input, history)  # 调用 Agent 获取回复

    st.session_state.chat_messages.append({  # 将助手回复追加进聊天记录
        "role": "assistant",
        "content": reply,
        "time": _now(),
    })
    st.rerun()  # 立即重新运行脚本，让最新消息出现在聊天容器中