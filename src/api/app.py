"""
FastAPI 应用入口
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from .routes.hexagram import router as hexagram_router
from .routes.analysis import router as analysis_router
from .routes.history import router as history_router
from .routes.extended import router as extended_router
from .routes.chat import router as chat_router
from .routes.tieban import router as tieban_router

app = FastAPI(
    title="皇极经世推演系统",
    description="基于邵雍《皇极经世书》的世界发展规律推演算法平台",
    version="0.2.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(hexagram_router, prefix="/api/hexagram", tags=["卦象推演"])
app.include_router(analysis_router, prefix="/api/analysis", tags=["周期分析"])
app.include_router(history_router, prefix="/api/history", tags=["历史验证"])
app.include_router(extended_router, prefix="/api/ext", tags=["卦辞·唱和·AI解读"])
app.include_router(chat_router, prefix="/api/chat", tags=["AI对话"])
app.include_router(tieban_router, prefix="/api/tieban", tags=["铁板神数"])

# 前端页面目录
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"


@app.get("/", response_class=HTMLResponse)
def index():
    """首页 - 大众版（白话解读）"""
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return index_file.read_text(encoding="utf-8")
    return HTMLResponse("<h1>皇极经世推演系统</h1><p>前端文件未找到，请访问 <a href='/docs'>/docs</a> 查看 API 文档</p>")


@app.get("/pro", response_class=HTMLResponse)
def pro():
    """专业版（完整数据展示）"""
    pro_file = FRONTEND_DIR / "pro.html"
    if pro_file.exists():
        return pro_file.read_text(encoding="utf-8")
    return HTMLResponse("<h1>专业版未找到</h1>")


@app.get("/tieban", response_class=HTMLResponse)
def tieban_page():
    """铁板神数批命"""
    tieban_file = FRONTEND_DIR / "tieban.html"
    if tieban_file.exists():
        return tieban_file.read_text(encoding="utf-8")
    return HTMLResponse("<h1>铁板批命页面未找到</h1>")


@app.get("/api")
def api_root():
    """API 信息"""
    return {
        "name": "皇极经世推演系统",
        "version": "0.2.0",
        "description": "元会运世·九层卦象·分形同构",
        "endpoints": {
            "hexagram": "/api/hexagram — 卦象推演",
            "analysis": "/api/analysis — 周期分析与趋势推演",
            "history": "/api/history — 历史验证与模式匹配",
            "extended": "/api/ext — 卦辞解读·声音唱和·AI辅助",
            "docs": "/docs — API文档",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8060)
