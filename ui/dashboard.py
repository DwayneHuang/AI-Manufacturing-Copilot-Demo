"""
Dashboard UI — 左侧 ERP Dashboard 面板
展示 BOM、库存、物料缺口、采购管理
"""
import streamlit as st
import pandas as pd
from data.store import get_store
from erp.bom_service import get_bom_summary, get_all_products
from erp.inventory_service import get_all_inventory, get_low_stock_items, update_inventory
from erp.procurement_service import (
    calculate_material_gaps, generate_procurement_suggestions,
    get_production_plan, update_production_plan,
    approve_purchase_draft, reject_purchase_draft,
    create_purchase_draft
)


def _safe_style_map(styler, func, subset):
    """兼容旧版 applymap 和新版 map"""
    if hasattr(styler, "map"):
        return styler.map(func, subset=subset)
    return styler.applymap(func, subset=subset)


def render_dashboard():
    """渲染左侧 ERP Dashboard"""
    st.markdown("### 📊 ERP Dashboard")

    # ── KPI 指标 ──
    _render_kpi_metrics()

    # ── Tab 分页 ──
    tabs = st.tabs(["🏭 生产计划", "📋 BOM", "📦 库存", "⚠️ 物料缺口", "🛒 采购管理"])

    with tabs[0]:
        _render_production_plan()
    with tabs[1]:
        _render_bom()
    with tabs[2]:
        _render_inventory()
    with tabs[3]:
        _render_gaps()
    with tabs[4]:
        _render_procurement()


def _render_kpi_metrics():
    """顶部 KPI 指标卡片"""
    store = get_store()
    gaps = calculate_material_gaps()
    gap_count = sum(1 for g in gaps if g["gap"] > 0)
    total_plan = sum(p["quantity"] for p in store.production_plan.values())
    pending_drafts = sum(1 for d in store.purchase_drafts if d["status"] == "待审批")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📱 在产产品", f"{len(store.products)} 款")
    c2.metric("🏭 计划总产量", f"{total_plan:,} 台")
    c3.metric("⚠️ 物料缺口", f"{gap_count} 项", delta=f"-{gap_count}" if gap_count else None, delta_color="inverse")
    c4.metric("📝 待审批单据", f"{pending_drafts} 单")


def _render_production_plan():
    """生产计划展示与编辑"""
    st.markdown("#### 生产计划管理")
    st.caption("可直接调整各产品产量，物料总需求与缺口分析将实时联动计算")

    plan_data = get_production_plan()
    df = pd.DataFrame(plan_data)
    df.columns = ["产品ID", "产品名称", "计划产量", "交付日期", "优先级", "状态"]
    st.dataframe(df, use_container_width=True, hide_index=True)

    # 编辑区
    st.markdown("---")
    st.markdown("**✏️ 调整计划产量**")
    col_pid, col_qty, col_btn = st.columns([2, 2, 1])
    with col_pid:
        products = get_all_products()
        product_options = {f"{p['id']} - {p['name']}": p["id"] for p in products}
        selected = st.selectbox("选择产品", list(product_options.keys()), key="dash_plan_product")
    with col_qty:
        new_qty = st.number_input("新产量(台)", min_value=0, max_value=20000, value=600, step=100, key="dash_plan_qty")
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("更新计划", key="dash_plan_update", type="primary"):
            pid = product_options[selected]
            result = update_production_plan(pid, new_qty)
            if result["success"]:
                st.success(result["message"])
                st.rerun()
            else:
                st.error(result["message"])


