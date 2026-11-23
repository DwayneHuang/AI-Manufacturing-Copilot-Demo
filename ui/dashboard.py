"""
Dashboard UI — 左侧 ERP Dashboard 面板
展示 BOM、库存、物料缺口、采购管理
"""
import streamlit as st  # Streamlit Web 界面框架
import pandas as pd  # 数据处理库，用于构造表格 DataFrame
from data.store import get_store  # 获取全局共享的 ERP 数据仓库实例
from erp.bom_service import get_bom_summary, get_all_products  # BOM 汇总与产品查询服务
from erp.inventory_service import get_all_inventory, get_low_stock_items, update_inventory  # 库存查询与更新服务
from erp.procurement_service import (  # 采购、缺口计算与生产计划服务
    calculate_material_gaps, generate_procurement_suggestions,
    get_production_plan, update_production_plan,
    approve_purchase_draft, reject_purchase_draft,
    create_purchase_draft
)


def _safe_style_map(styler, func, subset):
    """兼容旧版 applymap 和新版 map（Pandas 2.1+ 推荐使用 map）"""
    if hasattr(styler, "map"):  # 新版 Pandas Styler 提供 map 方法
        return styler.map(func, subset=subset)  # 对指定列子集应用样式映射函数
    return styler.applymap(func, subset=subset)  # 旧版 Pandas 回退使用 applymap


def render_dashboard():
    """渲染左侧 ERP Dashboard"""
    st.markdown("#### ERP Dashboard")  # 面板主标题

    # ── KPI 指标 ──
    _render_kpi_metrics()  # 渲染顶部 4 个核心 KPI 指标卡片

    # ── Tab 分页 ──
    tabs = st.tabs(["生产计划", "BOM", "库存", "物料缺口", "采购管理"])  # 创建 5 个功能标签页

    with tabs[0]:  # 标签页 0：生产计划
        _render_production_plan()
    with tabs[1]:  # 标签页 1：BOM 清单
        _render_bom()
    with tabs[2]:  # 标签页 2：库存管理
        _render_inventory()
    with tabs[3]:  # 标签页 3：物料缺口分析
        _render_gaps()
    with tabs[4]:  # 标签页 4：采购建议与人工审批
        _render_procurement()


def _render_kpi_metrics():
    """顶部 KPI 指标卡片"""
    store = get_store()  # 读取当前共享的 ERP 数据仓库
    gaps = calculate_material_gaps()  # 计算所有物料的缺口明细
    gap_count = sum(1 for g in gaps if g["gap"] > 0)  # 统计存在缺口（gap 大于 0）的物料项数
    total_plan = sum(p["quantity"] for p in store.production_plan.values())  # 汇总各产品计划总产量
    pending_drafts = sum(1 for d in store.purchase_drafts if d["status"] == "待审批")  # 统计待审批采购申请单数量
    c1, c2, c3, c4 = st.columns(4)  # 均分为 4 列展示 KPI 卡片
    c1.metric("在产产品", f"{len(store.products)} 款")  # 在产产品款数
    c2.metric("计划总产量", f"{total_plan:,} 台")  # 计划总产量（千分位格式化）
    c3.metric("物料缺口", f"{gap_count} 项", delta=f"-{gap_count}" if gap_count else None, delta_color="inverse")  # 缺口项数；delta_color="inverse" 使负向变化显示为警示色
    c4.metric("待审批单据", f"{pending_drafts} 单")  # 待审批单据数量


