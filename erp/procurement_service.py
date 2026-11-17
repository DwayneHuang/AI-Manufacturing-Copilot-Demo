"""
Procurement Service — 物料需求计算、缺口分析、采购建议
确定性计算逻辑，保证结果准确可验证
"""
from __future__ import annotations
from datetime import datetime
from data.store import get_store
from data.mock_data import MATERIAL_SUPPLIER_MAP
from erp.bom_service import expand_bom


def calculate_material_requirements() -> list[dict]:
    """
    根据所有产品的生产计划，汇总计算各物料总需求量。
    同一物料在多个产品中使用时会合并需求。
    """
    store = get_store()
    plan = store.production_plan
    agg = {}
    for pid, pinfo in plan.items():
        bom_expanded = expand_bom(pid, pinfo["quantity"])
        product_name = store.products.get(pid, {}).get("name", pid)
        for item in bom_expanded:
            mid = item["material_id"]
            if mid not in agg:
                agg[mid] = {
                    "material_id": mid,
                    "material_name": item["material_name"],
                    "category": item["category"],
                    "unit": item["unit"],
                    "unit_cost": item["unit_cost"],
                    "total_required": 0,
                    "sources": [],
                }
            agg[mid]["total_required"] += item["total_quantity"]
            agg[mid]["sources"].append({
                "product_id": pid,
                "product_name": product_name,
                "quantity_per": item["quantity_per"],
                "plan_quantity": pinfo["quantity"],
                "subtotal": item["total_quantity"],
            })
    return list(agg.values())


def calculate_material_gaps() -> list[dict]:
    """
    计算物料缺口 = 总需求 + 安全库存 - 当前库存
    """
    store = get_store()
    requirements = calculate_material_requirements()
    gaps = []
    for req in requirements:
        mid = req["material_id"]
        inv = store.inventory.get(mid, {})
        current_stock = inv.get("quantity", 0)
        safety_stock = inv.get("safety_stock", 0)
        total_needed = req["total_required"]
        gap = total_needed + safety_stock - current_stock
        item = {
            **req,
            "current_stock": current_stock,
            "safety_stock": safety_stock,
            "gap": max(0, gap),
            "gap_without_safety": max(0, total_needed - current_stock),
            "available_for_production": max(0, current_stock - safety_stock),
            "status": "充足" if gap <= 0 else ("紧急" if total_needed > current_stock else "需补货"),
        }
        gaps.append(item)
    priority = {"紧急": 0, "需补货": 1, "充足": 2}
    gaps.sort(key=lambda x: (priority.get(x["status"], 9), -x["gap"]))
    return gaps


