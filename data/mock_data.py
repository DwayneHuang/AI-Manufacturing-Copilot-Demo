"""
Mock ERP Data for AI Manufacturing Copilot Demo
模拟企业 ERP 系统的产品、BOM、库存、供应商等业务数据
"""

# ───────────────────────── 产品主数据 ─────────────────────────
PRODUCTS = {
    "P001": {
        "id": "P001",
        "name": "智能手表 X1 Pro",
        "category": "可穿戴设备",
        "unit_price": 1299.00,
        "description": "高端智能手表，支持健康监测、NFC支付、GPS定位",
    },
    "P002": {
        "id": "P002",
        "name": "智能手环 B2",
        "category": "可穿戴设备",
        "unit_price": 399.00,
        "description": "轻量化智能手环，主打运动健康监测",
    },
    "P003": {
        "id": "P003",
        "name": "无线降噪耳机 E1",
        "category": "音频设备",
        "unit_price": 599.00,
        "description": "主动降噪 TWS 耳机，Hi-Fi 音质",
    },
}

# ───────────────────────── 物料主数据 ─────────────────────────
MATERIALS = {
    "M001": {"id": "M001", "name": "AMOLED显示屏 1.43寸", "category": "显示器件", "unit": "块", "unit_cost": 85.00},
    "M002": {"id": "M002", "name": "主控芯片 RTK8773C", "category": "芯片/IC", "unit": "片", "unit_cost": 42.00},
    "M003": {"id": "M003", "name": "锂聚合物电池 410mAh", "category": "电池", "unit": "块", "unit_cost": 18.50},
    "M004": {"id": "M004", "name": "蓝牙5.3模块", "category": "通信模组", "unit": "个", "unit_cost": 12.00},
    "M005": {"id": "M005", "name": "心率/血氧传感器", "category": "传感器", "unit": "个", "unit_cost": 15.00},
    "M006": {"id": "M006", "name": "六轴加速度计/陀螺仪", "category": "传感器", "unit": "个", "unit_cost": 8.50},
    "M007": {"id": "M007", "name": "表壳(不锈钢316L)", "category": "结构件", "unit": "个", "unit_cost": 35.00},
    "M008": {"id": "M008", "name": "硅胶表带(22mm)", "category": "配件", "unit": "条", "unit_cost": 6.00},
    "M009": {"id": "M009", "name": "防水密封圈", "category": "配件", "unit": "个", "unit_cost": 0.80},
    "M010": {"id": "M010", "name": "无线充电模块", "category": "电子模组", "unit": "个", "unit_cost": 9.50},
    "M011": {"id": "M011", "name": "OLED显示屏 0.96寸", "category": "显示器件", "unit": "块", "unit_cost": 32.00},
    "M012": {"id": "M012", "name": "锂聚合物电池 180mAh", "category": "电池", "unit": "块", "unit_cost": 9.00},
    "M013": {"id": "M013", "name": "TPU弹性表带", "category": "配件", "unit": "条", "unit_cost": 3.50},
    "M014": {"id": "M014", "name": "外壳(PC塑料)", "category": "结构件", "unit": "个", "unit_cost": 5.00},
    "M015": {"id": "M015", "name": "磁吸充电触点", "category": "电子模组", "unit": "个", "unit_cost": 2.50},
    "M016": {"id": "M016", "name": "动圈喇叭单元 6mm", "category": "音频器件", "unit": "个", "unit_cost": 7.50},
    "M017": {"id": "M017", "name": "微型锂电池 55mAh", "category": "电池", "unit": "块", "unit_cost": 5.00},
    "M018": {"id": "M018", "name": "充电仓电池 500mAh", "category": "电池", "unit": "块", "unit_cost": 12.00},
    "M019": {"id": "M019", "name": "主动降噪芯片 BES2600", "category": "芯片/IC", "unit": "片", "unit_cost": 28.00},
    "M020": {"id": "M020", "name": "硅胶耳套(S/M/L套装)", "category": "配件", "unit": "套", "unit_cost": 1.50},
    "M021": {"id": "M021", "name": "充电仓外壳(PC+ABS)", "category": "结构件", "unit": "个", "unit_cost": 8.00},
    "M022": {"id": "M022", "name": "Type-C充电接口模块", "category": "电子模组", "unit": "个", "unit_cost": 3.00},
}

