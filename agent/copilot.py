"""
Copilot Agent — LLM + Function Calling 智能体
支持 Gemini API (配置 key 时) 与 高保真模拟模式 (无 key 时，直接驱动确定性 ERP Tools)
"""
from __future__ import annotations
import os
import json
import re
from data.store import get_store
from agent.tools import execute_tool, GEMINI_TOOL_DECLARATIONS

SYSTEM_PROMPT = """你是"智造 Copilot"，一个专业的 AI 制造业助手，服务于智能硬件制造企业。

你的核心能力：
1. BOM (物料清单) 查询与展开
2. 库存查询与管理
3. 物料需求计算与缺口分析
4. 采购建议生成与采购申请创建
5. 生产计划查询与调整
6. 供应商信息查询

重要业务规则：
- 所有业务数据的计算必须通过调用工具函数完成，保证确定性与可验证性，严禁自行编造数字
- 采购申请只能生成草案（Draft），必须由人工审批确认，不可直接提交正式订单
- 回复语言必须简洁、专业、条理清晰，使用 Markdown 表格呈现结构化数据
- 当用户表达修改库存或调整排产计划时，调用对应修改工具并告知用户左侧 Dashboard 已同步更新

当前系统产品主数据：
- P001: 智能手表 X1 Pro
- P002: 智能手环 B2
- P003: 无线降噪耳机 E1
"""


