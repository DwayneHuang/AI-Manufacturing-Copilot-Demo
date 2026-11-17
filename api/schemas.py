"""
Pydantic Schemas for FastAPI ERP Endpoints
定义数据传输与验证模型
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ── 产品相关 ──
class ProductSchema(BaseModel):
    id: str = Field(..., description="产品ID")
    name: str = Field(..., description="产品名称")
    category: str = Field(..., description="产品类别")
    unit_price: float = Field(..., description="销售单价(元)")
    description: str = Field("", description="产品描述")


# ── BOM 相关 ──
class BOMItemSchema(BaseModel):
    material_id: str
    material_name: str
    category: str
    quantity_per: int
    unit: str
    unit_cost: float
    subtotal: float
    total_quantity: Optional[int] = None
    total_cost: Optional[float] = None


class BOMSummarySchema(BaseModel):
    product_id: str
    product_name: str
    bom_item_count: int
    total_material_cost: float
    items: List[BOMItemSchema]


class BOMExpandRequest(BaseModel):
    quantity: int = Field(..., gt=0, description="生产数量")


# ── 库存相关 ──
class InventoryItemSchema(BaseModel):
    material_id: str
    material_name: str
    category: str
    quantity: int
    unit: str
    safety_stock: int
    warehouse: str
    status: str


class InventoryUpdateRequest(BaseModel):
    new_quantity: int = Field(..., ge=0, description="新库存数量")


# ── 生产计划 ──
class ProductionPlanItemSchema(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    deadline: str
    priority: str
    status: str


class ProductionPlanUpdateRequest(BaseModel):
    quantity: int = Field(..., ge=0, description="新生产计划数量")


# ── 需求与缺口 ──
class RequirementItemSchema(BaseModel):
    material_id: str
    material_name: str
    category: str
    unit: str
    unit_cost: float
    total_required: int
    sources: List[Dict[str, Any]]


class GapItemSchema(BaseModel):
    material_id: str
    material_name: str
    category: str
    unit: str
    unit_cost: float
    total_required: int
    current_stock: int
    safety_stock: int
    gap: int
    gap_without_safety: int
    available_for_production: int
    status: str


# ── 采购建议与草案 ──
class ProcurementSuggestionSchema(BaseModel):
    material_id: str
    material_name: str
    unit: str
    gap_quantity: int
    suggested_quantity: int
    unit_cost: float
    total_cost: float
    supplier_id: str
    supplier_name: str
    lead_time_days: int
    status: str
    priority: str


class PurchaseDraftSchema(BaseModel):
    id: str
    created_at: str
    items: List[ProcurementSuggestionSchema]
    item_count: int
    total_amount: float
    status: str
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    remarks: Optional[str] = ""


class ApprovalActionRequest(BaseModel):
    reason: Optional[str] = Field("", description="审批意见或驳回原因")


# ── 供应商 ──
class SupplierSchema(BaseModel):
    id: str
    name: str
    contact: str
    phone: str
    email: str
    materials: List[str]
    lead_time_days: int
    min_order_qty: int
    rating: str
    payment_terms: str