def _render_production_plan():
    with st.container(key="production_plan"):
        """生产计划展示与编辑"""
        st.markdown("#### 生产计划管理")  # 子标题
        st.caption("可直接调整各产品产量，物料总需求与缺口分析将实时联动计算")  # 功能说明小字

        plan_data = get_production_plan()  # 获取当前生产计划列表
        df = pd.DataFrame(plan_data)  # 转为 DataFrame 以便表格展示
        df.columns = ["产品ID", "产品名称", "计划产量", "交付日期", "优先级", "状态"]  # 重命名为中文表头
        st.dataframe(df, width="stretch", hide_index=True)  # 已修正废弃参数：use_container_width=True -> width="stretch"；隐藏默认索引列

        # 编辑区
        #st.markdown("---")  # 分隔线
        st.markdown("#### ✏️ 调整计划产量")  # 排产调整区标题
        col_pid, col_qty, col_btn = st.columns([2, 2, 1])  # 三列布局：产品选择(2) : 新产量输入(2) : 提交按钮(1)
        with col_pid:
            products = get_all_products()  # 获取全部产品列表
            product_options = {f"{p['id']} - {p['name']}": p["id"] for p in products}  # 构建“显示文本 -> 产品ID”映射
            selected = st.selectbox("选择产品", list(product_options.keys()), key="dash_plan_product")  # 产品下拉选择框
        with col_qty:
            new_qty = st.number_input("新产量(台)", min_value=0, max_value=20000, value=600, step=100, key="dash_plan_qty")  # 新产量输入框（默认 600，步进 100）
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)  # 占位换行，使按钮与左侧输入框大致垂直对齐
            if st.button("更新计划", key="dash_plan_update", type="primary"):  # 主按钮：触发排产产量更新
                pid = product_options[selected]  # 取出选中的产品 ID
                result = update_production_plan(pid, new_qty)  # 调用服务层更新计划产量
                if result["success"]:  # 更新成功
                    st.success(result["message"])  # 显示成功提示
                    st.rerun()  # 立即重新运行脚本，刷新 KPI、物料缺口与采购建议
                else:  # 更新失败
                    st.error(result["message"])  # 显示错误提示


def _render_bom():
    with st.container(key="bom"):
        """BOM 展示"""
        st.markdown("#### BOM 物料清单")  # 子标题

        products = get_all_products()  # 获取全部产品列表
        product_options = {f"{p['id']} - {p['name']}": p["id"] for p in products}  # 选项映射
        selected = st.selectbox("选择产品查看 BOM", list(product_options.keys()), key="dash_bom_product")  # 选择要查看 BOM 的产品
        pid = product_options[selected]  # 取出产品 ID

        bom_summary = get_bom_summary(pid)  # 查询该产品的 BOM 汇总与明细
        st.info(f"物料种类: **{bom_summary['bom_item_count']}** 项 | 单台物料成本: **¥{bom_summary['total_material_cost']:.2f}**")  # 展示物料项数与单台成本

        bom_data = bom_summary["items"]  # 取出 BOM 物料明细列表
        df = pd.DataFrame(bom_data)  # 转为 DataFrame
        df = df[["material_id", "material_name", "category", "quantity_per", "unit", "unit_cost", "subtotal"]]  # 筛选并固定列顺序
        df.columns = ["物料编码", "物料名称", "物料类别", "单台用量", "单位", "单价(¥)", "单台小计(¥)"]  # 中文表头
        st.dataframe(df, width="stretch", hide_index=True)  # 已修正废弃参数：use_container_width=True -> width="stretch"

        store = get_store()  # 获取数据仓库
        plan_qty = store.production_plan.get(pid, {}).get("quantity", 0)  # 读取该产品当前排产数量
        if plan_qty > 0:  # 若排产数量大于 0，计算整批物料预算
            total_cost = bom_summary["total_material_cost"] * plan_qty  # 单台成本 × 排产数量
            st.metric(f"当前排产 {plan_qty} 台总物料预算", f"¥{total_cost:,.2f}")  # 展示总预算指标卡