def _render_bom():
    """BOM 展示"""
    st.markdown("#### BOM 物料清单")

    products = get_all_products()
    product_options = {f"{p['id']} - {p['name']}": p["id"] for p in products}
    selected = st.selectbox("选择产品查看 BOM", list(product_options.keys()), key="dash_bom_product")
    pid = product_options[selected]

    bom_summary = get_bom_summary(pid)
    st.info(f"物料种类: **{bom_summary['bom_item_count']}** 项 | 单台物料成本: **¥{bom_summary['total_material_cost']:.2f}**")

    bom_data = bom_summary["items"]
    df = pd.DataFrame(bom_data)
    df = df[["material_id", "material_name", "category", "quantity_per", "unit", "unit_cost", "subtotal"]]
    df.columns = ["物料编码", "物料名称", "物料类别", "单台用量", "单位", "单价(¥)", "单台小计(¥)"]
    st.dataframe(df, use_container_width=True, hide_index=True)

    store = get_store()
    plan_qty = store.production_plan.get(pid, {}).get("quantity", 0)
    if plan_qty > 0:
        total_cost = bom_summary["total_material_cost"] * plan_qty
        st.metric(f"当前排产 {plan_qty} 台总物料预算", f"¥{total_cost:,.2f}")


def _render_inventory():
    """库存展示"""
    st.markdown("#### 库存管理")

    inv_data = get_all_inventory()
    df = pd.DataFrame(inv_data)
    df = df[["material_id", "material_name", "category", "quantity", "unit", "safety_stock", "warehouse", "status"]]
    df.columns = ["物料编码", "物料名称", "类别", "现有库存", "单位", "安全库存", "存放仓库", "状态"]

    status_filter = st.multiselect(
        "按库存状态筛选",
        ["正常", "接近安全库存", "低于安全库存", "缺货"],
        default=None,
        key="dash_inv_filter",
    )
    if status_filter:
        df = df[df["状态"].isin(status_filter)]

    def style_status(val):
        colors = {"正常": "#00B42A", "接近安全库存": "#FF7D00", "低于安全库存": "#F53F3F", "缺货": "#F53F3F"}
        return f"color: {colors.get(val, 'black')}; font-weight: bold"

    styled = _safe_style_map(df.style, style_status, subset=["状态"])
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # 库存修改
    st.markdown("---")
    st.markdown("**✏️ 手动修改库存**")
    col_mid, col_qty, col_btn = st.columns([2, 2, 1])
    with col_mid:
        mat_options = {f"{m['material_id']} - {m['material_name']}": m["material_id"] for m in inv_data}
        selected_mat = st.selectbox("选择物料", list(mat_options.keys()), key="dash_inv_material")
    with col_qty:
        new_inv_qty = st.number_input("新库存数量", min_value=0, max_value=99999, value=500, step=50, key="dash_inv_qty")
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("更新库存", key="dash_inv_update", type="primary"):
            mid = mat_options[selected_mat]
            result = update_inventory(mid, new_inv_qty)
            if result["success"]:
                st.success(result["message"])
                st.rerun()
            else:
                st.error(result["message"])