# ───────────────────────── BOM 结构 ─────────────────────────
# key = 产品ID, value = 物料清单(material_id, 单位用量)
BOM = {
    "P001": [
        {"material_id": "M001", "quantity_per": 1, "unit": "块"},
        {"material_id": "M002", "quantity_per": 1, "unit": "片"},
        {"material_id": "M003", "quantity_per": 1, "unit": "块"},
        {"material_id": "M004", "quantity_per": 1, "unit": "个"},
        {"material_id": "M005", "quantity_per": 1, "unit": "个"},
        {"material_id": "M006", "quantity_per": 1, "unit": "个"},
        {"material_id": "M007", "quantity_per": 1, "unit": "个"},
        {"material_id": "M008", "quantity_per": 1, "unit": "条"},
        {"material_id": "M009", "quantity_per": 2, "unit": "个"},
        {"material_id": "M010", "quantity_per": 1, "unit": "个"},
    ],
    "P002": [
        {"material_id": "M011", "quantity_per": 1, "unit": "块"},
        {"material_id": "M002", "quantity_per": 1, "unit": "片"},
        {"material_id": "M012", "quantity_per": 1, "unit": "块"},
        {"material_id": "M004", "quantity_per": 1, "unit": "个"},
        {"material_id": "M005", "quantity_per": 1, "unit": "个"},
        {"material_id": "M013", "quantity_per": 1, "unit": "条"},
        {"material_id": "M014", "quantity_per": 1, "unit": "个"},
        {"material_id": "M015", "quantity_per": 1, "unit": "个"},
    ],
    "P003": [
        {"material_id": "M016", "quantity_per": 2, "unit": "个"},
        {"material_id": "M004", "quantity_per": 1, "unit": "个"},
        {"material_id": "M017", "quantity_per": 2, "unit": "块"},
        {"material_id": "M018", "quantity_per": 1, "unit": "块"},
        {"material_id": "M019", "quantity_per": 1, "unit": "片"},
        {"material_id": "M020", "quantity_per": 3, "unit": "套"},
        {"material_id": "M021", "quantity_per": 1, "unit": "个"},
        {"material_id": "M022", "quantity_per": 1, "unit": "个"},
    ],
}

# ───────────────────────── 库存数据 ─────────────────────────
INVENTORY = {
    "M001": {"quantity": 300,  "safety_stock": 100, "warehouse": "W01-A区"},
    "M002": {"quantity": 200,  "safety_stock": 200, "warehouse": "W01-B区"},
    "M003": {"quantity": 600,  "safety_stock": 100, "warehouse": "W02-A区"},
    "M004": {"quantity": 500,  "safety_stock": 300, "warehouse": "W01-B区"},
    "M005": {"quantity": 800,  "safety_stock": 200, "warehouse": "W01-C区"},
    "M006": {"quantity": 450,  "safety_stock": 100, "warehouse": "W01-C区"},
    "M007": {"quantity": 150,  "safety_stock": 100, "warehouse": "W03-A区"},
    "M008": {"quantity": 700,  "safety_stock": 100, "warehouse": "W03-B区"},
    "M009": {"quantity": 2000, "safety_stock": 200, "warehouse": "W03-B区"},
    "M010": {"quantity": 400,  "safety_stock": 100, "warehouse": "W01-D区"},
    "M011": {"quantity": 1200, "safety_stock": 200, "warehouse": "W01-A区"},
    "M012": {"quantity": 1500, "safety_stock": 200, "warehouse": "W02-A区"},
    "M013": {"quantity": 1100, "safety_stock": 200, "warehouse": "W03-B区"},
    "M014": {"quantity": 900,  "safety_stock": 200, "warehouse": "W03-A区"},
    "M015": {"quantity": 1000, "safety_stock": 200, "warehouse": "W01-D区"},
    "M016": {"quantity": 600,  "safety_stock": 200, "warehouse": "W01-E区"},
    "M017": {"quantity": 500,  "safety_stock": 200, "warehouse": "W02-A区"},
    "M018": {"quantity": 400,  "safety_stock": 100, "warehouse": "W02-A区"},
    "M019": {"quantity": 300,  "safety_stock": 100, "warehouse": "W01-B区"},
    "M020": {"quantity": 3000, "safety_stock": 500, "warehouse": "W03-C区"},
    "M021": {"quantity": 500,  "safety_stock": 100, "warehouse": "W03-A区"},
    "M022": {"quantity": 900,  "safety_stock": 100, "warehouse": "W01-D区"},
}

