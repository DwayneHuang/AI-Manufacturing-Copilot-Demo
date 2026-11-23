"""
UI Styles — 全局 CSS 样式（用于 Streamlit 界面美化与组件模板定义）
"""

MAIN_CSS = """
<style>
/* 顶部 Toolbar */
[data-testid="stHeader"] {
    height: 40px;
    min-height: 40px;
}

/* ── 全局布局 ── */
.block-container {
    padding-top: 1rem !important;      /* 调整页面顶部内边距；想留白更多可改大如 2rem */
    padding-bottom: 1rem !important;   /* 调整页面底部内边距 */
}
/* header[data-testid="stHeader"] { */
/*    background: linear-gradient(90deg, #3370FF 0%, #2B5CE6 100%); */
                                       /* Streamlit 顶部工具栏渐变色（飞书蓝系）；改色换 hex 值即可 */
/* } */

----------------------------------------------------
/* Sidebar */
/* ── 侧边栏整体容器 ── */
section[data-testid="stSidebar"] {
    /*width: 300px !important;*/              /* 侧边栏宽度；想改宽/窄就调这个值 */
    /*min-width: 260px !important;*/          /* 最小宽度 */
    background-color: #F7F8FA !important; /* 侧边栏背景色 */
    border-right: 1px solid #E5E6EB !important; /* 右侧边框线 */
}

/* ── 侧边栏内部内容区域边距与间距 ── */
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    padding: 0px 12px !important;        /* 侧边栏内边距 */
}

/* 侧边栏内部纵向块之间的间距（gap） */
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 4px !important;                  /* 调整侧边栏各项之间的垂直空隙 */
}

/* 侧边栏标题与说明文字微调 */
section[data-testid="stSidebar"] h3 {
    font-size: 16px !important;
    margin-bottom: 4px !important;
}

section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    font-size: 12px !important;
    line-height: 1.4 !important;
}

/* 侧边栏 info 提示框样式 */
section[data-testid="stSidebar"] div[data-testid="stAlert"] {
    border-radius: 8px !important;      /* 圆角 */
    padding: 0px 0px !important;       /* 内边距 */
}

/* info 框内部文字大小与行距 */
section[data-testid="stSidebar"] div[data-testid="stAlert"] p,
section[data-testid="stSidebar"] div[data-testid="stAlert"] span {
    font-size: 12px !important;         /* 文字大小 */
    line-height: 1.4 !important;        /* 行高 */
}

/* info 框左侧图标大小 */
section[data-testid="stSidebar"] div[data-testid="stAlert"] svg {
    width: 12px !important;
    height: 12px !important;
}

section[data-testid="stSidebar"] h4, 
section[data-testid="stSidebar"] li,
section[data-testid="stSidebar"] p {
    font-size: 12px !important;
}

/* 侧边栏按钮圆角与大小 */
section[data-testid="stSidebar"] .stButton button {
    border-radius: 12px !important;      /* 按钮圆角；改 0px 为直角，改大更圆润 */
    min-height: 24px !important;        /* 按钮高度；想改矮或改高就调这里 */
    height: 24px !important;            /* 固定高度，避免默认高度撑开 */
    /* padding: 0px 0px !important;*/       /* 上下 / 左右内边距，影响按钮大小与松紧 */
    font-size: 12px !important;         /* 按钮文字大小 */
}


----------------------------------------------------

/* ── 状态标签 ── */
.status-ok      { color: #00B42A; font-weight: 600; } /* 正常/通过状态：绿色加粗 */
.status-warning  { color: #FF7D00; font-weight: 600; } /* 警告/缺口提示：橙色加粗 */
.status-danger   { color: #F53F3F; font-weight: 600; } /* 危险/严重短缺：红色加粗 */
.status-pending  { color: #3370FF; font-weight: 600; } /* 待处理/审批中：蓝色加粗 */
.status-approved { color: #00B42A; font-weight: 600; } /* 已批准：绿色加粗 */
.status-rejected { color: #F53F3F; font-weight: 600; } /* 已驳回：红色加粗 */

----------------------------------------------------

/* 快捷按钮本身的外观与大小 */
[class*="st-key-quick_"] .stButton button {
    border: 1px solid #E5E6EB;
}
[class*="st-key-quick_"] .stButton button p {
    border-radius: 12px !important;      /* 圆角大小 */
    padding: 0px 0px !important;        /* 上下 / 左右内边距，防止 emoji + 文字换行 */
    font-size: 12px !important;         /* 按钮文字大小 */
    color: #1F2329 !important;           /* 文字颜色 */
    line-height: 1.4 !important;         /* 行高 */
}

.st-key-feishu_chat_area {
    background: #F7F8FA;               /* 聊天记录区底色（浅灰） */
    border: 1px solid #E5E6EB;         /* 边框颜色 */
    border-radius: 0 0 12px 12px;      /* 仅左下、右下圆角 */
    padding: 0px 0px;                    /* 上下 8px 内边距，左右由内部组件控制 */
    min-height: 300px;                 /* 最小高度 300px；消息少时保持面板高度，可改大如 500px */
}
.st-key-feishu_chat_area div {
    font-size: 12px !important;
    line-height: 1.2 !important;
}

.st-key-chat_input textarea {
    font-size: 12px !important;
}

----------------------------------------------------
/* ── render_dashboard() 内 st.tabs 字体大小（不使用 [data-baseweb="tab"]） ── */
.st-key-dashboard_frame [data-testid="stTab"],
.st-key-dashboard_frame [data-testid="stTab"] * {
    font-size: 12px !important;   /* 改成你想要的字号 */
    line-height: 1 !important;
}

.st-key-production_plan h4 span,
.st-key-bom h4 span,
.st-key-inventory h4 span,
.st-key-gaps h4 span,
.st-key-procurement h4 span {
    font-size: 16px !important;
}

.st-key-production_plan div,
.st-key-bom div,
.st-key-inventory div,
.st-key-gaps div,
.st-key-procurement div,
.st-key-procurement div span {
    font-size: 12px !important;
    line-height: 1.5 !important;
}

/* ── all selectbox 上方标签、当前选中与下拉框文字字号 ── */
[data-testid="stSelectbox"] label p,
[data-testid="stSelectbox"] input,
[data-testid="stSelectboxVirtualDropdown"] div {
    font-size: 12px !important;   /* 按需调整 */
}

.st-key-dash_plan_qty input,
.st-key-inventory input {
    font-size: 12px !important;
}

/* ── “更新计划”主按钮样式 ── */
.st-key-dash_plan_update button,
.st-key-dash_plan_update button p,
.st-key-dash_inv_update button,
.st-key-dash_inv_update button p,
.st-key-dash_create_po button,
.st-key-dash_create_po button p {
    border-radius: 12px !important;      /* 按钮圆角 */
    font-size: 12px !important;         /* 按钮文字大小 */
    /*white-space: nowrap !important;*/     /* 防止按钮文字换行 */
    line-height: 1.2 !important;
}

/* ── 让按钮在所在 column 容器中自动顶到最底部 ── */
.st-key-dash_plan_update,
.st-key-dash_inv_update,
.st-key-dash_create_po {
    margin-top: auto !important;
}
----------------------------------------------------

/* ── 分隔线样式 ── */
.divider-vertical {
    border-left: 2px solid #E5E6EB;    /* 竖向分割线（需在 HTML 中手动调用该 class） */
    height: 100%;                      /* 占满父容器高度 */
    margin: 0 8px;                     /* 左右外边距各 8px */
}

/* ── 快捷操作按钮 ── */
.quick-action-row {
    display: flex;                     /* 快捷按钮横向排列 */
    gap: 3px;                          /* 按钮间距 6px */
    flex-wrap: wrap;                   /* 空间不足时自动换行 */
    margin-bottom: 8px;                /* 底部留出 8px 间距 */
}

/* ── 审批卡片 ── */
.approval-card {
    background: white;                 /* 审批卡片白底 */
    border: 1px solid #E5E6EB;         /* 常规边框 */
    border-left: 4px solid #3370FF;    /* 左侧 4px 蓝色强调条（默认待审批色） */
    border-radius: 8px;                /* 卡片圆角 */
    padding: 14px 16px;                /* 卡片内边距 */
    margin: 8px 0;                     /* 卡片上下外边距 */
}
.approval-card.approved {
    border-left-color: #00B42A;        /* 审批通过时，左侧强调条变为绿色 */
}
.approval-card.rejected {
    border-left-color: #F53F3F;        /* 审批驳回时，左侧强调条变为红色 */
}

/* ── 表格优化 ── */
.stDataFrame { border-radius: 8px; overflow: hidden; }
                                       /* 给 st.dataframe 加圆角并裁切溢出边角 */

/* ── 隐藏 Streamlit 默认元素 ── */
/* #MainMenu { visibility: hidden; } */     /* 隐藏右上角默认菜单按钮 */
footer { visibility: hidden; }         /* 隐藏底部 "Made with Streamlit" 页脚 */

/* ── 飞书聊天面板 ── */
.feishu-header {
    background: linear-gradient(135deg, #00868B 0%, #2B5CE6 100%);
                                       /* 聊天面板头部 135 度蓝紫渐变背景 */
    color: white;                      /* 头部文字颜色 */
    padding: 6px 20px;                /* 头部内边距（上下 14px，左右 20px） */
    border-radius: 12px 12px 0 0;      /* 仅左上、右上圆角，方便与下方聊天区衔接 */
    margin-bottom: 12px;                  /* 紧贴下方元素，不留底部外边距 */
    display: flex;                     /* 启用弹性布局，让图标和标题横向排列 */
    align-items: center;               /* 垂直居中对齐 */
    gap: 10px;                         /* 图标与文字块之间的间距 */
}
.feishu-header .title {
    font-size: 14px;                   /* 助手主标题字号 */
    font-weight: 600;                  /* 半粗体 */
}
.feishu-header .subtitle {
    font-size: 12px;                   /* 副标题字号 */
    opacity: 0.8;                     /* 85% 不透明度，弱化层级突出主标题 */
}

/* Mainheader & Dashboard */
/* ── 主标题 样式 ── */
.st-key-main_header {
    margin-bottom: 12px !important;   /* 想留白大一点就改大，想更紧可改 0px 或 -6px */
    padding-bottom: 0 !important;
}

/* Dashboard 外框（同时兼顾外层 key 容器与内部 border wrapper） */
.st-key-dashboard_frame {
    border: 1px solid #D1D5DB !important;
    border-radius: 12px !important;
    padding: 20px !important;
    background-color: #FFFFFF !important;
}
.st-key-dashboard_frame h4 {
    font-size: 20px !important;
}

.st-key-chat_frame {
    border-radius: 12px !important;
    padding: 10px !important;
}

/* ── Dashboard 卡片 ── */
div[data-testid="stMetric"] {
    background: #F7F8FA;               /* 指标卡背景色 */
    border: 1px solid #E5E6EB;         /* 指标卡边框 */
    border-radius: 10px;               /* 指标卡圆角 */
    padding: 2px 12px;                /* 指标卡内边距 */
    height: 80px !important;          /* 固定 4 张指标卡高度一致；想改高/矮就调这个数字 */
    box-sizing: border-box;            /* 让 padding 和 border 算在 112px 高度内，不额外撑高 */
    display: flex;                     /* 纵向排列内部 Label / Value / Delta */
    flex-direction: column;
    justify-content: flex-start;       /* 顶部对齐；若想整体垂直居中可改 center */
    overflow: hidden;                  /* 防止字号过大或文本过长时溢出卡片边界 */
}

/* 1. 指标卡标题字体大小 */
div[data-testid="stMetric"] [data-testid="stMetricLabel"] p {
    color: #165DFF;                    /* 标题颜色 */
    font-size: 12px !important;        /* 标题字号 */
    line-height: 2.5 !important;       /* 标题行高 */
    margin-bottom: 0px !important;     /* 与主数值的间距 */
}

/* 2. 指标卡主数值字体大小 */
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-size: 20px !important;        /* 主数值字号 */
    line-height: 1 !important;      /* 主数值行高 */
}

/* 3. 指标卡 delta 增减幅度字体大小 */
div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
    font-size: 12px !important;        /* delta 字号 */
    line-height: 1 !important;       /* delta 行高 */
    margin-top: 0px !important;        /* 与主数值的间距 */
}

/* 指标卡 delta 图标（SVG 箭头）大小 */
div[data-testid="stMetric"] [data-testid="stMetricDelta"] svg {
    width: 12px !important;            /* 图标宽度 */
    height: 12px !important;           /* 图标高度 */
    font-size: 12px !important;        /* 兼容图标字体或继承尺寸 */
}

/* ── 主 caption 样式 ── */
.st-key-main_caption [data-testid="stCaptionContainer"] {
    font-size: 10px !important;
    color: #86909C !important;
    line-height: 1.4 !important;
}

</style>
"""

FEISHU_HEADER_HTML = """
<div class="feishu-header">
    <div>
        <div style="font-size: 28px;">🤖</div> <!-- 左侧机器人图标大小；改 font-size 即可缩放 -->
    </div>
    <div>
        <div class="title">飞书助手（模拟）</div> <!-- 聊天面板主标题文案 -->
        <div class="subtitle">用自然语言查询与操作 ERP</div> <!-- 聊天面板副标题文案 -->
    </div>
</div>
"""

WELCOME_MESSAGE = """👋 你好！我是 **ERP Copilot**，你的 AI 制造业助手。

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