def _render_gaps():
    """物料缺口分析"""
    st.markdown("#### 物料缺口分析")
    st.caption("确定性计算公式：缺口 = 总需求量 + 安全库存 - 当前库存")

    gaps = calculate_material_gaps()
    gap_items = [g for g in gaps if g["gap"] > 0]
    ok_items = [g for g in gaps if g["gap"] <= 0]

    if not gap_items:
        st.success("✅ 当前所有物料库存充足，满足排产计划需求！")
    else:
        st.warning(f"检测到 **{len(gap_items)}** 项物料存在缺口")

        df_data = []
        for g in gap_items:
            df_data.append({
                "物料编码": g["material_id"],
                "物料名称": g["material_name"],
                "总需求": g["total_required"],
                "现有库存": g["current_stock"],
                "安全库存": g["safety_stock"],
                "缺口数量": g["gap"],
                "补货预估成本(¥)": f"{g['gap'] * g['unit_cost']:,.2f}",
                "状态": g["status"],
            })
        df = pd.DataFrame(df_data)

        def style_gap_status(val):
            if val == "紧急":
                return "color: #F53F3F; font-weight: bold"
            elif val == "需补货":
                return "color: #FF7D00; font-weight: bold"
            return ""

        styled = _safe_style_map(df.style, style_gap_status, subset=["状态"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

        total_gap_cost = sum(g["gap"] * g["unit_cost"] for g in gap_items)
        st.metric("补齐缺口预估总成本", f"¥{total_gap_cost:,.2f}")

    with st.expander(f"📦 库存充足的物料清单 ({len(ok_items)} 项)", expanded=False):
        if ok_items:
            df_ok = pd.DataFrame([{
                "物料编码": g["material_id"],
                "物料名称": g["material_name"],
                "总需求": g["total_required"],
                "现有库存": g["current_stock"],
                "安全库存": g["safety_stock"],
                "富余可用": g["current_stock"] - g["total_required"],
            } for g in ok_items])
            st.dataframe(df_ok, use_container_width=True, hide_index=True)


def _render_procurement():
    """采购管理"""
    st.markdown("#### 采购管理与人工审批")

    # 采购建议
    with st.expander("📋 智能采购建议", expanded=True):
        suggestions = generate_procurement_suggestions()
        if suggestions:
            df_data = []
            for s in suggestions:
                df_data.append({
                    "物料名称": s["material_name"],
                    "缺口数量": s["gap_quantity"],
                    "建议采购量": s["suggested_quantity"],
                    "推荐供应商": s["supplier_name"],
                    "供货周期(天)": s["lead_time_days"],
                    "预估金额(¥)": f"{s['total_cost']:,.2f}",
                    "优先级": s["priority"],
                })
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

            total = sum(s["total_cost"] for s in suggestions)
            col1, col2 = st.columns([2, 1])
            col1.metric("建议采购总金额", f"¥{total:,.2f}")
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("📝 生成采购申请草案", type="primary", key="dash_create_po"):
                    result = create_purchase_draft(suggestions)
                    if result["success"]:
                        st.success(result["message"])
                        st.rerun()
                    else:
                        st.info(result["message"])
        else:
            st.success("✅ 当前库存充足，无采购需求。")

    # 采购申请单与人工审批
    st.markdown("---")
    st.markdown("**📄 采购申请单 (需人工审批)**")
    store = get_store()
    drafts = store.purchase_drafts
    if not drafts:
        st.info("暂无采购申请单据。可点击上方【生成采购申请草案】或在飞书聊天框输入【创建采购申请】。")
        return

    for draft in reversed(drafts):
        status_colors = {"待审批": "🟡", "已批准": "🟢", "已驳回": "🔴"}
        status_icon = status_colors.get(draft["status"], "⚪")

        with st.expander(
            f"{status_icon} 单号: {draft['id']} | 金额: ¥{draft['total_amount']:,.2f} | 状态: {draft['status']}",
            expanded=(draft["status"] == "待审批")
        ):
            col1, col2, col3 = st.columns(3)
            col1.write(f"**创建时间**: {draft['created_at']}")
            col2.write(f"**物料项数**: {draft['item_count']} 项")
            col3.write(f"**申请金额**: ¥{draft['total_amount']:,.2f}")

            items_df = pd.DataFrame([{
                "物料": i["material_name"],
                "采购量": f"{i['suggested_quantity']}{i['unit']}",
                "推荐供应商": i["supplier_name"],
                "单价": f"¥{i['unit_cost']:.2f}",
                "小计": f"¥{i['total_cost']:,.2f}",
            } for i in draft["items"]])
            st.dataframe(items_df, use_container_width=True, hide_index=True)

            # 审批操作区
            if draft["status"] == "待审批":
                st.markdown("> ⚠️ **人工审批提醒**：AI Agent 仅生成申请草案，点击【批准】确认提交采购订单。")
                col_a, col_r, col_space = st.columns([1, 1, 3])
                with col_a:
                    if st.button("✅ 批准", key=f"approve_{draft['id']}", type="primary"):
                        result = approve_purchase_draft(draft["id"])
                        st.success(result["message"])
                        st.rerun()
                with col_r:
                    if st.button("❌ 驳回", key=f"reject_{draft['id']}"):
                        result = reject_purchase_draft(draft["id"], "管理员驳回")
                        st.warning(result["message"])
                        st.rerun()
            elif draft["status"] == "已批准":
                st.success(f"✅ 已由【{draft.get('approved_by', '管理员')}】于 {draft.get('approved_at', '-')} 审批通过")
            elif draft["status"] == "已驳回":
                st.error(f"❌ 已驳回 | 备注: {draft.get('remarks', '-')}")