def generate_procurement_suggestions() -> list[dict]:
    """
    根据缺口分析，生成采购建议。
    匹配供应商、考虑最小订购量、计算采购金额。
    """
    store = get_store()
    gaps = calculate_material_gaps()
    suggestions = []
    for item in gaps:
        if item["gap"] <= 0:
            continue
        mid = item["material_id"]
        supplier_ids = MATERIAL_SUPPLIER_MAP.get(mid, [])
        if not supplier_ids:
            continue
        sup_id = supplier_ids[0]
        sup = store.suppliers.get(sup_id, {})
        min_order = sup.get("min_order_qty", 1)
        suggested_qty = max(item["gap"], min_order)
        suggested_qty = ((suggested_qty + 99) // 100) * 100
        suggestions.append({
            "material_id": mid,
            "material_name": item["material_name"],
            "unit": item["unit"],
            "gap_quantity": item["gap"],
            "suggested_quantity": suggested_qty,
            "unit_cost": item["unit_cost"],
            "total_cost": round(suggested_qty * item["unit_cost"], 2),
            "supplier_id": sup_id,
            "supplier_name": sup.get("name", "未知"),
            "lead_time_days": sup.get("lead_time_days", 0),
            "status": item["status"],
            "priority": "高" if item["status"] == "紧急" else "中",
        })
    return suggestions


def create_purchase_draft(suggestions: list[dict] | None = None) -> dict:
    """
    创建采购申请草案（需人工审批）。
    不直接提交正式订单。
    """
    store = get_store()
    if suggestions is None:
        suggestions = generate_procurement_suggestions()
    if not suggestions:
        return {"success": False, "message": "当前物料库存充足，无需采购"}

    draft_id = f"PO-{datetime.now().strftime('%Y%m%d')}-{len(store.purchase_drafts) + 1:03d}"
    total_amount = sum(s["total_cost"] for s in suggestions)
    draft = {
        "id": draft_id,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "items": suggestions,
        "item_count": len(suggestions),
        "total_amount": round(total_amount, 2),
        "status": "待审批",
        "approved_by": None,
        "approved_at": None,
        "remarks": "",
    }
    store.purchase_drafts.append(draft)
    return {
        "success": True,
        "draft": draft,
        "message": f"已创建采购申请草案 {draft_id}，共 {len(suggestions)} 项物料，"
                   f"总金额 ¥{total_amount:,.2f}，等待审批。",
    }


def approve_purchase_draft(draft_id: str) -> dict:
    """审批通过采购草案"""
    store = get_store()
    for draft in store.purchase_drafts:
        if draft["id"] == draft_id and draft["status"] == "待审批":
            draft["status"] = "已批准"
            draft["approved_by"] = "管理员"
            draft["approved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return {"success": True, "message": f"采购申请 {draft_id} 已批准 ✅"}
    return {"success": False, "message": f"未找到待审批的采购申请 {draft_id}"}


def reject_purchase_draft(draft_id: str, reason: str = "") -> dict:
    """驳回采购草案"""
    store = get_store()
    for draft in store.purchase_drafts:
        if draft["id"] == draft_id and draft["status"] == "待审批":
            draft["status"] = "已驳回"
            draft["remarks"] = reason or "未通过审批"
            return {"success": True, "message": f"采购申请 {draft_id} 已驳回 ❌"}
    return {"success": False, "message": f"未找到待审批的采购申请 {draft_id}"}


def get_all_purchase_drafts() -> list[dict]:
    """获取所有采购草案"""
    store = get_store()
    return store.purchase_drafts


def get_production_plan() -> list[dict]:
    """获取当前生产计划"""
    store = get_store()
    plan = store.production_plan
    result = []
    for pid, info in plan.items():
        product = store.products.get(pid, {})
        result.append({
            "product_id": pid,
            "product_name": product.get("name", pid),
            "quantity": info["quantity"],
            "deadline": info["deadline"],
            "priority": info["priority"],
            "status": info["status"],
        })
    return result


def update_production_plan(product_id: str, quantity: int) -> dict:
    """更新生产计划中的产品数量"""
    store = get_store()
    if product_id not in store.production_plan:
        return {"success": False, "message": f"产品 {product_id} 不在生产计划中"}
    old_qty = store.production_plan[product_id]["quantity"]
    store.production_plan[product_id]["quantity"] = quantity
    product = store.products.get(product_id, {})
    return {
        "success": True,
        "product_id": product_id,
        "product_name": product.get("name", product_id),
        "old_quantity": old_qty,
        "new_quantity": quantity,
        "message": f"已将 {product.get('name', product_id)} 的生产计划从 {old_qty} 更新为 {quantity} 台",
    }


def get_suppliers() -> list[dict]:
    """获取所有供应商信息"""
    store = get_store()
    return [
        {"id": sid, **info}
        for sid, info in store.suppliers.items()
    ]


def get_supplier_for_material(material_id: str) -> list[dict]:
    """查询某物料对应的供应商"""
    store = get_store()
    supplier_ids = MATERIAL_SUPPLIER_MAP.get(material_id, [])
    result = []
    for sid in supplier_ids:
        sup = store.suppliers.get(sid, {})
        if sup:
            result.append({"id": sid, **sup})
    return result
