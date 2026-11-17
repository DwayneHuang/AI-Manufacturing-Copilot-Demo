"""
BOM Service — BOM 展开与查询
确定性计算，保证结果准确可验证
"""
from __future__ import annotations
from data.store import get_store


def get_bom(product_id: str) -> list[dict]:
    """获取某产品的 BOM（含物料名称和单价信息）"""
    store = get_store()
    bom = store.bom.get(product_id, [])
    result = []
    for item in bom:
        mid = item["material_id"]
        mat = store.materials.get(mid, {})
        result.append({
            "material_id": mid,
            "material_name": mat.get("name", "未知"),
            "category": mat.get("category", ""),
            "quantity_per": item["quantity_per"],
            "unit": item["unit"],
            "unit_cost": mat.get("unit_cost", 0.0),
            "subtotal": round(item["quantity_per"] * mat.get("unit_cost", 0.0), 2),
        })
    return result


def expand_bom(product_id: str, production_qty: int) -> list[dict]:
    """展开 BOM：按生产数量计算每种物料的总需求量"""
    bom = get_bom(product_id)
    for item in bom:
        item["total_quantity"] = item["quantity_per"] * production_qty
        item["total_cost"] = round(item["subtotal"] * production_qty, 2)
    return bom


def get_bom_summary(product_id: str) -> dict:
    """获取 BOM 汇总信息"""
    store = get_store()
    bom = get_bom(product_id)
    product = store.products.get(product_id, {})
    total_material_cost = sum(item["subtotal"] for item in bom)
    return {
        "product_id": product_id,
        "product_name": product.get("name", "未知"),
        "bom_item_count": len(bom),
        "total_material_cost": round(total_material_cost, 2),
        "items": bom,
    }


def get_all_products() -> list[dict]:
    """获取所有产品列表"""
    store = get_store()
    return [
        {"id": pid, **info}
        for pid, info in store.products.items()
    ]


def get_product_by_id(product_id: str) -> dict | None:
    """获取单个产品信息"""
    store = get_store()
    prod = store.products.get(product_id)
    if prod:
        return {"id": product_id, **prod}
    return None