def _render_inventory():
    with st.container(key="inventory"):
        """库存展示"""
        st.markdown("#### 库存管理")  # 子标题

        inv_data = get_all_inventory()  # 获取全部物料库存数据
        df = pd.DataFrame(inv_data)  # 转为 DataFrame
        df = df[["material_id", "material_name", "category", "quantity", "unit", "safety_stock", "warehouse", "status"]]  # 筛选展示字段
        df.columns = ["物料编码", "物料名称", "类别", "现有库存", "单位", "安全库存", "存放仓库", "状态"]  # 中文表头

        status_filter = st.multiselect(  # 库存状态多选筛选器
            "按库存状态筛选",
            ["正常", "接近安全库存", "低于安全库存", "缺货"],
            default=None,
            key="dash_inv_filter",
        )
        if status_filter:  # 若用户选择了筛选状态，则过滤表格行
            df = df[df["状态"].isin(status_filter)]

        def style_status(val):  # 根据库存状态返回文字颜色与加粗样式
            colors = {"正常": "#00B42A", "接近安全库存": "#FF7D00", "低于安全库存": "#F53F3F", "缺货": "#F53F3F"}
            return f"color: {colors.get(val, 'black')}; font-weight: bold"

        styled = _safe_style_map(df.style, style_status, subset=["状态"])  # 给“状态”列上色
        st.dataframe(styled, width="stretch", hide_index=True)  # 已修正废弃参数：use_container_width=True -> width="stretch"

        # 库存修改
        #st.markdown("---")  # 分隔线
        st.markdown("#### ✏️ 手动修改库存")  # 库存调整区标题
        col_mid, col_qty, col_btn = st.columns([2, 2, 1])  # 三列布局：选物料、输新库存、点更新
        with col_mid:
            mat_options = {f"{m['material_id']} - {m['material_name']}": m["material_id"] for m in inv_data}  # 物料下拉选项映射
            selected_mat = st.selectbox("选择物料", list(mat_options.keys()), key="dash_inv_material")  # 物料选择框
        with col_qty:
            new_inv_qty = st.number_input("新库存数量", min_value=0, max_value=99999, value=500, step=50, key="dash_inv_qty")  # 新库存输入框（默认 500，步进 50）
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)  # 对齐按钮位置
            if st.button("更新库存", key="dash_inv_update", type="primary"):  # 点击更新库存
                mid = mat_options[selected_mat]  # 取出物料编码
                result = update_inventory(mid, new_inv_qty)  # 调用服务层更新库存
                if result["success"]:  # 更新成功
                    st.success(result["message"])  # 提示成功
                    st.rerun()  # 刷新界面状态
                else:  # 更新失败
                    st.error(result["message"])  # 提示错误


def _render_gaps():
    with st.container(key="gaps"):
        """物料缺口分析"""
        st.markdown("#### 物料缺口分析")  # 子标题
        st.caption("确定性计算公式：缺口 = 总需求量 + 安全库存 - 当前库存")  # 缺口计算公式说明

        gaps = calculate_material_gaps()  # 获取缺口计算结果列表
        gap_items = [g for g in gaps if g["gap"] > 0]  # 筛选出存在缺口的物料
        ok_items = [g for g in gaps if g["gap"] <= 0]  # 筛选出库存充足（无缺口）的物料

        if not gap_items:  # 没有缺口物料时的提示
            st.success("✅ 当前所有物料库存充足，满足排产计划需求！")
        else:  # 存在缺口时展示缺口表与补货成本
            st.warning(f"检测到 **{len(gap_items)}** 项物料存在缺口")

            df_data = []  # 构造缺口展示行
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
            df = pd.DataFrame(df_data)  # 转为 DataFrame

            def style_gap_status(val):  # 按缺口紧急程度设置状态颜色
                if val == "紧急":
                    return "color: #F53F3F; font-weight: bold"
                elif val == "需补货":
                    return "color: #FF7D00; font-weight: bold"
                return ""

            styled = _safe_style_map(df.style, style_gap_status, subset=["状态"])  # 应用缺口状态样式
            st.dataframe(styled, width="stretch", hide_index=True)  # 已修正废弃参数：use_container_width=True -> width="stretch"

            total_gap_cost = sum(g["gap"] * g["unit_cost"] for g in gap_items)  # 汇总补齐缺口的预估总成本
            st.metric("补齐缺口预估总成本", f"¥{total_gap_cost:,.2f}")  # 展示补货总成本指标卡

        with st.expander(f"📦 库存充足的物料清单 ({len(ok_items)} 项)", expanded=False):  # 可折叠查看无缺口物料，默认收起
            if ok_items:
                df_ok = pd.DataFrame([{
                    "物料编码": g["material_id"],
                    "物料名称": g["material_name"],
                    "总需求": g["total_required"],
                    "现有库存": g["current_stock"],
                    "安全库存": g["safety_stock"],
                    "富余可用": g["current_stock"] - g["total_required"],
                } for g in ok_items])
                st.dataframe(df_ok, width="stretch", hide_index=True)  # 已修正废弃参数：use_container_width=True -> width="stretch"


