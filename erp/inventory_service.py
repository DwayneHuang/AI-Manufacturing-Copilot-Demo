"""
Inventory Service — 库存查询与管理
确定性操作，支持查询和修改
"""
from __future__ import annotations
from data.store import get_store


def get_all_inventory() -> list[dict]:
    """获取所有物料的库存信息"""
    store = get_store()
    result = []
    for mid, inv in store.inventory.items():
        mat = store.materials.get(mid, {})
        qty = inv["quantity"]
        safety = inv["safety_stock"]
        if qty <= 0:
            status = "缺货"
        elif qty < safety:
            status = "低于安全库存"
        elif qty < safety * 1.2:
            status = "接近安全库存"
        else:
            status = "正常"
        result.append({
            "material_id": mid,
            "material_name": mat.get("name", "未知"),
            "category": mat.get("category", ""),
            "quantity": qty,
            "unit": mat.get("unit", ""),
            "safety_stock": safety,
            "warehouse": inv.get("warehouse", ""),
            "status": status,
        })
    return result


def get_inventory_by_material(material_id: str) -> dict | None:
    """查询单个物料的库存"""
    store = get_store()
    inv = store.inventory.get(material_id)
    if not inv:
        return None
    mat = store.materials.get(material_id, {})
    qty = inv["quantity"]
    safety = inv["safety_stock"]
    if qty <= 0:
        status = "缺货"
    elif qty < safety:
        status = "低于安全库存"
    elif qty < safety * 1.2:
        status = "接近安全库存"
    else:
        status = "正常"
    return {
        "material_id": material_id,
        "material_name": mat.get("name", "未知"),
        "category": mat.get("category", ""),
        "quantity": qty,
        "unit": mat.get("unit", ""),
        "safety_stock": safety,
        "warehouse": inv.get("warehouse", ""),
        "status": status,
    }


def update_inventory(material_id: str, new_quantity: int) -> dict:
    """更新物料库存数量"""
    store = get_store()
    if material_id not in store.inventory:
        return {"success": False, "message": f"物料 {material_id} 不存在"}
    old_qty = store.inventory[material_id]["quantity"]
    store.inventory[material_id]["quantity"] = new_quantity
    mat = store.materials.get(material_id, {})
    return {
        "success": True,
        "material_id": material_id,
        "material_name": mat.get("name", "未知"),
        "old_quantity": old_qty,
        "new_quantity": new_quantity,
        "message": f"已将 {mat.get('name', material_id)} 的库存从 {old_qty} 更新为 {new_quantity}",
    }


def get_low_stock_items() -> list[dict]:
    """获取低库存预警物料"""
    all_inv = get_all_inventory()
    return [item for item in all_inv if item["status"] in ("缺货", "低于安全库存", "接近安全库存")]
