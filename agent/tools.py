"""
Agent Tools — 供 LLM Function Calling 使用的工具注册表
每个工具包含：函数定义、JSON Schema 声明、执行入口
"""
from __future__ import annotations
from erp.bom_service import get_bom, expand_bom, get_bom_summary, get_all_products
from erp.inventory_service import (
    get_all_inventory, get_inventory_by_material, update_inventory, get_low_stock_items,
)
from erp.procurement_service import (
    calculate_material_requirements, calculate_material_gaps,
    generate_procurement_suggestions, create_purchase_draft,
    approve_purchase_draft, reject_purchase_draft,
    get_production_plan, update_production_plan,
    get_suppliers, get_supplier_for_material,
)


# ─────────────────── 工具函数映射 ───────────────────
TOOL_FUNCTIONS = {
    "get_product_list": lambda **kw: get_all_products(),
    "get_bom": lambda product_id, **kw: get_bom_summary(product_id),
    "expand_bom": lambda product_id, quantity, **kw: expand_bom(product_id, int(quantity)),
    "get_inventory": lambda **kw: get_all_inventory(),
    "get_inventory_by_material": lambda material_id, **kw: get_inventory_by_material(material_id),
    "update_inventory": lambda material_id, new_quantity, **kw: update_inventory(material_id, int(new_quantity)),
    "get_low_stock_items": lambda **kw: get_low_stock_items(),
    "calculate_material_requirements": lambda **kw: calculate_material_requirements(),
    "calculate_material_gaps": lambda **kw: calculate_material_gaps(),
    "generate_procurement_suggestions": lambda **kw: generate_procurement_suggestions(),
    "create_purchase_draft": lambda **kw: create_purchase_draft(),
    "approve_purchase_draft": lambda draft_id, **kw: approve_purchase_draft(draft_id),
    "reject_purchase_draft": lambda draft_id, reason="", **kw: reject_purchase_draft(draft_id, reason),
    "get_production_plan": lambda **kw: get_production_plan(),
    "update_production_plan": lambda product_id, quantity, **kw: update_production_plan(product_id, int(quantity)),
    "get_suppliers": lambda **kw: get_suppliers(),
    "get_supplier_for_material": lambda material_id, **kw: get_supplier_for_material(material_id),
}


def execute_tool(tool_name: str, arguments: dict) -> dict | list | str:
    """执行工具并返回结果"""
    func = TOOL_FUNCTIONS.get(tool_name)
    if not func:
        return {"error": f"未知工具: {tool_name}"}
    try:
        return func(**arguments)
    except Exception as e:
        return {"error": f"执行 {tool_name} 出错: {str(e)}"}


# ─────────────────── Gemini Function Declarations ───────────────────
GEMINI_TOOL_DECLARATIONS = [
    {
        "name": "get_product_list",
        "description": "获取所有产品列表，包含产品ID、名称、类别、单价",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "get_bom",
        "description": "获取指定产品的 BOM 物料清单，包含物料名称、用量、单价等",
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": "产品ID，如 P001, P002, P003",
                },
            },
            "required": ["product_id"],
        },
    },
    {
        "name": "expand_bom",
        "description": "按生产数量展开 BOM，计算每种物料的总需求量和总成本",
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": "产品ID",
                },
                "quantity": {
                    "type": "integer",
                    "description": "生产数量",
                },
            },
            "required": ["product_id", "quantity"],
        },
    },
    {
        "name": "get_inventory",
        "description": "获取所有物料的当前库存信息，包含库存量、安全库存、仓库位置、状态",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "get_inventory_by_material",
        "description": "查询指定物料的库存详情",
        "parameters": {
            "type": "object",
            "properties": {
                "material_id": {
                    "type": "string",
                    "description": "物料ID，如 M001",
                },
            },
            "required": ["material_id"],
        },
    },
    {
        "name": "update_inventory",
        "description": "更新指定物料的库存数量",
        "parameters": {
            "type": "object",
            "properties": {
                "material_id": {
                    "type": "string",
                    "description": "物料ID",
                },
                "new_quantity": {
                    "type": "integer",
                    "description": "新的库存数量",
                },
            },
            "required": ["material_id", "new_quantity"],
        },
    },
    {
        "name": "get_low_stock_items",
        "description": "获取所有低于安全库存的物料预警列表",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "calculate_material_requirements",
        "description": "根据当前生产计划，汇总计算所有物料的总需求量",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "calculate_material_gaps",
        "description": "分析物料缺口：比较生产需求与当前库存，找出不足的物料及缺口数量",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "generate_procurement_suggestions",
        "description": "根据物料缺口，生成采购建议，包含供应商、建议采购量、预估成本",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "create_purchase_draft",
        "description": "创建采购申请草案，需要人工审批确认后才能正式下单",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "approve_purchase_draft",
        "description": "审批通过某个采购申请",
        "parameters": {
            "type": "object",
            "properties": {
                "draft_id": {
                    "type": "string",
                    "description": "采购申请编号，如 PO-20261117-001",
                },
            },
            "required": ["draft_id"],
        },
    },
    {
        "name": "reject_purchase_draft",
        "description": "驳回某个采购申请",
        "parameters": {
            "type": "object",
            "properties": {
                "draft_id": {
                    "type": "string",
                    "description": "采购申请编号",
                },
                "reason": {
                    "type": "string",
                    "description": "驳回原因",
                },
            },
            "required": ["draft_id"],
        },
    },
    {
        "name": "get_production_plan",
        "description": "获取当前所有产品的生产计划，包含产量、交期、优先级",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "update_production_plan",
        "description": "修改某产品的生产计划数量",
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": "产品ID",
                },
                "quantity": {
                    "type": "integer",
                    "description": "新的计划生产数量",
                },
            },
            "required": ["product_id", "quantity"],
        },
    },
    {
        "name": "get_suppliers",
        "description": "获取所有供应商列表及其详细信息",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "get_supplier_for_material",
        "description": "查询某物料对应的供应商信息",
        "parameters": {
            "type": "object",
            "properties": {
                "material_id": {
                    "type": "string",
                    "description": "物料ID",
                },
            },
            "required": ["material_id"],
        },
    },
]