class CopilotAgent:
    """AI 制造业 Copilot 智能体"""

    def __init__(self):
        self.use_llm = False
        self.model = None
        self._try_init_gemini()

    def _try_init_gemini(self):
        """尝试初始化 Gemini API (从环境变量或 Streamlit secrets 读取)"""
        api_key = os.environ.get("GOOGLE_API_KEY", "")
        if not api_key:
            try:
                import streamlit as st
                if hasattr(st, "secrets") and "GOOGLE_API_KEY" in st.secrets:
                    api_key = st.secrets["GOOGLE_API_KEY"]
            except Exception:
                pass

        if not api_key:
            self.use_llm = False
            return

        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                "gemini-2.0-flash",
                system_instruction=SYSTEM_PROMPT,
                tools=[{"function_declarations": GEMINI_TOOL_DECLARATIONS}],
            )
            self.use_llm = True
        except Exception:
            self.use_llm = False

    def chat(self, user_input: str, history: list[dict]) -> str:
        """统一对话接口"""
        if self.use_llm:
            try:
                return self._chat_with_llm(user_input, history)
            except Exception as e:
                # LLM 调用出错时优雅降级到确定性模拟 Agent
                fallback_reply = self._chat_simulated(user_input)
                return f"{fallback_reply}\n\n*(注：LLM 接口响应异常 [{str(e)[:30]}]，已自动切换为确定性规则引擎处理)*"
        return self._chat_simulated(user_input)

    # ─────────────── Gemini LLM 模式 (Function Calling) ───────────────
    def _chat_with_llm(self, user_input: str, history: list[dict]) -> str:
        """使用 Gemini API + Function Calling 驱动确定性工具"""
        import google.generativeai as genai

        gemini_history = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})

        chat = self.model.start_chat(history=gemini_history)
        response = chat.send_message(user_input)

        max_rounds = 5
        for _ in range(max_rounds):
            candidate = response.candidates[0]
            has_fc = False
            for part in candidate.content.parts:
                if hasattr(part, "function_call") and part.function_call and part.function_call.name:
                    has_fc = True
                    tool_name = part.function_call.name
                    tool_args = dict(part.function_call.args) if part.function_call.args else {}
                    tool_result = execute_tool(tool_name, tool_args)
                    response = chat.send_message(
                        genai.protos.Content(
                            parts=[genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=tool_name,
                                    response={"result": json.dumps(tool_result, ensure_ascii=False, default=str)},
                                )
                            )]
                        )
                    )
                    break
            if not has_fc:
                break

        return response.text

    # ─────────────── 确定性模拟模式（无需 API Key） ───────────────
    def _chat_simulated(self, user_input: str) -> str:
        """基于确定性意图识别的 Agent，直接调用真实 ERP 工具，保证准确性与双向同步"""
        store = get_store()
        text = user_input.lower().strip()
        products = store.products

        # ── 1. 修改库存 ──
        m_mat = re.search(r'(M\d{3})\D*?(\d+)', user_input, re.IGNORECASE)
        is_stock_action = any(w in text for w in ["改", "修", "调", "设", "变", "更新"]) and any(w in text for w in ["库存", "存量", "数量", "为"])
        if m_mat and is_stock_action:
            mid, qty = m_mat.group(1).upper(), int(m_mat.group(2))
            result = execute_tool("update_inventory", {"material_id": mid, "new_quantity": qty})
            if isinstance(result, dict) and result.get("success"):
                return f"✅ **库存已更新**\n\n{result['message']}\n\n> 💡 左侧 Dashboard 与缺口分析已实时同步更新。"
            return f"❌ 操作失败：{result.get('message', '未知错误')}"

        # ── 2. 修改生产计划 ──
        pid_target = None
        qty_target = None
        # 尝试匹配 P001/P002/P003 + 数字
        m_pid = re.search(r'(P\d{3})\D*?(\d+)', user_input, re.IGNORECASE)
        if m_pid:
            pid_target = m_pid.group(1).upper()
            qty_target = int(m_pid.group(2))
        else:
            # 尝试产品中文名称 + 数量
            for pid, pinfo in products.items():
                if pinfo["name"] in user_input or any(kw in user_input for kw in [pinfo["name"][:4], pid]):
                    qty_m = re.search(r'(\d+)\s*[台个只套件]?', user_input)
                    if qty_m:
                        pid_target = pid
                        qty_target = int(qty_m.group(1))
                        break

        is_plan_action = any(w in text for w in ["改", "修", "调", "设", "变", "更新", "排产"])
        if pid_target and qty_target is not None and is_plan_action:
            result = execute_tool("update_production_plan", {"product_id": pid_target, "quantity": qty_target})
            if isinstance(result, dict) and result.get("success"):
                return f"✅ **生产计划已更新**\n\n{result['message']}\n\n> 📊 生产计划已联动重新计算物料总需求与缺口分析，左侧 Dashboard 已同步刷新。"
            return f"❌ 操作失败：{result.get('message', '未知错误')}"

        # ── 3. 创建采购申请草案（人工审批） ──
        if re.search(r'(创建|生成|发起|提交|下|提).*(采购|订单|申请|草案|po)', text):
            result = execute_tool("create_purchase_draft", {})
            if isinstance(result, dict) and result.get("success"):
                draft = result["draft"]
                lines = [f"📝 **已成功创建采购申请草案**\n"]
                lines.append(f"- **申请单号**: `{draft['id']}`")
                lines.append(f"- **物料项数**: {draft['item_count']} 项")
                lines.append(f"- **预估总额**: **¥{draft['total_amount']:,.2f}**")
                lines.append(f"- **单据状态**: ⏳ **待审批 (Pending Approval)**\n")
                lines.append("| 物料名称 | 缺口 | 建议采购量 | 推荐供应商 | 交期 | 预估金额 |")
                lines.append("|----------|------|------------|------------|------|----------|")
                for item in draft["items"]:
                    lines.append(
                        f"| {item['material_name']} | {item['gap_quantity']} "
                        f"| {item['suggested_quantity']}{item['unit']} | {item['supplier_name']} "
                        f"| {item['lead_time_days']}天 | ¥{item['total_cost']:,.2f} |"
                    )
                lines.append(f"\n> ⚠️ **人工审批保障**：AI 助手仅生成申请草案，未向供应商正式下单。")
                lines.append(f"> 请在左侧 Dashboard「采购管理」标签页中点击【✅ 批准】，或在右侧回复 `批准 {draft['id']}`。")
                return "\n".join(lines)
            return f"ℹ️ {result.get('message', '当前物料充足，无需采购')}"

        # ── 4. 审批与驳回 ──
        m_approve = re.search(r'(批准|同意|通过|审核通过|approve)\s*(PO[\w-]*)?', user_input, re.IGNORECASE)
        if m_approve:
            draft_id = (m_approve.group(2) or "").strip().upper()
            if not draft_id:
                pending = [d for d in store.purchase_drafts if d["status"] == "待审批"]
                if pending:
                    draft_id = pending[-1]["id"]
            if draft_id:
                result = execute_tool("approve_purchase_draft", {"draft_id": draft_id})
                return f"{'✅' if result.get('success') else '❌'} {result['message']}\n\n> 状态已更新至左侧「采购管理」面板。"
            return "❓ 请指定要批准的单号，例如：`批准 PO-20261118-001`"

        m_reject = re.search(r'(拒绝|驳回|否决|不通过|reject)\s*(PO[\w-]*)?', user_input, re.IGNORECASE)
        if m_reject:
            draft_id = (m_reject.group(2) or "").strip().upper()
            if not draft_id:
                pending = [d for d in store.purchase_drafts if d["status"] == "待审批"]
                if pending:
                    draft_id = pending[-1]["id"]
            if draft_id:
                result = execute_tool("reject_purchase_draft", {"draft_id": draft_id, "reason": "人工审批驳回"})
                return f"{'✅' if result.get('success') else '❌'} {result['message']}\n\n> 驳回状态已同步至 ERP 数据源。"
            return "❓ 请指定要驳回的单号，例如：`驳回 PO-20261118-001`"

        # ── 5. 查询 BOM ──
        if re.search(r'(bom|物料清单|组成|配方|用料|结构|零[部件])', text):
            pid = self._extract_product_id(user_input)
            if not pid:
                return self._product_selection_hint("请问要查询哪个产品的 BOM 清单？")
            result = execute_tool("get_bom", {"product_id": pid})
            if isinstance(result, dict) and "items" in result:
                lines = [f"📋 **{result['product_name']}** ({result['product_id']}) 的 BOM 清单\n"]
                lines.append(f"包含 **{result['bom_item_count']}** 种物料 | 单台物料成本: **¥{result['total_material_cost']:.2f}**\n")
                lines.append("| 物料编码 | 物料名称 | 类别 | 单台用量 | 单价(¥) | 小计(¥) |")
                lines.append("|----------|----------|------|----------|---------|---------|")
                for item in result["items"]:
                    lines.append(
                        f"| {item['material_id']} | {item['material_name']} | {item['category']} "
                        f"| {item['quantity_per']}{item['unit']} | {item['unit_cost']:.2f} | {item['subtotal']:.2f} |"
                    )
                return "\n".join(lines)
            return "❌ 未找到对应产品的 BOM 数据"

        # ── 6. 查询库存 ──
        if re.search(r'(库存|stock|存量|仓库|余量)', text):
            m_mid = re.search(r'(M\d{3})', user_input, re.IGNORECASE)
            if m_mid:
                mid = m_mid.group(1).upper()
                result = execute_tool("get_inventory_by_material", {"material_id": mid})
                if result:
                    status_icons = {"正常": "🟢", "接近安全库存": "🟡", "低于安全库存": "🔴", "缺货": "❌"}
                    icon = status_icons.get(result["status"], "⚪")
                    return (
                        f"📦 **物料库存详情**\n\n"
                        f"- **物料编码**: `{result['material_id']}`\n"
                        f"- **物料名称**: **{result['material_name']}** ({result['category']})\n"
                        f"- **当前库存**: **{result['quantity']}** {result['unit']}\n"
                        f"- **安全库存**: {result['safety_stock']} {result['unit']}\n"
                        f"- **存放仓库**: {result['warehouse']}\n"
                        f"- **库存状态**: {icon} **{result['status']}**"
                    )
                return f"❌ 未找到物料 {mid} 的库存记录"

            result = execute_tool("get_inventory", {})
            if isinstance(result, list):
                lines = ["📦 **物料库存总览**\n"]
                lines.append("| 编码 | 名称 | 当前库存 | 安全库存 | 存放位置 | 状态 |")
                lines.append("|------|------|----------|----------|----------|------|")
                status_icons = {"正常": "🟢", "接近安全库存": "🟡", "低于安全库存": "🔴", "缺货": "❌"}
                warn_count = 0
                for item in result:
                    icon = status_icons.get(item["status"], "⚪")
                    if item["status"] != "正常":
                        warn_count += 1
                    lines.append(
                        f"| {item['material_id']} | {item['material_name']} "
                        f"| {item['quantity']}{item['unit']} | {item['safety_stock']}{item['unit']} "
                        f"| {item['warehouse']} | {icon} {item['status']} |"
                    )
                if warn_count > 0:
                    lines.append(f"\n> ⚠️ 注意：检测到 **{warn_count}** 项物料库存低于或接近安全线！")
                return "\n".join(lines)
            return "❌ 获取库存失败"

        # ── 7. 物料缺口分析 ──
        if re.search(r'(缺口|差额|不足|shortage|缺少|不够|缺料|断料)', text):
            result = execute_tool("calculate_material_gaps", {})
            if isinstance(result, list):
                gaps = [i for i in result if i["gap"] > 0]
                if not gaps:
                    return "✅ **当前物料充足**：所有物料均满足排产计划与安全库存要求，暂无缺口！"
                lines = [f"⚠️ **物料缺口计算与排产影响分析**\n"]
                lines.append(f"当前排产计划下，共有 **{len(gaps)}** 项关键物料存在短缺：\n")
                lines.append("| 物料编码 | 物料名称 | 总需求 | 现有库存 | 安全库存 | 缺口数量 | 预估成本 | 状态 |")
                lines.append("|----------|----------|--------|----------|----------|----------|----------|------|")
                total_cost = 0.0
                for item in gaps:
                    cost = item["gap"] * item["unit_cost"]
                    total_cost += cost
                    icon = "🔴" if item["status"] == "紧急" else "🟡"
                    lines.append(
                        f"| {item['material_id']} | {item['material_name']} | {item['total_required']} "
                        f"| {item['current_stock']} | {item['safety_stock']} | **{item['gap']}** "
                        f"| ¥{cost:,.2f} | {icon} {item['status']} |"
                    )
                lines.append(f"\n💰 **补齐缺口预估总成本: ¥{total_cost:,.2f}**")
                lines.append("\n> 💡 您可以直接回复 **生成采购建议** 或 **创建采购申请**。")
                return "\n".join(lines)
            return "❌ 缺口计算失败"

        # ── 8. 采购建议 ──
        if re.search(r'(采购建议|补货建议|procurement|采购方案|怎么买|采购推荐)', text):
            result = execute_tool("generate_procurement_suggestions", {})
            if isinstance(result, list) and result:
                lines = ["🛒 **智能采购补货建议**\n"]
                lines.append("根据物料缺口、供应商起订量(MOQ)及交期智能测算：\n")
                lines.append("| 物料名称 | 缺口 | 建议采购量 | 推荐供应商 | 供货周期 | 预估金额 | 优先级 |")
                lines.append("|----------|------|------------|------------|----------|----------|--------|")
                total = sum(item["total_cost"] for item in result)
                for item in result:
                    lines.append(
                        f"| {item['material_name']} | {item['gap_quantity']} "
                        f"| {item['suggested_quantity']}{item['unit']} | {item['supplier_name']} "
                        f"| {item['lead_time_days']}天 | ¥{item['total_cost']:,.2f} | {item['priority']} |"
                    )
                lines.append(f"\n💰 **建议采购总金额: ¥{total:,.2f}**")
                lines.append("\n> 💡 回复 **创建采购申请** 可直接生成草案单据供人工审批。")
                return "\n".join(lines)
            return "✅ 当前所有物料库存充足，无需采购。"

        # ── 9. 生产计划查询 ──
        if re.search(r'(生产计划|排产|计划产量|排期|production)', text):
            result = execute_tool("get_production_plan", {})
            if isinstance(result, list):
                lines = ["📊 **当前工厂生产计划**\n"]
                lines.append("| 产品编码 | 产品名称 | 计划产量 | 交付期限 | 优先级 | 排产状态 |")
                lines.append("|----------|----------|----------|----------|--------|----------|")
                for item in result:
                    pri_icon = {"高": "🔴", "中": "🟡", "低": "🟢"}.get(item["priority"], "⚪")
                    lines.append(
                        f"| {item['product_id']} | {item['product_name']} "
                        f"| {item['quantity']} 台 | {item['deadline']} "
                        f"| {pri_icon} {item['priority']} | {item['status']} |"
                    )
                lines.append("\n> 💡 提示：可通过自然语言如 `修改智能手表计划为800台` 随时调整排产。")
                return "\n".join(lines)
            return "❌ 获取生产计划失败"

        # ── 10. 供应商查询 ──
        if re.search(r'(供应商|supplier|供货商|厂商|交期|合作方)', text):
            m_mid = re.search(r'(M\d{3})', user_input, re.IGNORECASE)
            if m_mid:
                mid = m_mid.group(1).upper()
                result = execute_tool("get_supplier_for_material", {"material_id": mid})
                if result:
                    lines = [f"🏭 **物料 {mid} 合作供应商信息**\n"]
                    for s in result:
                        lines.append(
                            f"- **{s['name']}** (`{s['id']}`)\n"
                            f"  👤 联系人: {s['contact']} | 📞 电话: {s['phone']} | 📧 {s['email']}\n"
                            f"  ⏱ 供货周期: {s['lead_time_days']}天 | 最小起订量: {s['min_order_qty']} | 评级: {s['rating']} | 结算方式: {s['payment_terms']}"
                        )
                    return "\n".join(lines)
                return f"未找到物料 {mid} 的供应商记录"

            result = execute_tool("get_suppliers", {})
            if isinstance(result, list):
                lines = ["🏭 **合作供应商总览**\n"]
                lines.append("| 供应商ID | 企业名称 | 联系人 | 电话 | 供货周期 | 评级 | 结算方式 |")
                lines.append("|----------|----------|--------|------|----------|------|----------|")
                for s in result:
                    lines.append(
                        f"| {s['id']} | {s['name']} | {s['contact']} | {s['phone']} "
                        f"| {s['lead_time_days']}天 | {s['rating']} | {s['payment_terms']} |"
                    )
                return "\n".join(lines)
            return "❌ 获取供应商失败"

        # ── 11. 产品主数据查询 ──
        if re.search(r'(产品|型号|品类|商品|在产)', text):
            result = execute_tool("get_product_list", {})
            if isinstance(result, list):
                lines = ["📱 **企业在产产品目录**\n"]
                for p in result:
                    lines.append(
                        f"- **{p['name']}** (`{p['id']}`) - 类别: `{p['category']}`  \n"
                        f"  售价: ¥{p['unit_price']:,.2f} | 描述: {p['description']}"
                    )
                return "\n".join(lines)

        # ── 12. 默认助手引导 ──
        return (
            "🤖 **智造 Copilot 在线**，已连接工厂 ERP 系统与确定性计算引擎。\n\n"
            "你可以直接向我发送以下自然语言指令：\n"
            "- 📋 **BOM 查询**: `查看智能手表X1 Pro的BOM`\n"
            "- 📦 **库存总览**: `查询当前库存` 或 `查询M001库存`\n"
            "- ✏️ **修改库存**: `把M001库存改为600`\n"
            "- ⚠️ **缺口分析**: `分析物料缺口`\n"
            "- 🛒 **采购建议**: `生成采购建议`\n"
            "- 📝 **发起申请**: `创建采购申请`\n"
            "- 📊 **排产调整**: `把智能手环计划产量修改为1200`\n"
            "- 🏭 **供应商**: `查询供应商列表` 或 `查看M001的供应商`\n"
            "- ✅ **审批草案**: `批准 PO-20261118-001`"
        )

    def _extract_product_id(self, text: str) -> str | None:
        """从用户语句中精准提取产品 ID"""
        m = re.search(r'(P00[1-3])', text, re.IGNORECASE)
        if m:
            return m.group(1).upper()
        keyword_map = {
            "P001": ["智能手表", "手表", "x1", "pro"],
            "P002": ["智能手环", "手环", "b2"],
            "P003": ["无线耳机", "降噪耳机", "耳机", "e1"],
        }
        text_lower = text.lower()
        for pid, keywords in keyword_map.items():
            for kw in keywords:
                if kw in text_lower:
                    return pid
        return None

    def _product_selection_hint(self, prompt: str) -> str:
        """提示选择产品"""
        store = get_store()
        lines = [f"❓ {prompt}\n"]
        for pid, pinfo in store.products.items():
            lines.append(f"- `{pid}` **{pinfo['name']}**")
        lines.append("\n请在消息中指明产品名称或编码，如：`查看智能手表的BOM`。")
        return "\n".join(lines)
