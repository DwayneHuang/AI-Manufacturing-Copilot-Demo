"""
FastAPI ERP Service
提供确定性的 ERP Tools / Functions，负责 BOM 展开、库存查询、物料需求及缺口计算、采购建议等业务逻辑
可独立启动 (uvicorn api.main:app) 或由 Streamlit 直接调用
"""
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from api.schemas import (
    ProductSchema, BOMSummarySchema, BOMExpandRequest, BOMItemSchema,
    InventoryItemSchema, InventoryUpdateRequest,
    ProductionPlanItemSchema, ProductionPlanUpdateRequest,
    RequirementItemSchema, GapItemSchema,
    ProcurementSuggestionSchema, PurchaseDraftSchema, ApprovalActionRequest,
    SupplierSchema
)
from erp.bom_service import get_all_products, get_product_by_id, get_bom_summary, expand_bom
from erp.inventory_service import (
    get_all_inventory, get_inventory_by_material, update_inventory, get_low_stock_items
)
from erp.procurement_service import (
    calculate_material_requirements, calculate_material_gaps,
    generate_procurement_suggestions, create_purchase_draft,
    approve_purchase_draft, reject_purchase_draft,
    get_all_purchase_drafts, get_production_plan, update_production_plan,
    get_suppliers, get_supplier_for_material
)

app = FastAPI(
    title="AI Manufacturing ERP Tools API",
    description="智能制造 Copilot 确定性 ERP 核心计算服务与业务数据 API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ───────────────────────── 产品 API ─────────────────────────
@app.get("/api/products", response_model=List[ProductSchema], tags=["产品管理"])
def list_products():
    """获取所有产品列表"""
    return get_all_products()


@app.get("/api/products/{product_id}", response_model=ProductSchema, tags=["产品管理"])
def get_product(product_id: str):
    """根据ID获取单个产品信息"""
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"产品 {product_id} 不存在")
    return product


# ───────────────────────── BOM API ─────────────────────────
@app.get("/api/bom/{product_id}", response_model=BOMSummarySchema, tags=["BOM 管理"])
def get_product_bom(product_id: str):
    """获取产品的 BOM 物料清单及汇总成本"""
    summary = get_bom_summary(product_id)
    if summary["bom_item_count"] == 0:
        raise HTTPException(status_code=404, detail=f"未找到产品 {product_id} 的 BOM")
    return summary


@app.post("/api/bom/{product_id}/expand", response_model=List[BOMItemSchema], tags=["BOM 管理"])
def expand_product_bom(product_id: str, req: BOMExpandRequest):
    """按生产数量展开 BOM，计算总需求量与成本"""
    items = expand_bom(product_id, req.quantity)
    if not items:
        raise HTTPException(status_code=404, detail=f"未找到产品 {product_id} 的 BOM")
    return items


# ───────────────────────── 库存 API ─────────────────────────
@app.get("/api/inventory", response_model=List[InventoryItemSchema], tags=["库存管理"])
def list_inventory():
    """获取所有物料的当前库存状态"""
    return get_all_inventory()


@app.get("/api/inventory/low-stock", response_model=List[InventoryItemSchema], tags=["库存管理"])
def list_low_stock():
    """获取低库存与缺货预警物料"""
    return get_low_stock_items()


@app.get("/api/inventory/{material_id}", response_model=InventoryItemSchema, tags=["库存管理"])
def get_material_inventory(material_id: str):
    """查询单项物料库存"""
    inv = get_inventory_by_material(material_id)
    if not inv:
        raise HTTPException(status_code=404, detail=f"物料 {material_id} 不存在")
    return inv


@app.put("/api/inventory/{material_id}", tags=["库存管理"])
def modify_inventory(material_id: str, req: InventoryUpdateRequest):
    """更新指定物料的库存数量"""
    res = update_inventory(material_id, req.new_quantity)
    if not res.get("success"):
        raise HTTPException(status_code=404, detail=res.get("message"))
    return res


# ───────────────────────── 生产计划 API ─────────────────────────
@app.get("/api/production-plan", response_model=List[ProductionPlanItemSchema], tags=["生产计划"])
def list_production_plan():
    """获取当前所有产品的排产计划"""
    return get_production_plan()


@app.put("/api/production-plan/{product_id}", tags=["生产计划"])
def modify_production_plan(product_id: str, req: ProductionPlanUpdateRequest):
    """修改指定产品的排产计划数量"""
    res = update_production_plan(product_id, req.quantity)
    if not res.get("success"):
        raise HTTPException(status_code=404, detail=res.get("message"))
    return res


# ───────────────────────── 需求与缺口分析 API ─────────────────────────
@app.get("/api/requirements", response_model=List[RequirementItemSchema], tags=["需求与缺口"])
def get_requirements():
    """根据生产计划计算物料总需求汇总"""
    return calculate_material_requirements()


@app.get("/api/gaps", response_model=List[GapItemSchema], tags=["需求与缺口"])
def get_gaps():
    """确定性计算物料缺口 (生产需求 + 安全库存 - 当前库存)"""
    return calculate_material_gaps()


# ───────────────────────── 采购建议与草案审批 API ─────────────────────────
@app.get("/api/procurement/suggestions", response_model=List[ProcurementSuggestionSchema], tags=["采购管理"])
def get_procurement_suggestions():
    """根据缺口生成采购建议（含供应商匹配、最小订购量向上取整）"""
    return generate_procurement_suggestions()


@app.get("/api/procurement/drafts", response_model=List[PurchaseDraftSchema], tags=["采购管理"])
def list_purchase_drafts():
    """获取所有采购申请草案及审批状态"""
    return get_all_purchase_drafts()


@app.post("/api/procurement/drafts", tags=["采购管理"])
def create_draft():
    """创建采购申请草案（需人工审批）"""
    res = create_purchase_draft()
    return res


@app.post("/api/procurement/drafts/{draft_id}/approve", tags=["采购管理"])
def approve_draft(draft_id: str):
    """人工审批通过采购申请草案"""
    res = approve_purchase_draft(draft_id)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res


@app.post("/api/procurement/drafts/{draft_id}/reject", tags=["采购管理"])
def reject_draft(draft_id: str, req: Optional[ApprovalActionRequest] = None):
    """人工驳回采购申请草案"""
    reason = req.reason if req else ""
    res = reject_purchase_draft(draft_id, reason)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res


# ───────────────────────── 供应商 API ─────────────────────────
@app.get("/api/suppliers", response_model=List[SupplierSchema], tags=["供应商"])
def list_suppliers():
    """获取所有供应商列表及供货周期、评级"""
    return get_suppliers()


@app.get("/api/suppliers/by-material/{material_id}", response_model=List[SupplierSchema], tags=["供应商"])
def list_suppliers_by_material(material_id: str):
    """根据物料查询匹配的供应商"""
    return get_supplier_for_material(material_id)


# ───────────────────────── 系统健康检查 ─────────────────────────
@app.get("/health", tags=["系统"])
def health():
    return {"status": "ok", "service": "AI Manufacturing ERP Tools API"}