def _render_procurement():
    with st.container(key="procurement"):
        """采购管理"""
        st.markdown("#### 采购管理与人工审批")  # 子标题

        # 采购建议
        with st.expander("📋 智能采购建议", expanded=True):  # 采购建议折叠块，默认展开
            suggestions = generate_procurement_suggestions()  # 根据缺口生成采购建议
            if suggestions:  # 有采购建议时展示建议明细表
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
                st.dataframe(df, width="stretch", hide_index=True)  # 已修正废弃参数：use_container_width=True -> width="stretch"

                total = sum(s["total_cost"] for s in suggestions)  # 计算建议采购总金额
                col1, col2 = st.columns([2, 1])  # 左侧显示总金额，右侧放生成草案按钮
                col1.metric("建议采购总金额", f"¥{total:,.2f}")
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)  # 对齐按钮
                    if st.button("📝 生成采购申请草案", type="primary", key="dash_create_po"):  # 点击生成采购申请单草案
                        result = create_purchase_draft(suggestions)  # 调用服务层创建草案
                        if result["success"]:
                            st.success(result["message"])  # 提示草案已生成
                            st.rerun()  # 刷新页面以显示新生成的单据
                        else:
                            st.info(result["message"])
            else:  # 无缺口则无需采购
                st.success("✅ 当前库存充足，无采购需求。")

        # 采购申请单与人工审批
        #st.markdown("---")  # 分隔线
        st.markdown("**📄 采购申请单 (需人工审批)**")  # 审批列表标题
        store = get_store()  # 获取全局仓库
        drafts = store.purchase_drafts  # 取出所有采购申请单
        if not drafts:  # 尚无申请单时的引导提示
            st.info("暂无采购申请单据。可点击上方【生成采购申请草案】或在飞书聊天框输入【创建采购申请】。")
            return

        for draft in reversed(drafts):  # 倒序遍历，让最新创建的单据排在最前面
            status_colors = {"待审批": "🟡", "已批准": "🟢", "已驳回": "🔴"}  # 状态对应圆点图标
            status_icon = status_colors.get(draft["status"], "⚪")  # 获取当前单据状态图标

            with st.expander(  # 每张采购单渲染为一个折叠卡片；待审批单据默认展开
                f"{status_icon} 单号: {draft['id']} | 金额: ¥{draft['total_amount']:,.2f} | 状态: {draft['status']}",
                expanded=(draft["status"] == "待审批")
            ):
                col1, col2, col3 = st.columns(3)  # 单据摘要信息三列展示
                col1.write(f"**创建时间**: {draft['created_at']}")
                col2.write(f"**物料项数**: {draft['item_count']} 项")
                col3.write(f"**申请金额**: ¥{draft['total_amount']:,.2f}")

                items_df = pd.DataFrame([{  # 构造单据内采购物料明细表
                    "物料": i["material_name"],
                    "采购量": f"{i['suggested_quantity']}{i['unit']}",
                    "推荐供应商": i["supplier_name"],
                    "单价": f"¥{i['unit_cost']:.2f}",
                    "小计": f"¥{i['total_cost']:,.2f}",
                } for i in draft["items"]])
                st.dataframe(items_df, width="stretch", hide_index=True)  # 已修正废弃参数：use_container_width=True -> width="stretch"

                # 审批操作区
                if draft["status"] == "待审批":  # 仅待审批状态显示批准/驳回按钮
                    st.markdown("> ⚠️ **人工审批提醒**：AI Agent 仅生成申请草案，点击【批准】确认提交采购订单。")
                    col_a, col_r, col_space = st.columns([1, 1, 3])  # 批准按钮、驳回按钮、右侧留白占位
                    with col_a:
                        if st.button("✅ 批准", key=f"approve_{draft['id']}", type="primary"):  # 批准单据
                            result = approve_purchase_draft(draft["id"])
                            st.success(result["message"])
                            st.rerun()
                    with col_r:
                        if st.button("❌ 驳回", key=f"reject_{draft['id']}"):  # 驳回单据
                            result = reject_purchase_draft(draft["id"], "管理员驳回")
                            st.warning(result["message"])
                            st.rerun()
                elif draft["status"] == "已批准":  # 已批准状态展示审批人及时间
                    st.success(f"✅ 已由【{draft.get('approved_by', '管理员')}】于 {draft.get('approved_at', '-')} 审批通过")
                elif draft["status"] == "已驳回":  # 已驳回状态展示驳回备注
                    st.error(f"❌ 已驳回 | 备注: {draft.get('remarks', '-')}")