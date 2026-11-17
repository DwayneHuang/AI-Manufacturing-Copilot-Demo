"""
Unified Data Store
统一数据仓库与双向同步管理
支持 Streamlit session_state 与 Standalone FastAPI 独立运行两种模式
"""
import copy
from data.mock_data import PRODUCTS, MATERIALS, BOM, INVENTORY, SUPPLIERS, PRODUCTION_PLAN


class ERPDataStore:
    """ERP 数据管理器，支持内存存储及与 Streamlit session_state 双向绑定"""

    _instance = None

    def __init__(self):
        self._products = copy.deepcopy(PRODUCTS)
        self._materials = copy.deepcopy(MATERIALS)
        self._bom = copy.deepcopy(BOM)
        self._inventory = copy.deepcopy(INVENTORY)
        self._suppliers = copy.deepcopy(SUPPLIERS)
        self._production_plan = copy.deepcopy(PRODUCTION_PLAN)
        self._purchase_drafts = []

    @classmethod
    def get_instance(cls) -> "ERPDataStore":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _has_streamlit(self) -> bool:
        try:
            import streamlit as st
            # Check if streamlit runtime is active
            return hasattr(st, "session_state") and "products" in st.session_state
        except Exception:
            return False

    @property
    def products(self) -> dict:
        if self._has_streamlit():
            import streamlit as st
            return st.session_state.products
        return self._products

    @property
    def materials(self) -> dict:
        if self._has_streamlit():
            import streamlit as st
            return st.session_state.materials
        return self._materials

    @property
    def bom(self) -> dict:
        if self._has_streamlit():
            import streamlit as st
            return st.session_state.bom
        return self._bom

    @property
    def inventory(self) -> dict:
        if self._has_streamlit():
            import streamlit as st
            return st.session_state.inventory
        return self._inventory

    @property
    def suppliers(self) -> dict:
        if self._has_streamlit():
            import streamlit as st
            return st.session_state.suppliers
        return self._suppliers

    @property
    def production_plan(self) -> dict:
        if self._has_streamlit():
            import streamlit as st
            return st.session_state.production_plan
        return self._production_plan

    @property
    def purchase_drafts(self) -> list:
        if self._has_streamlit():
            import streamlit as st
            return st.session_state.purchase_drafts
        return self._purchase_drafts

    def reset_to_defaults(self):
        """重置数据为默认 Mock 数据"""
        self._products = copy.deepcopy(PRODUCTS)
        self._materials = copy.deepcopy(MATERIALS)
        self._bom = copy.deepcopy(BOM)
        self._inventory = copy.deepcopy(INVENTORY)
        self._suppliers = copy.deepcopy(SUPPLIERS)
        self._production_plan = copy.deepcopy(PRODUCTION_PLAN)
        self._purchase_drafts = []
        if self._has_streamlit():
            import streamlit as st
            st.session_state.products = copy.deepcopy(PRODUCTS)
            st.session_state.materials = copy.deepcopy(MATERIALS)
            st.session_state.bom = copy.deepcopy(BOM)
            st.session_state.inventory = copy.deepcopy(INVENTORY)
            st.session_state.suppliers = copy.deepcopy(SUPPLIERS)
            st.session_state.production_plan = copy.deepcopy(PRODUCTION_PLAN)
            st.session_state.purchase_drafts = []


def get_store() -> ERPDataStore:
    """获取单例数据仓库"""
    return ERPDataStore.get_instance()