# ───────────────────────── 供应商数据 ─────────────────────────
SUPPLIERS = {
    "S001": {
        "id": "S001",
        "name": "京东方科技集团",
        "contact": "李明",
        "phone": "138-0001-1234",
        "email": "liming@boe.com",
        "materials": ["M001", "M011"],
        "lead_time_days": 14,
        "min_order_qty": 100,
        "rating": "A",
        "payment_terms": "月结30天",
    },
    "S002": {
        "id": "S002",
        "name": "瑞昱半导体(上海)",
        "contact": "王芳",
        "phone": "139-0002-5678",
        "email": "wangfang@realtek.com",
        "materials": ["M002", "M019"],
        "lead_time_days": 21,
        "min_order_qty": 500,
        "rating": "A",
        "payment_terms": "月结45天",
    },
    "S003": {
        "id": "S003",
        "name": "欣旺达电子股份",
        "contact": "张伟",
        "phone": "136-0003-9012",
        "email": "zhangwei@sunwoda.com",
        "materials": ["M003", "M012", "M017", "M018"],
        "lead_time_days": 10,
        "min_order_qty": 200,
        "rating": "B+",
        "payment_terms": "月结30天",
    },
    "S004": {
        "id": "S004",
        "name": "中科蓝讯科技",
        "contact": "赵丽",
        "phone": "135-0004-3456",
        "email": "zhaoli@bluetrum.com",
        "materials": ["M004"],
        "lead_time_days": 7,
        "min_order_qty": 100,
        "rating": "A",
        "payment_terms": "款到发货",
    },
    "S005": {
        "id": "S005",
        "name": "汇顶科技股份",
        "contact": "刘洋",
        "phone": "137-0005-7890",
        "email": "liuyang@goodix.com",
        "materials": ["M005", "M006"],
        "lead_time_days": 12,
        "min_order_qty": 200,
        "rating": "A+",
        "payment_terms": "月结30天",
    },
    "S006": {
        "id": "S006",
        "name": "深圳通达精密配件",
        "contact": "陈强",
        "phone": "134-0006-2345",
        "email": "chenqiang@tdpj.com",
        "materials": ["M007", "M008", "M009", "M010", "M013", "M014", "M015", "M020", "M021", "M022"],
        "lead_time_days": 5,
        "min_order_qty": 50,
        "rating": "B",
        "payment_terms": "款到发货",
    },
    "S007": {
        "id": "S007",
        "name": "歌尔股份有限公司",
        "contact": "孙梅",
        "phone": "133-0007-6789",
        "email": "sunmei@goertek.com",
        "materials": ["M016"],
        "lead_time_days": 15,
        "min_order_qty": 300,
        "rating": "A",
        "payment_terms": "月结45天",
    },
}

# ───────────────────────── 默认生产计划 ─────────────────────────
PRODUCTION_PLAN = {
    "P001": {"quantity": 500, "deadline": "2026-12-15", "priority": "高", "status": "计划中"},
    "P002": {"quantity": 1000, "deadline": "2026-12-20", "priority": "中", "status": "计划中"},
    "P003": {"quantity": 800, "deadline": "2026-12-25", "priority": "中", "status": "计划中"},
}

# ───────────────────────── 物料-供应商 映射(反向索引) ─────────────────────────
def build_material_supplier_map(suppliers: dict) -> dict:
    """构建物料 -> 供应商列表 的反向索引"""
    m2s = {}
    for sid, info in suppliers.items():
        for mid in info["materials"]:
            m2s.setdefault(mid, []).append(sid)
    return m2s

MATERIAL_SUPPLIER_MAP = build_material_supplier_map(SUPPLIERS)
