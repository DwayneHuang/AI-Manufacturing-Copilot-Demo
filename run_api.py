"""
FastAPI Server Launcher
启动独立 FastAPI ERP 服务 (支持 OpenAPI / Swagger 文档: http://127.0.0.1:8000/docs)
"""
import sys
import uvicorn

if __name__ == "__main__":
    print("🚀 正在启动 AI Manufacturing ERP Tools FastAPI 服务...")
    print("📖 Swagger UI 接口文档地址: http://127.0.0.1:8000/docs")
    print("🔍 ReDoc 接口文档地址:   http://127.0.0.1:8000/redoc")
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
