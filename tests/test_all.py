"""
Comprehensive Unit & Integration Tests for AI Manufacturing Copilot Demo
验证所有确定性 ERP 计算工具、Agent 意图识别、采购审批与双向同步
"""
import sys
import os

# 将项目根目录加入 sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from data.store import get_store
from erp.bom_service import get_bom, expand_bom, get_bom_summary, get_all_products
from erp.inventory_service import get_all_inventory, get_inventory_by_material, update_inventory, get_low_stock_items
from erp.procurement_service import (
    calculate_material_requirements, calculate_material_gaps,
    generate_procurement_suggestions, create_purchase_draft,
    approve_purchase_draft, reject_purchase_draft,
    get_production_plan, update_production_plan, get_suppliers
)
from agent.tools import execute_tool
from agent.copilot import CopilotAgent


def test_bom_service():
    print("Testing BOM Service...")
    products = get_all_products()
    assert len(products) >= 3, "Should have at least 3 products"

    bom_p1 = get_bom("P001")
    assert len(bom_p1) == 10, f"P001 should have 10 BOM items, got {len(bom_p1)}"

    summary = get_bom_summary("P001")
    assert summary["total_material_cost"] > 0, "BOM cost should be positive"

    expanded = expand_bom("P001", 100)
    assert expanded[0]["total_quantity"] == expanded[0]["quantity_per"] * 100
    print("  ✅ BOM Service passed")


def test_inventory_service():
    print("Testing Inventory Service...")
    inv = get_all_inventory()
    assert len(inv) == 22, f"Should have 22 materials, got {len(inv)}"

    item = get_inventory_by_material("M001")
    assert item is not None and item["material_id"] == "M001"

    old_qty = item["quantity"]
    res = update_inventory("M001", old_qty + 50)
    assert res["success"] is True
    assert get_inventory_by_material("M001")["quantity"] == old_qty + 50

    # restore
    update_inventory("M001", old_qty)
    print("  ✅ Inventory Service passed")


def test_procurement_service():
    print("Testing Procurement & Gap Calculation...")
    store = get_store()
    store.reset_to_defaults()

    reqs = calculate_material_requirements()
    assert len(reqs) > 0, "Requirements should not be empty"

    gaps = calculate_material_gaps()
    assert len(gaps) > 0, "Gaps should not be empty"
    gap_items = [g for g in gaps if g["gap"] > 0]
    assert len(gap_items) > 0, "Should have gap items under initial plan"

    suggestions = generate_procurement_suggestions()
    assert len(suggestions) > 0, "Suggestions should not be empty"
    for s in suggestions:
        assert s["suggested_quantity"] >= s["gap_quantity"], "Suggested qty should cover gap"
        assert s["total_cost"] > 0, "Total cost should be positive"

    # Test purchase draft creation and human approval
    draft_res = create_purchase_draft()
    assert draft_res["success"] is True
    draft = draft_res["draft"]
    draft_id = draft["id"]
    assert draft["status"] == "待审批", "New draft must be 待审批"

    # Approve
    app_res = approve_purchase_draft(draft_id)
    assert app_res["success"] is True
    approved_draft = [d for d in store.purchase_drafts if d["id"] == draft_id][0]
    assert approved_draft["status"] == "已批准"
    print("  ✅ Procurement Service & Human Approval passed")


def test_agent_tools_execution():
    print("Testing Agent Tool Registry Execution...")
    res = execute_tool("get_product_list", {})
    assert isinstance(res, list) and len(res) >= 3

    res = execute_tool("get_bom", {"product_id": "P001"})
    assert "items" in res

    res = execute_tool("calculate_material_gaps", {})
    assert isinstance(res, list)
    print("  ✅ Agent Tools Registry passed")


def test_agent_simulated_chat():
    print("Testing Copilot Agent Natural Language Interaction...")
    store = get_store()
    store.reset_to_defaults()
    agent = CopilotAgent()

    # 1. BOM Query
    reply = agent.chat("查看智能手表的BOM物料清单", [])
    assert "智能手表" in reply and "BOM" in reply and "AMOLED" in reply
    print("    - BOM query chat: OK")

    # 2. Inventory Query
    reply = agent.chat("查询M001库存详情", [])
    assert "M001" in reply and "当前库存" in reply
    print("    - Single item inventory query chat: OK")

    # 3. Gap Analysis
    reply = agent.chat("分析当前生产计划的物料缺口", [])
    assert "缺口" in reply
    print("    - Gap analysis chat: OK")

    # 4. Procurement Suggestions
    reply = agent.chat("请生成采购建议", [])
    assert "建议采购" in reply or "采购建议" in reply
    print("    - Procurement suggestion chat: OK")

    # 5. Inventory Update via Natural Language
    reply = agent.chat("把M001库存改为999", [])
    assert "✅" in reply and "999" in reply
    assert store.inventory["M001"]["quantity"] == 999, "Data store inventory should be updated"
    print("    - Inventory update via natural language: OK")

    # 6. Production Plan Adjustment via Natural Language
    reply = agent.chat("将智能手表计划产量调整为800", [])
    assert "✅" in reply
    assert store.production_plan["P001"]["quantity"] == 800, "Production plan should be 800"
    print("    - Production plan adjust chat: OK")

    # 7. Create Purchase Draft
    reply = agent.chat("创建采购申请单", [])
    assert "采购申请草案已创建" in reply or "待审批" in reply
    print("    - Purchase draft creation chat: OK")

    # 8. Human Approval via Natural Language
    pending_drafts = [d for d in store.purchase_drafts if d["status"] == "待审批"]
    if pending_drafts:
        draft_id = pending_drafts[-1]["id"]
        reply = agent.chat(f"批准 {draft_id}", [])
        assert "已批准" in reply
        assert pending_drafts[-1]["status"] == "已批准"
        print("    - Human approval chat: OK")

    print("  ✅ All Copilot Agent chat interactions passed!")


if __name__ == "__main__":
    test_bom_service()
    test_inventory_service()
    test_procurement_service()
    test_agent_tools_execution()
    test_agent_simulated_chat()
    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY! 🚀")
