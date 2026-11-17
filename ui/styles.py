"""
UI Styles — 全局 CSS 样式
"""

MAIN_CSS = """
<style>
/* ── 全局布局 ── */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
}
header[data-testid="stHeader"] {
    background: linear-gradient(90deg, #3370FF 0%, #2B5CE6 100%);
}

/* ── Dashboard 卡片 ── */
div[data-testid="stMetric"] {
    background: #F7F8FA;
    border: 1px solid #E5E6EB;
    border-radius: 10px;
    padding: 12px 16px;
}
div[data-testid="stMetric"] label {
    color: #646A73;
}

/* ── 状态标签 ── */
.status-ok      { color: #00B42A; font-weight: 600; }
.status-warning  { color: #FF7D00; font-weight: 600; }
.status-danger   { color: #F53F3F; font-weight: 600; }
.status-pending  { color: #3370FF; font-weight: 600; }
.status-approved { color: #00B42A; font-weight: 600; }
.status-rejected { color: #F53F3F; font-weight: 600; }

/* ── 飞书聊天面板 ── */
.feishu-header {
    background: linear-gradient(135deg, #3370FF 0%, #2B5CE6 100%);
    color: white;
    padding: 14px 20px;
    border-radius: 12px 12px 0 0;
    margin-bottom: 0;
    display: flex;
    align-items: center;
    gap: 10px;
}
.feishu-header .title {
    font-size: 16px;
    font-weight: 600;
}
.feishu-header .subtitle {
    font-size: 12px;
    opacity: 0.85;
}
.feishu-chat-area {
    background: #F5F6F7;
    border: 1px solid #E5E6EB;
    border-top: none;
    border-radius: 0 0 12px 12px;
    padding: 8px 0;
    min-height: 300px;
}

/* ── 分隔线样式 ── */
.divider-vertical {
    border-left: 2px solid #E5E6EB;
    height: 100%;
    margin: 0 8px;
}

/* ── 快捷操作按钮 ── */
.quick-action-row {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin-bottom: 8px;
}

/* ── 审批卡片 ── */
.approval-card {
    background: white;
    border: 1px solid #E5E6EB;
    border-left: 4px solid #3370FF;
    border-radius: 8px;
    padding: 14px 16px;
    margin: 8px 0;
}
.approval-card.approved {
    border-left-color: #00B42A;
}
.approval-card.rejected {
    border-left-color: #F53F3F;
}

/* ── 表格优化 ── */
.stDataFrame { border-radius: 8px; overflow: hidden; }

/* ── 隐藏 Streamlit 默认元素 ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* ── 侧边分割线 ── */
[data-testid="column"]:first-child {
    border-right: 2px solid #E5E6EB;
    padding-right: 16px !important;
}
</style>
"""

FEISHU_HEADER_HTML = """
<div class="feishu-header">
    <div>
        <div style="font-size: 28px;">🤖</div>
    </div>
    <div>
        <div class="title">智造 Copilot · 飞书助手</div>
        <div class="subtitle">AI Manufacturing Agent — 自然语言查询与操作 ERP</div>
    </div>
</div>
"""

WELCOME_MESSAGE = """👋 你好！我是 **智造 Copilot**，你的 AI 制造业助手。

我可以帮你完成以下操作：

| 功能 | 示例指令 |
|------|---------|
| 📋 BOM 查询 | "查看智能手表的物料清单" |
| 📦 库存查询 | "当前库存情况如何？" |
| ⚠️ 缺口分析 | "分析物料缺口" |
| 🛒 采购建议 | "生成采购建议" |
| ✏️ 修改数据 | "把M001库存改为500" |
| 📊 生产计划 | "查看生产计划" |
| 📝 采购申请 | "创建采购申请单" |

直接用自然语言告诉我你需要什么吧！"""
